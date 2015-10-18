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
        ('WIN32', '1'), ('inline', '__inline')
    ]

    extra_compile_args=[
        # more stupid build hacks
        '/TP',
    ]

chipmunk_src = glob.glob('phys/src/*.c')

extensions = [
    Library(
        name='chipmunk',
        sources=chipmunk_src,
        include_dirs=['phys/include'],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
    ),
    Extension(
        'server.phys.*', ['phys/**/*.pyx'],
        libraries=['chipmunk'],
        include_dirs=['phys/include'],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
    ),
    Extension('*', ['**/*.pyx']),
]

setup(
    ext_modules=cythonize(extensions),
)

