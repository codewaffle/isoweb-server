from distutils import msvccompiler

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
    Extension(
        'phys.chipmunk',
        chipmunk_src + ['phys/chipmunk.pyx'],
        include_dirs=['phys/include'],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
    ),
    Extension(
        'phys.*', ['phys/**/*.pyx'],
    ),
    Extension('*', ['**/*.pyx']),
]

setup(
    ext_modules=cythonize(extensions),
)

