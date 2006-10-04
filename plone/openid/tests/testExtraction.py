import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from plone.openid.plugins.oid import OpenIdPlugin
from plone.openid.tests.consumer import PatchPlugin
from zExceptions import Redirect

# Use a mock consumer for the OpenId plugin
PatchPlugin(OpenIdPlugin)

class TestOpenIdExtraction(ZopeTestCase.ZopeTestCase):
    server_response={
            "openid.mode"              : "id_res",
            "nonce"                    : "nonce",
            "openid.identity"          : "http://plone.myopenid.com",
            "openid.assoc_handle"      : "assoc_handle",
            "openid.return_to"         : "return_to",
            "openid.signed"            : "signed",
            "openid.sig"               : "sig",
            "openid.invalidate_handle" : "invalidate_handle",
            }

    def afterSetUp(self):
        self.app._setObject("openid", OpenIdPlugin("openid"))


    def testEmptyExtraction(self):
        creds=self.app.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds, {})


    def testRedirect(self):
        """Test if a redirect is generated for a login attempt.
        This test requires a working internet connection!
        """
        self.app.REQUEST.form["__ac_identity_url"]="http://plone.myopenid.com"
        self.assertRaises(Redirect,
                self.app.openid.extractCredentials,
                self.app.REQUEST)


    def testPositiveOpenIdResponse(self):
        """Test if a positive authentication is extracted.
        """
        self.app.REQUEST.form.update(self.server_response)
        creds=self.app.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds["openid.identity"], "http://plone.myopenid.com")
        self.assertEqual(creds["openid.mode"], "id_res")
        self.assertEqual(creds["openid.return_to"], "return_to")


    def testNegativeOpenIdResponse(self):
        """Check if a cancelled authentication request is correctly ignored.
        """
        self.app.REQUEST.form.update(self.server_response)
        self.app.REQUEST.form["openid.mode"]="cancel"
        creds=self.app.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds, {})


    def testPriorities(self):
        """Check if a new login identity has preference over an existing login.
        """

        self.app.REQUEST.form.update(self.server_response)
        self.app.REQUEST.form["__ac_identity_url"]="http://plone.myopenid.com"
        self.assertRaises(Redirect,
                self.app.openid.extractCredentials,
                self.app.REQUEST)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdExtraction))
    return suite


if __name__ == '__main__':
    framework()

