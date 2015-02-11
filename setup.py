from setuptools import setup, find_packages

version = '2.0.3'

setup(name='plone.openid',
      version=version,
      description="OpenID authentication support for PAS",
      long_description=open("README.txt").read() + '\n' +
                       open("CHANGES.txt").read(),
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='PAS openid authentication',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.openid',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'python-openid >=2.2.1,<2.3dev',
        'transaction',
        'Acquisition',
        'Products.PluggableAuthService',
        'ZODB3',
        'Zope2',
      ],
      )
