import unittest

class TestOpenIdAuthentication(unittest.TestCase):
    identity = "http://plone.myopenid.com"

    def createPlugin(self):
        from plone.openid.tests.utils import MockPAS
        from plone.openid.plugins.oid import OpenIdPlugin
        plugin=OpenIdPlugin("openid")
        pas=MockPAS()
        return plugin.__of__(pas)


    def buildServerResponse(self):
        credentials={}
        for field in [ "nonce", "openid.assoc_handle", "openid.return_to",
                        "openid.signed", "openid.sig",
                        "openid.invalidate_handle", "openid.mode"]:
            credentials[field]=field
        credentials["openid.identity"]=self.identity
        credentials["openid.source"]="server"

        # this isn't part of the server response, but is added to the
        # credentials by PAS
        credentials["extractor"] = "openid"

        return credentials


    def testEmptyAuthentication(self):
        """Test if we do not invent an identity out of thin air.
        """
        plugin=self.createPlugin()
        creds=plugin.authenticateCredentials({})
        self.assertEqual(creds, None)


    def testEmptyStringIdentityAuthentication(self):
        """Test coverage for bug #7176, where an
           "" (i.e. an empty string) identity passed to
           authenticationCredentials should return fail authentication
        """
        credentials=self.buildServerResponse()
        credentials["openid.identity"]=""
        plugin=self.createPlugin()
        creds=plugin.authenticateCredentials(credentials)
        self.assertEqual(creds, None)


    def testUnknownOpenIdSource(self):
        """Test if an incorrect source does not produce unexpected exceptions.
        """
        plugin=self.createPlugin()
        creds=plugin.authenticateCredentials({"openid.source" : "x"})
        self.assertEqual(creds, None)



    def testIncompleteServerAuthentication(self):
        """Test authentication of OpenID server responses.
        """
        credentials=self.buildServerResponse()
        del credentials["openid.sig"]
        plugin=self.createPlugin()
        creds=plugin.authenticateCredentials(credentials)
        self.assertEqual(creds, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdAuthentication))
    return suite
