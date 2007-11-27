from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from plone.openid import config

if not config.HAS_OPENID:
    import logging
    logger=logging.getLogger("Plone")
    logger.info("OpenID system packages not installed, OpenID support not available")
elif not config.HAS_SSL:
    import logging
    logger=logging.getLogger("Plone")
    logger.info("Python does not have SSL support. OpenID support not available")
    config.HAS_OPENID=False
else:
    from plugins import oid
    registerMultiPlugin(oid.OpenIdPlugin.meta_type)



def initialize(context):
    if config.HAS_OPENID:
        context.registerClass(oid.OpenIdPlugin,
                                permission=ManageUsers,
                                constructors=
                                        (oid.manage_addOpenIdPlugin,
                                        oid.addOpenIdPlugin),
                                visibility=None,
                                icon="www/openid.png")

