from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from plone.openid.config import HAS_OPENID

if HAS_OPENID:
    from plugins import oid
    registerMultiPlugin(oid.OpenIdPlugin.meta_type)
else:
    import logging
    logger=logging.getLogger("Plone")
    logger.info("OpenID packages not installed")


def initialize(context):
    if HAS_OPENID:
        context.registerClass(oid.OpenIdPlugin,
                                permission=ManageUsers,
                                constructors=
                                        (oid.manage_addOpenIdPlugin,
                                        oid.addOpenIdPlugin),
                                visibility=None,
                                icon="www/openid.png")

