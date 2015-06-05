#!/usr/bin/env python

from distutils.core import setup, Command
import pytest


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = pytest.main([])
        raise SystemExit(errno)


setup(name='webhealth',
      version='1.0',
      description='Bulk website health checker',
      author='henadzit',
      packages=['webhealth'],
      cmdclass={'test': PyTest},)