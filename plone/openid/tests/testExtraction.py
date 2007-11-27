from plone.openid.tests.oitestcase import FunctionalOpenIdTestCase
from zExceptions import Redirect


class TestOpenIdExtraction(FunctionalOpenIdTestCase):

    def testEmptyExtraction(self):
        """Test if we do not invent credentials out of thin air.
        """
        creds=self.folder.pas.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds, {})

    def testEmptyStringIdentityExtraction(self):
        """Test coverage for bug #7176. In the case where "" (i.e an empty
           string) is passed in as the identity via the request, 
           we essentially want to ensure that a Redirect isn't raised, which 
           would signify that an IOpenIdExtractionPlugin challenge was initialized.
           
           This test demonstrates our openid plugin's extractCredentials eliminates
           credentials that aren't in the openid.* namespace.
        """
        self.app.REQUEST.form.update(self.server_response)
        self.app.REQUEST.form["__ac_identity_url"]=""
        creds=self.folder.pas.openid.extractCredentials(self.app.REQUEST)
        self.failIf(creds.has_key("__ac_identity_url"))
        

    def testRedirect(self):
        """Test if a redirect is generated for a login attempt.
        This test requires a working internet connection!
        """
        self.app.REQUEST.form["__ac_identity_url"]=self.identity
        self.assertRaises(Redirect,
                self.folder.pas.openid.extractCredentials,
                self.app.REQUEST)


    def testPositiveOpenIdResponse(self):
        """Test if a positive authentication is extracted.
        """
        self.app.REQUEST.form.update(self.server_response)
        creds=self.folder.pas.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds["openid.identity"], self.identity)
        self.assertEqual(creds["openid.mode"], "id_res")
        self.assertEqual(creds["openid.return_to"], "return_to")


    def testNegativeOpenIdResponse(self):
        """Check if a cancelled authentication request is correctly ignored.
        """
        self.app.REQUEST.form.update(self.server_response)
        self.app.REQUEST.form["openid.mode"]="cancel"
        creds=self.folder.pas.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds, {})


    def testFormRedirectPriorities(self):
        """Check if a new login identity has preference over openid server
        reponse.
        """
        self.app.REQUEST.form.update(self.server_response)
        self.app.REQUEST.form["__ac_identity_url"]=self.identity
        self.assertRaises(Redirect,
                self.folder.pas.openid.extractCredentials,
                self.app.REQUEST)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdExtraction))
    return suite
