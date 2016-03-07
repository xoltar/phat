from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import sys
import os.path
ext_modules = [
    Extension(
        '_phat',
        ['_phat.cpp'],
        include_dirs=['include', '../include'],
        language='c++',
    ),
]

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': ['-std=c++11'],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

setup(
    name='phat',
    version='0.0.1',
    author='Bryn Keller',
    author_email='xoltar@xoltar.org',
    url='https://bitbucket.org/phat-code/phat',
    description='Python bindings for PHAT',
    license = 'LGPL',
    keywords='algebraic-topology PHAT distributed topology persistent-homology',
    long_description=long_description,
    ext_modules=ext_modules,
    install_requires=['pybind11'],
    cmdclass={'build_ext': BuildExt},
    py_modules = ['phat'],
    # packages = find_packages(exclude = ['doc', 'test'])
 )





