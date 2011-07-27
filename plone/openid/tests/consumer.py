from openid.consumer.consumer import FAILURE, SUCCESS
from openid.message import SREG_URI


class MockNamespaceMap:
    def getNamespaceURI(self, alias):
        return SREG_URI

class MockMessage:
    """ A mock OpenID Message.
    """
    def __init__(self, message=None):
        self.msg = message
        self.namespaces = MockNamespaceMap()

    def __str__(self):
        return str(self.msg)

class MockAuthRequest:
    """A mock OpenID AuthRequest.
    """
    def __init__(self, status=None, credentials=None, message=None):
        self.status=status
        if credentials is None or 'openid.identity' not in credentials:
            self.identity_url = None
        else:
            self.identity_url = credentials['openid.identity']
        self.message = MockMessage(message)
        self._creds = credentials


    def redirectURL(self, trust_root, return_to):
        return return_to

    def extensionResponse(self, namespace_uri, require_signed):
        return self._creds


class MockConsumer:
    """A mock OpenID consumerclass.
    """

    def begin(self, identity):
        self.identity=identity
        return MockAuthRequest()

    def complete(self, credentials, current_url):
        status=SUCCESS
        message="authentication completed succesfully"

        if credentials.has_key("openid.identity") and credentials["openid.identity"] == "":
            # if the python openid is passed an identity of an empty string
            # an IndexError is raised in the depths of its XRI identification
            # see: http://www.oasis-open.org/committees/tc_home.php?wg_abbrev=xri

            # an empty string is common when the submit button of the
            # openid login is clicked prior to providing an identity url
            # we simulate openid's response here in our mock object
            message="invalid identity"
            status=FAILURE
        else:
            for field in [ "openid.source", "nonce", "openid.identity",
                    "openid.assoc_handle", "openid.return_to", "openid.signed",
                    "openid.sig", "openid.invalidate_handle", "openid.mode"]:
                if field not in credentials:
                    message="field missing"
                    status=FAILURE


        return MockAuthRequest(status=status,
                                message=message,
                                credentials=credentials)

def PatchPlugin(plugin):
    def getConsumer(self):
        return MockConsumer()

    plugin.getConsumer=getConsumer

