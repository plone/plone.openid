OpenID PAS support
==================

Installing plone.openid
-----------------------

This package is made to be used as a normal python package within Zope 2. This 
is only supported in Zope 2.10 or later. If you are using Zope 2.8 or Zope 2.9
you can install the pythonproducts package from
http://dev.serverzen.com/site/projects/pythonproducts to add python product
support to your Zope.

After installing this product in your python path it needs to be registered
in your Zope instance. This can be done by putting a
plone.openid-configure.zcml file in the etc/pakage-includes directory with
this content::

  <include package="plone.openid" />


Other stuff
-----------
The OpenID authentication flow goes like this:

- user submits a ID (which is a URL) to you site
- consumer.begin(id).redirectURL(..) returns a redirect URL
- after auth the user is redirect back to a url in the plone site; the
  auth response is verified there. If succesfull a cookie is set
- the cookie is checked with the OpenID consumer

Plugins:
- credential extraction:
  - takes the cookie and extracts the openid information from it. Should
    use the standard Zope cookie in order to cleanly leverage CacheFu.
    TODO: check if the cookie auth plugin will bite us here by invaliding
    our cookie
- authentication:
  - takes the cookie information and verifies it

- login form handling takes the url and does the redirect. Return redirect
  to what though?
  -> credential extraction plugin
  -> auth plugin will set cookie if credentials authenticate

- use a challenge plugin for non-Plone sites to present the login form


Storage
-------
A custom storage is needed:
- the secret should be generated once and stored on the plugin. Maybe
  a 'reset secret' button would be useful - that will force all existing
  cookies to be invalidated
- storage should be in the ZODB/ZEO in order to support clustered setups
- 
