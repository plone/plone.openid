import logging

from Acquisition import aq_parent
from AccessControl.SecurityInfo import ClassSecurityInfo
import transaction
from zExceptions import Redirect
from zope.event import notify

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import \
    (IAuthenticationPlugin, IPropertiesPlugin, IUserEnumerationPlugin)
from plone.openid.interfaces import IOpenIdExtractionPlugin
from plone.openid.events import OpenIDRegistrationReceivedEvent
from plone.openid.store import ZopeStore

from openid.yadis.discover import DiscoveryFailure
from openid.consumer.consumer import Consumer, SUCCESS
from openid.extensions.sreg import SRegRequest, data_fields

manage_addOpenIdPlugin = PageTemplateFile("../www/openidAdd", globals(),
                __name__="manage_addOpenIdPlugin")

logger = logging.getLogger("PluggableAuthService")

def addOpenIdPlugin(self, id, title='', REQUEST=None):
    """Add a OpenID plugin to a Pluggable Authentication Service.
    """
    p=OpenIdPlugin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=OpenID+plugin+added." %
                self.absolute_url())


class OpenIdPlugin(BasePlugin):
    """OpenID authentication plugin.
    """

    meta_type = "OpenID plugin"
    security = ClassSecurityInfo()

    use_simple_registration = False

    _properties = (
        dict(id='use_simple_registration', type='boolean', mode='w',
             label='Use "Simple Registration" to retrieve user profile info'),)

    def __init__(self, id, title=None):
        self._setId(id)
        self.title=title
        self.store=ZopeStore()


    def getTrustRoot(self):
        pas=self._getPAS()
        site=aq_parent(pas)
        return site.absolute_url()


    def getConsumer(self):
        session=self.REQUEST["SESSION"]
        return Consumer(session, self.store)


    def extractOpenIdServerResponse(self, request, creds):
        """Process incoming redirect from an OpenId server.

        The redirect is detected by looking for the openid.mode
        form parameters. If it is found the creds parameter is
        cleared and filled with the found credentials.
        """

        mode=request.form.get("openid.mode", None)
        if mode=="id_res":
            # id_res means 'positive assertion' in OpenID, more commonly
            # described as 'positive authentication'
            creds.clear()
            creds["openid.source"]="server"
            creds["janrain_nonce"]=request.form.get("janrain_nonce")
            for (field,value) in request.form.iteritems():
                if field.startswith("openid.") or field.startswith("openid1_"):
                    creds[field]=request.form[field]
        elif mode=="cancel":
            # cancel is a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            pass


    # IOpenIdExtractionPlugin implementation
    def initiateChallenge(self, identity_url, return_to=None):
        consumer=self.getConsumer()
        try:
            auth_request=consumer.begin(identity_url)
        except DiscoveryFailure, e:
            logger.info("openid consumer discovery error for identity %s: %s",
                    identity_url, e[0])
            return
        except KeyError, e:
            logger.info("openid consumer error for identity %s: %s",
                    identity_url, e.why)
            pass

        if return_to is None:
            return_to=self.REQUEST.form.get("came_from", None)
        if not return_to or 'janrain_nonce' in return_to:
            # The conditional on janrain_nonce here is to handle the case where
            # the user logs in, logs out, and logs in again in succession.  We
            # were ending up with duplicate open ID variables on the second response
            # from the OpenID provider, which was breaking the second login.
            return_to=self.getTrustRoot()

        # Add a request for more user info if enabled
        if self.use_simple_registration:
            auth_request.addExtension(SRegRequest(optional=data_fields.keys()))

        url=auth_request.redirectURL(self.getTrustRoot(), return_to)

        # There is evilness here: we can not use a normal RESPONSE.redirect
        # since further processing of the request will happily overwrite
        # our redirect. So instead we raise a Redirect exception, However
        # raising an exception aborts all transactions, which means our
        # session changes are not stored. So we do a commit ourselves to
        # get things working.
        # XXX this also f**ks up ZopeTestCase
        transaction.commit()
        raise Redirect, url


    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        """This method performs the PAS credential extraction.

        It takes either the zope cookie and extracts openid credentials
        from it, or a redirect from an OpenID server.
        """
        creds={}
        identity=request.form.get("__ac_identity_url", None)
        if identity is not None and identity != "":
            self.initiateChallenge(identity)
            return creds

        self.extractOpenIdServerResponse(request, creds)
        return creds


    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.has_key("openid.source"):
            return None

        if credentials["openid.source"]=="server":
            consumer=self.getConsumer()

            # remove the extractor key that PAS adds to the credentials,
            # or python-openid will complain
            query = credentials.copy()
            del query['extractor']

            result=consumer.complete(query, self.REQUEST.ACTUAL_URL)
            identity=result.identity_url

            if result.status==SUCCESS:
                pas = self._getPAS()
                if self.use_simple_registration:
                    sreg_uri = result.message.namespaces.getNamespaceURI('sreg')
                    registration = result.extensionResponse(sreg_uri, True)
                    logger.info("Storing registration info for identity %s: %s",
                                identity, registration)
                    self.store.storeSimpleRegistration(identity, registration)
                    # The following is because the redirect to the OpenID
                    # server breaks the default PythonScript success traversal
                    # behavior.
                    # NOTE: we don't emit the raw registration, as
                    #       storeSimpleRegistration converts the raw response
                    #       to a PersistentMap
                    persistent_reg = self.store.getSimpleRegistration(identity)
                    user = pas.getUserById(identity)
                    notify(OpenIDRegistrationReceivedEvent(user, persistent_reg))

                pas.updateCredentials(self.REQUEST,
                                      self.REQUEST.RESPONSE,
                                      identity, "")
                return (identity, identity)
            else:
                logger.info("OpenId Authentication for %s failed: %s",
                                identity, result.message)

        return None


    # IUserEnumerationPlugin implementation
    def enumerateUsers(self, id=None, login=None, exact_match=False,
            sort_by=None, max_results=None, **kw):
        """Slightly evil enumerator.

        This is needed to be able to get PAS to return a user which it should
        be able to handle but who can not be enumerated.

        We do this by checking for the exact kind of call the PAS getUserById
        implementation makes
        """
        if id and login and id!=login:
            return []

        if (id and not exact_match) or kw:
            return (
                {'id': identity,
                 'login': identity,
                 'pluginid': self.getId()}
                for identity in self.store.getAllRegistrations().iterkeys()
                if id.lower() in identity.lower()
            )

        if id is None and login is None:
            return (
                {'id': identity,
                 'login': identity,
                 'pluginid': self.getId()}
                for identity in self.store.getAllRegistrations().iterkeys()
            )

        key=id and id or login

        if not (key.startswith("http:") or key.startswith("https:")):
            return []

        return [ {
                    "id" : key,
                    "login" : key,
                    "pluginid" : self.getId(),
                } ]

    # IPropertiesPlugin implementation
    def getPropertiesForUser(self, user, request=None):
        user_id = user.getId()
        if not self.use_simple_registration or \
           not (user_id.startswith("http:") or user_id.startswith("https:")):
            return {}
        else:
            registration = self.store.getSimpleRegistration(user_id, {})
            return registration


classImplements(OpenIdPlugin, IOpenIdExtractionPlugin, IAuthenticationPlugin,
                IPropertiesPlugin, IUserEnumerationPlugin)
