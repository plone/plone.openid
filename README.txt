OpenID PAS support
==================

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
