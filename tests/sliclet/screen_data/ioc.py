import numpy

_X = 50
_Y_FACTOR = 1.3


def empty_image(self):
    return [0] * 50 * 65


def gaussian_image(self):
    sigma = _X // 5

    def _dist(vec, is_y):
        s = _y_adjust(sigma) if is_y else sigma
        return (vec - vec.shape[0] // 2) ** 2 / (2 * (s**2))

    def _norm(mat):
        return ((mat - mat.min()) / (mat.max() - mat.min())) * 255

    def _vec(size):
        return numpy.linspace(0, size - 1, size)

    x, y = numpy.meshgrid(_vec(_X), _vec(_y_adjust(_X)))
    return _norm(numpy.exp(-(_dist(x, False) + _dist(y, True)))).flatten()


def size_x(self):
    return _X


def size_y(self):
    return _y_adjust(_X)


def _y_adjust(value):
    return int(value * _Y_FACTOR)
