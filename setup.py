from setuptools import setup, find_packages

version = '2.0.5'

setup(
    name='plone.openid',
    version=version,
    description="OpenID authentication support for PAS",
    long_description=(open("README.rst").read() + '\n' +
                      open("CHANGES.rst").read()),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Systems Administration :: Authentication/Directory",  # noqa
    ],
    keywords='PAS openid authentication',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.openid',
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
