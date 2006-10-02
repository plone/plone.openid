from plone.openid.util import GenerateSecret
from openid.store.interface import OpenIDStore
from openid.association import Association
from BTrees.OIBTree import OITreeSet
from BTrees.OOBTree import OOBTree
import time

class ZopeStore(OpenIDStore):
    """Zope OpenID store.

    This class implements an OpenID store which uses the ZODB.
    """
    def __init__(self):
        self.associations=OOBTree()
        self.handles=OOBTree()
        self.nonces=OITreeSet()
        self.authkey=GenerateSecret(length=self.AUTH_KEY_LEN)


    def getAssociationKey(self, server_url, handle):
        """Generate a key used to identify an association in our storage.
        """
        if handle is None:
            return self.handles[server_url][0]

        return (server_url, handle)


    def storeAssociation(self, server_url, association):
        key=self.getAssociationKey(server_url, association.handle)
        self.associations[key]=association.serialize()

        now=time.time()
        def cmpAssociations(one, two):
                return cmp(self.associations[one].getExpiresIn(now),
                           self.associations[two].getExpiresIn(now))
        lst=self.handles.get(server_url, [])
        lst.append(key)
        lst.sort(cmp=cmpAssociations)
        self.handles[server_url]=lst


    def getAssociation(self, server_url, handle=None):
        try:
            key=self.getAssociationKey(server_url, handle)
            assoc=Association.deserialize(self.associations[key])
        except KeyError:
            return None

        now=time.time()
        if assoc.getExpiresIn(now)==0:
            self.removeAssociation(server_url, handle)

        return assoc


    def removeAssociation(self, server_url, handle):
        key=self.getAssociationKey(server_url, handle)
        try:
            del self.associations[key]

            lst=self.handles[server_url]
            lst.remove(key)
            self.handles[server_url]=lst

            return True
        except KeyError:
            return False


    def storeNonce(self, nonce):
        self.nonces.insert(nonce)


    def useNonce(self, nonce):
        try:
            self.nonces.remove(nonce)
            return True
        except KeyError:
            return False


    def getAuthKey(self):
        return self.authkey


    def isDumb(self):
        return False

