import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from plone.openid.plugins.oid import OpenIdPlugin
from zExceptions import Redirect

# Open ZODB connection
app = ZopeTestCase.app()

# Set up sessioning objects
ZopeTestCase.utils.setupCoreSessions(app)

# Close ZODB connection
ZopeTestCase.close(app)


class TestOpenIdExtraction(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        request = self.app.REQUEST
        sdm = self.app.session_data_manager
        request.set('SESSION', sdm.getSessionData())
        self.session = request.SESSION
	self.app._setObject("openid", OpenIdPlugin("openid"))

    def testEmptyExtraction(self):
        creds=self.app.openid.extractCredentials(self.app.REQUEST)
        self.assertEqual(creds, {})

    def testRedirect(self):
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

