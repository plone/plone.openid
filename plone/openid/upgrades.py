from urllib import quote_plus

from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList

from plone.openid.util import getTool, getPASPlugin


def update_bbb_attributes(context):
    plugin_name, plugin = getPASPlugin(context)

    if plugin is not None:
        for attr, attr_class in {
            # BBB for versions < 1.0b2
            'assoctimeline': PersistentList,
            'noncetimeline': PersistentList,
            # BBB for versions < 2.1
            'identity_registrations': OOBTree,
        }.items():
            if not hasattr(plugin, attr):
                setattr(plugin, attr, attr_class())

def urlencode_usernames(context):
    """This upgrade step is intended to ensure that any currently saved
    Simple Registration values are updated to use a URL-encoded OpenID
    identity URL, to avoid traversal issues when Plone encounters a /
    in the URL.
    """
    acl = getTool(context, 'acl_users')
    openid = getPASPlugin(context)
    openid_name, openid = getPASPlugin(context)
    if openid_name is None:
        return

    all_registrations = openid.store.getAllRegistrations()
    to_update = [
        identity
        for identity in all_registrations
        if identity.startswith("http:") or identity.startswith("https:")
    ]
    for identity in to_update:
        # Fix values in our store
        encoded_id = quote_plus(identity)
        all_registrations[encoded_id] = all_registrations[identity]
        del all_registrations[identity]
