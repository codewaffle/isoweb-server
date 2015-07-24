import gevent.monkey
gevent.monkey.patch_all(ssl=False)
import pyximport
pyximport.install(setup_args={
    'include_dirs': './pyxh/',
})
