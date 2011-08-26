from base64 import urlsafe_b64encode, urlsafe_b64decode
import random

from Acquisition import aq_get
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin

from plone.openid.interfaces import IOpenIdExtractionPlugin


def GenerateSecret(length=16):
    letters ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letters+="abcdefghijklmnopqrstuvwxyz"
    letters+="01234567890!@#$%^&*()"

    secret=""
    for i in range(length):
        secret+=random.choice(letters)

    return secret

def getTool(context, tool):
    # Small version of getToolByName
    _marker = []
    try:
        return aq_get(context, tool, _marker, 1)
    except AttributeError:
        raise

def getPASPlugin(context, plugin_type=IExtractionPlugin,
                 provides=IOpenIdExtractionPlugin):
    acl = getTool(context, 'acl_users')
    plugins = acl.plugins.listPlugins(plugin_type)

    for plugin_name, plugin in plugins:
        if provides.providedBy(plugin):
            return plugin_name, plugin

    return (None, None)

def encodeIdentityURL(identity_url):
    # NOTE: the following can still contain =, which might be
    #       problematic in some cases
    return '_'.join(['openid', urlsafe_b64encode(identity_url)])

def decodeIdentityURL(user_id):
    # WARNING: expects a binary, not unicode string
    return urlsafe_b64decode(user_id.lstrip('openid_'))
