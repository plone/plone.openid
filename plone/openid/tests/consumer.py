
from openid.consumer.consumer import SUCCESS

class MockAuthRequest:
    """Amock OpenID AuthRequest.
    """
    def redirectURL(self, trust_root, return_to):
        return return_to


class MockConsumer:
    """A mock OpenID consumerclass.
    """

    def begin(self, identity):
        self.identity=identity
        return MockAuthRequest()

    def complete(self, credentials):
        result=MockAuthRequest(status=SUCCESS,
                                identity_url=self.identity)

def PatchPlugin(plugin):
    def getConsumer(self):
        return MockConsumer()

    plugin.getConsumer=getConsumer

