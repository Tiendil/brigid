def jinjaglobal(f):
    f._is_jinjaglobal = True
    return f


def jinjafilter(f):
    f._is_jinjafilter = True
    return f
