from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.utils import classImplements
from plone.session.plugins.session import SessionPlugin
from Products.PluggableAuthService.interfaces.plugins \
                import IAuthenticationPlugin, ICredentialsResetPlugin
from plone.openid.interfaces import IOpenIdExtractionPlugin
from plone.openid.store import ZopeStore
from zExceptions import Redirect
import transaction
from urljr.fetchers import HTTPFetchingError
from openid import cryptutil
from openid.consumer.consumer import Consumer, SUCCESS
import binascii, logging

manage_addOpenIdPlugin = PageTemplateFile("../www/openidAdd", globals(), 
                __name__="manage_addOpenIdPlugin")

logger = logging.getLogger("PluggableAuthService")

def addOpenIdPlugin(self, id, title='', path='/', REQUEST=None):
    """Add a OpenID plugin to a Pluggable Authentication Service.
    """
    p=OpenIdPlugin(id, title, path)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=OpenID+plugin+added." %
                self.absolute_url())


class OpenIdPlugin(SessionPlugin):
    """OpenID authentication plugin.
    """

    meta_type = "OpenID plugin"
    security = ClassSecurityInfo()

    def __init__(self, id, title=None, path="/"):
        SessionPlugin.__init__(self, id, title=title, path=path)
        self.store=ZopeStore()


    def getTrustRoot(self):
        pas=self._getPAS()
        site=pas.aq_parent
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
            for field in [ "identity", "assoc_handle", "return_to",
                    "signed", "sig", "invalidate_handle", "mode" ]:
                field="openid."+field
                if request.form.has_key(field):
                    creds[field]=request.form[field]
        elif mode=="cancel":
            # cancel is as a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            pass


    # IOpenIdExtractionPlugin implementation
    def initiateChallenge(self, identity_url, return_to=None):
        consumer=self.getConsumer()
        try:
            result=consumer.begin(identity_url)
        except HTTPFetchingError, e:
            logger.info("openid consumer error for identity %s: %s",
                    identity_url, e.why)
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
        if identity is not None:
            self.initiateChallenge(identity)
            return creds

        self.extractOpenIdServerResponse(request, creds)
        if creds:
            return creds

        return SessionPlugin.extractCredentials(self, request)


    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        auth=SessionPlugin.authenticateCredentials(
                self, credentials)
        if auth is not None:
            return auth

        if not credentials.has_key("openid.source"):
            return None

        if credentials["openid.source"]=="server":
            consumer=self.getConsumer()
            result=consumer.complete(credentials)
            identity=credentials["openid.identity"]

            if result.status==SUCCESS:
                self.setupSession(identity)
                return (identity, identity)
            else:
                logger.info("OpenId Authentication for %s failed: %s", identity, result.message)

        return None


    # ICredentialsResetPlugin implementation
    def resetCredentials(self, request, response):
        source=self.getSource()
        source.invalidateSession()

        SessionPlugin.resetCredentials(self, request, response)


classImplements(OpenIdPlugin, IOpenIdExtractionPlugin, IAuthenticationPlugin,
                ICredentialsResetPlugin)


