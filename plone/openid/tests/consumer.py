
from openid.consumer.consumer import FAILURE, SUCCESS

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
        status=SUCCESS
        for field in [ "openid.source", "nonce", "openid.identity",
                "openid.assoc_handle", "openid.return_to", "openid.signed",
                "openid.sig", "openid.invalidate_handle", "openid.mode"]:
            if field not in credentials:
                status=FAILURE

        if credentials["openid.identity"]!=self.identity:
            status=FAILURE

        result=MockAuthRequest(status=status,
                                identity_url=self.identity)

def PatchPlugin(plugin):
    def getConsumer(self):
        return MockConsumer()

    plugin.getConsumer=getConsumer

