class BaremetalException(Exception):
    pass


def error(message):
    raise BaremetalException(message)
