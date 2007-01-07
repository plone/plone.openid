from Testing import ZopeTestCase
from plone.session.tests.sessioncase import PloneSessionTestCase
from Testing.ZopeTestCase.placeless import setUp, tearDown
from Testing.ZopeTestCase.placeless import zcml

from plone.openid.plugins.oid import OpenIdPlugin
from plone.openid.tests.consumer import PatchPlugin
from plone.openid.tests.layer import PloneOpenId

# Use a mock consumer for the OpenId plugin
PatchPlugin(OpenIdPlugin)

class OpenIdTestCase(PloneSessionTestCase):

    layer = PloneOpenId

    identity = "http://plone.myopenid.com"
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

    _setup_fixture = False

    def afterSetUp(self):
        PloneSessionTestCase.afterSetUp(self)

        if self.app.folder.hasObject("openid"):
            self.app.folder._delObject("openid")

        self.app.folder._setObject("openid", OpenIdPlugin("openid"))

class FunctionalOpenIdTestCase(ZopeTestCase.Functional, OpenIdTestCase):
    pass
