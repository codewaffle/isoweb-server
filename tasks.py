import os
import sys

from invoke import run, task


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def ensure_vcvars():
    if which('cl.exe') is None:
        assert 'ProgramFiles(x86)' in os.environ, 'It appears you are not on a 64-bit Windows system.. cannot proceed'
        output = run('"{}" x64 && {} -c "import os; print(repr(dict(os.environ)))"'.format(os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft Visual Studio 14.0', 'VC', 'vcvarsall.bat'), sys.executable))
        # update local environ
        new_environ = eval(output.stdout)
        os.environ.update(new_environ)
        print('vcvars injected')


@task
def build_chipmunk():
    assert os.name == 'nt', 'Only Windows support has been implemented so far'

    ensure_vcvars()

    os.makedirs('build/chipmunk', exist_ok=True)
    opath = os.getcwd()
    os.chdir('build/chipmunk')

    assert which('cl.exe'), 'cl.exe not found in PATH'

    run('cl /c /Ox /fp:fast /I../../vendor/chipmunk/include /DWIN32 /DNDEBUG ../../vendor/chipmunk/src/*.c')

    os.makedirs('../../vendor/chipmunk/lib', exist_ok=True)
    run('lib *.obj /OUT:../../vendor/chipmunk/lib/chipmunk.lib')

    os.chdir(opath)


@task
def build():
    build_chipmunk()
