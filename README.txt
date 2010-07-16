OpenID PAS support
==================

Introduction
------------

This product implements OpenID_ authentication support for Zope_ via a
Pluggable Authentication Service plugin. 

Using this package everyone with an OpenID authentity will be able to
login on your Zope site. OpenID accounts are not given any extra roles
beyond the standard Authenticated role. This allows you to make a distinction
between people that have explicitly signed up to your site and people
who are unknown but have succesfully verified their identity.

.. _Zope: http://www.zope.org/
.. _OpenID: http://www.openidenabled.com/

Authentication flow
-------------------

The OpenID authentication flow goes like this:

- user submits a OpenID identity (which is a URL) to you site. This is
  done through a HTTP POST using a form variable called ``__ac_identity_url``
- the PAS plugin sees this variable during credential extraction and 
  initiates a OpenID challenge. This results in a transaction commit and
  a redirect to an OpenID server.
- the OpenID server takes care of authenticating the user and redirect the
  user back to the Zope site.
- the OpenID PAS plugin extracts the information passed in via the OpenID
  server redirect and uses that in its authentication code to complete the
  OpenID authentication

Session management
------------------

The PAS plugin only takes care of authenticating users. In almost all
environments it will be needed to also setup a session so users stay
logged in when they visit another page. This can be done via a special
session management PAS plugin, for example `plone.session`_.

.. _plone.session: http://pypi.python.org/pypi/plone.session
