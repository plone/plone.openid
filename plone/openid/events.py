from zope.interface import implements

from Products.PluggableAuthService.events import PASEvent

from plone.openid.interfaces import IOpenIDRegistrationReceivedEvent

class OpenIDRegistrationReceivedEvent(PASEvent):
    implements(IOpenIDRegistrationReceivedEvent)

    def __init__(self, principal, simple_registration):
        super(OpenIDRegistrationReceivedEvent, self).__init__(principal)
        self.simple_registration = simple_registration
