from zope.interface import Attribute

from Products.PluggableAuthService.interfaces.events import IPASEvent
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin

class IOpenIdExtractionPlugin(IExtractionPlugin):
    """Extract OpenID credential information from a request.
    """

    def initiateAuthentication(identity_url, return_to=None):
        """Initiate the OpenID authentication.
        """


    def extractCredentials(request):
        """ request -> { 'openid.identity' : identity,
                         'openid.assoc_handle' : assoc_handle,
                         'openid.return_to' : return_to,
                         'openid.signed' : signed,
                         'openid.sig' : sig,
                         'openid.invalidate_handle' : invalidate_handle,
                        }
        """

class IOpenIDRegistrationReceivedEvent(IPASEvent):
    """A user successfully authenticated against an OpenID server.
    """
    simple_registration = Attribute(
        "The profile information returned from a Simple Registration request.")
