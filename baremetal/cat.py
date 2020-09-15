def cat(*args):
    result = args[0]
    for arg in args[1:]:
        result = result.cat(arg)
    return result
