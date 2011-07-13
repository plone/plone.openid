import unittest

class TestOpenIdAuthentication(unittest.TestCase):
    identity = "http://plone.myopenid.com"

    def createPlugin(self, with_simple_registration=False):
        from plone.openid.tests.utils import MockPAS
        from plone.openid.plugins.oid import OpenIdPlugin
        if with_simple_registration:
            from plone.openid.tests.consumer import PatchPlugin
            # Use a mock consumer for the OpenId plugin
            PatchPlugin(OpenIdPlugin)

        plugin=OpenIdPlugin("openid")
        pas=MockPAS()
        return plugin.__of__(pas)


    def buildServerResponse(self, with_simple_registration=False):
        openid_fields = [ "nonce", "openid.assoc_handle", "openid.return_to",
                        "openid.signed", "openid.sig",
                        "openid.invalidate_handle", "openid.mode"]

        if with_simple_registration:
            from openid.extensions.sreg import data_fields
            openid_fields.extend(data_fields)


        credentials={}
        for field in openid_fields:
            credentials[field]=field
        credentials["openid.identity"]=self.identity
        credentials["openid.source"]="server"
        if with_simple_registration:
            credentials['openid.mode'] = 'id_res'

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


    def testSimpleRegistrationResponse(self):
        """Test that Simple Registration responses are stored correctly.
        """
        from openid.extensions.sreg import data_fields
        from plone.openid.tests.utils import MockUser
        credentials = self.buildServerResponse(with_simple_registration=True)
        plugin = self.createPlugin(with_simple_registration=True)
        plugin.use_simple_registration = True
        creds = plugin.authenticateCredentials(credentials)
        del credentials['extractor']
        self.assertEqual(plugin.getPropertiesForUser(MockUser(self.identity)),
                         credentials)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdAuthentication))
    return suite
