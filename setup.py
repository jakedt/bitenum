#!/usr/bin/env python

from distutils.core import setup


version = __import__('bitenum').__version__


setup(name='bitenum',
      version=version,
      description='Bit packing implementation of enumerations.',
      author='Jake Moshenko',
      author_email='jake.moshenko@coreos.com',
      url='https://github.com/jakedt/bitenum',
      packages=['bitenum'],
      install_requires=['six>=1.4.0'],
      test_suite='nose.collector',
      tests_require=['nose'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: PyPy',
      ]
     )
