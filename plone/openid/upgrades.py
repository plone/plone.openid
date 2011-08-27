from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList

from plone.openid.util import getPASPlugin


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
