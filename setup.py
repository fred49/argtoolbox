#!/usr/bin/env python
"""Packaging script."""

import codecs
import os
import re
import shlex
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

HERE = os.path.abspath(os.path.dirname(__file__))

# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    """TODO"""
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(HERE, *file_paths), 'r') as fde2:
        version_file = fde2.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get the long description from the relevant file
with codecs.open('README.rst', encoding='utf-8') as fde:
    LONG_DESCRIPTION = fde.read()


def run_command(cmd, return_stdout=False):
    """TODO"""
    dpkg_process = subprocess.Popen(shlex.split(cmd),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    stdout, stderr = dpkg_process.communicate()
    status = False
    if dpkg_process.wait() == 0:
        status = True
    #print stderr
    if return_stdout:
        return (status, stdout.decode('utf8').strip('\n'))
    return status

class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly
    greeting."""

    def run(self):
        install.run(self)
        # Detection of virtual env installation.
        if os.getenv('VIRTUAL_ENV', False):
            self.install_virtual_env()
        else:
            self.install_etc()

    def install_virtual_env(self):
        """Installation in a virtualenv."""
        print("\nINFO: Registering argcomplete support in the current virtualenv for auto activation.")
        directory = os.getenv('VIRTUAL_ENV')
        cmd = "activate-global-python-argcomplete --dest "
        cmd += os.path.join(directory, 'bin')
        subprocess.call(shlex.split(cmd))
        fde2 = open(os.path.join(directory, 'bin', 'activate'), 'a')
        data = "\nsource "
        data += os.path.join(directory, 'bin', 'python-argcomplete.sh')
        data += '\n'
        fde2.write(data)
        fde2.close()
        print("INFO: You may need to launch a new install of bash for the auto completion to be active.\n")

    def install_etc(self):
        """TODO"""
        print("\nINFO: Registering argcomplete support in /etc/ for global activation.")
        cmd = "activate-global-python-argcomplete --global"
        status = run_command(cmd)
        if not  status:
            print("WARN: Global activation for argcomplete failed !!!")
            print("WARN: See 'argtoolboxtool register -h'.\n")


setup(
    cmdclass={'install': CustomInstallCommand},
    name='argtoolbox',
    version=find_version('argtoolbox', '__init__.py'),
    description='The easy way to create a short program with file options and command line options.',
    long_description=LONG_DESCRIPTION,

    # The project URL.
    url='https://github.com/fred49/argtoolbox',

    # Author details
    author='Frederic MARTIN',
    author_email='frederic.martin.fma@gmail.com',

    # Choose your license
    license="GPL3",

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='argparse ConfigFile command line interface',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages.
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),

    package_data={
        'argtoolbox': ['templates/*.tml'],
    },
    entry_points={
        'console_scripts': ['argtoolboxtool=argtoolbox.commands:PROG'],
    },

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed.
    install_requires=[
        'argparse',
        'argcomplete==1.9.2'
    ],
    test_suite='tests.get_all_tests',
)
