__author__ = 'Adam'


class Temperature(object):

    def __init__(self):
        self.c_temp = 0

    def f_get(self):
        return self.celsius * 9 / 5 + 32
    def f_set(self, value):
        self.celsius = (float(value)-32) * 5 / 9
    fahrenheit = property(f_get, f_set)

    def c_set(self, value):
        self.c_temp = float(value)
    def c_get(self):
        return self.c_temp
    celsius = property(c_get, c_set)
