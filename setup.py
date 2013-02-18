from distutils.core import setup, Command
from setuptools.command.test import test as TestCommand
import sys

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='majorityjudgement',
    version='0.1.2',
    author='David R. MacIver',
    author_email='david@drmaciver.com',
    packages=['majorityjudgement'],
    url='https://github.com/DRMacIver/majority-judgement-python',
    license='LICENSE.txt',
    description='Implementation of majority judgement voting procedure',
    long_description=open('README.txt').read(),
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)
