from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from plugins import oid

registerMultiPlugin(oid.OpenIdPlugin.meta_type)

def initialize(context):
    context.registerClass(oid.OpenIdPlugin,
                            permission=ManageUsers,
                            constructors=
                                    (oid.manage_addOpenIdPlugin,
                                    oid.addOpenIdPlugin),
                            visibility=None,
                            icon="www/openid.png")

