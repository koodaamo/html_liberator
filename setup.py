from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='html_liberator',
      version=version,
      description="Extract HTML embedded within RTF documents",
      long_description="""\
HTML email sent by MS Outlook is embedded within RTF. This library helps extract the HTML.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='RTF HTML TNEF email microsoft outlook',
      author='Petri Savolainen',
      author_email='petri.savolainen@koodaamo.fi',
      url='',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
