import unittest

from Products.PluggableAuthService.tests.conformance \
    import (IAuthenticationPlugin_conformance,
            IUserEnumerationPlugin_conformance)

from plone.openid.tests.oitestcase import OpenIdTestCase

class UserSearchTest(OpenIdTestCase,
                     IAuthenticationPlugin_conformance,
                     IUserEnumerationPlugin_conformance):

    def _getTargetClass( self ):
        from plone.openid.plugins.oid import OpenIdPlugin

        return OpenIdPlugin

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def afterSetUp(self):
        OpenIdTestCase.afterSetUp(self)
        self.openid.use_simple_registration = True

        # Create new openid users
        store = self.openid.store
        store.storeSimpleRegistration('http://plone.myopenid.com/member1',
                                      {'fullname': 'Some User',
                                       'email': 'some@user.com'})
        store.storeSimpleRegistration('http://plone.myopenid.com/member2',
                                      {'fullname': 'Other User',
                                       'email': 'other@user.com'})

    def testEmptySearch(self):
        results = self.openid.enumerateUsers()
        self.assertEqual(len(results), 2)

    def testUnknownKeys(self):
        results = self.openid.enumerateUsers(address="123 Anywhere Street",
                                       exact_match=True)
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member1',
                                   'http://plone.myopenid.com/member2'])

    def testExactStringSearch(self):
        results = self.openid.enumerateUsers(email="something@somewhere.tld",
                                       exact_match=True)
        self.assertEqual(results, [])
        results = self.openid.enumerateUsers(fullname="Some User",
                                       exact_match=True)
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member1'])
        results = self.openid.enumerateUsers(email="some@user.com",
                                             exact_match=True)
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member1'])

    def testInexactStringSearch(self):
        results = self.openid.enumerateUsers(email="some@user.com",
                                       exact_match=False)
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member1'])

        results = self.openid.enumerateUsers(email="@user.com",
                                             exact_match=False)
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member1',
                                   'http://plone.myopenid.com/member2'])

        results = self.openid.enumerateUsers(email="@user.com",
                                             exact_match=True)
        results = [info['id'] for info in results]
        self.assertEqual(results, [])

    def testSearchEmptyId(self):
        self.assertEqual(self.openid.enumerateUsers(id=''), [])
        self.assertEqual(self.openid.enumerateUsers(login=''), [])

    def testSearchSort(self):
        results = self.openid.enumerateUsers(email="@user.com",
                                             exact_match=False,
                                             sort_by='fullname')
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member2',
                                   'http://plone.myopenid.com/member1'])

    def testSearchMaxResults(self):
        results = self.openid.enumerateUsers(email="@user.com",
                                             exact_match=False,
                                             sort_by='fullname',
                                             max_results=1)
        results = [info['id'] for info in results]
        self.assertEqual(results, ['http://plone.myopenid.com/member2'])

    def testSearchSequence(self):
        keys = ['http://plone.myopenid.com/member1',
                'http://plone.myopenid.com/member2']
        results = self.openid.enumerateUsers(id=keys)
        self.assertEqual(len(results), 2)
        results = self.openid.enumerateUsers(login=keys)
        self.assertEqual(len(results), 2)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UserSearchTest))
    return suite
