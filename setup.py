from setuptools import setup, find_packages

version = '1.1'

setup(name='plone.openid',
      version=version,
      description="OpenID authentication support for PAS",
      long_description=open("README.txt").read() + \
                       open("docs/HISTORY.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='PAS openid authentication',
      author='Wichert Akkerman - Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.openid',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://dist.plone.org',
#      dependency_links = [
#          'http://www.openidenabled.com/resources/downloads/python-openid/',
#      ],
      install_requires=[
        'setuptools',
        'python-openid >=2.0.0,<2.0.999',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
