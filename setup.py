from distutils import msvccompiler
from setuptools.extension import Library

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

from Cython.Build import cythonize

import os
import glob

define_macros = []
extra_compile_args = []

if os.name == 'nt':
    msvccompiler.MSVCCompiler._c_extensions = []
    msvccompiler.MSVCCompiler._cpp_extensions.append('.c')

    define_macros = [
        # stupid build hacks..
        ('WIN32', '1'), # ('inline', '__inline')
    ]

    extra_compile_args=[
        # more stupid build hacks
        '/TP',
    ]


extensions = [
    Extension(
        'server.phys.*', ['phys/**/*.pyx'],
        libraries=['chipmunk'],
        include_dirs=['vendor/chipmunk/include'],
        library_dirs=['vendor/chipmunk/lib'],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        language='c++'
    ),
    Extension(
        'server.mathx.*', ['mathx/**/*.pyx'],
        include_dirs=['vendor/chipmunk/include'],
        library_dirs=['vendor/chipmunk/lib'],
        define_macros=define_macros,
    ),
    Extension(
        'server.*', ['**/*.pyx'],
    )
]

setup(
    name='isoweb_server',
    ext_modules=cythonize(extensions),
)

