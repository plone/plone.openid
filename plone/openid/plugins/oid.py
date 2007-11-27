from Acquisition import aq_parent
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins \
                import IAuthenticationPlugin, IUserEnumerationPlugin
from plone.openid.interfaces import IOpenIdExtractionPlugin
from plone.openid.store import ZopeStore
from zExceptions import Redirect
import transaction
from openid.yadis.discover import DiscoveryFailure
from openid.consumer.consumer import Consumer, SUCCESS
import logging

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
            # describes as 'positive authentication'
            creds.clear()
            creds["openid.source"]="server"
            creds["nonce"]=request.form.get("nonce")
            for (field,value) in request.form.iteritems():
                if field.startswith("openid."):
                    creds[field]=request.form[field]
        elif mode=="cancel":
            # cancel is a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            pass


    # IOpenIdExtractionPlugin implementation
    def initiateChallenge(self, identity_url, return_to=None):
        consumer=self.getConsumer()
        try:
            result=consumer.begin(identity_url)
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
        if not return_to:
            return_to=self.getTrustRoot()

        url=result.redirectURL(self.getTrustRoot(), return_to)

        # There is evilness here: we can not use a normal RESPONSE.redirect
        # since further processing of the request will happily overwrite
        # our redirect. So instead we raise a Redirect exception, However
        # raising an exception aborts all transactions, which means are
        # session changes are not stored. So we do a commit ourselves to
        # get things working.
        # XXX this also f**ks up ZopeTestCase
        transaction.commit()
        raise Redirect, url


    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        """This method performs the PAS credential extraction.

        It takes either the zope cookie and extracts openid credentials
        from it, or a redirect from a OpenID server.
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
            result=consumer.complete(credentials)
            identity=credentials["openid.identity"]

            if result.status==SUCCESS:
                self._getPAS().updateCredentials(self.REQUEST,
                        self.REQUEST.RESPONSE, identity, "")
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
            return None

        if (id and not exact_match) or kw:
            return None

        key=id and id or login

        if not (key.startswith("http:") or key.startswith("https:")):
            return None

        return [ {
                    "id" : key,
                    "login" : key,
                    "pluginid" : self.getId(),
                } ]



classImplements(OpenIdPlugin, IOpenIdExtractionPlugin, IAuthenticationPlugin,
                IUserEnumerationPlugin)


