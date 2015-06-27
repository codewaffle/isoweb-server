_class_cache = {}


def load_class(classpath):
    mod, cls = classpath.rsplit('.', 1)
    val = getattr(__import__(mod), cls)
    _class_cache[classpath] = val

    return val


def get_class(classpath):
    return _class_cache.get(classpath, load_class(classpath))