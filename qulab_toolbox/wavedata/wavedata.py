import copy
import numpy as np
import matplotlib.pyplot as plt


class Wavedata(object):

    def __init__(self,domain=(0,1),sampleRate=1e2):
        '''domain: 定义域，即采点的区域，不能是inf'''
        self._domain = domain
        self.len = domain[1] - domain[0]
        self.sampleRate = sampleRate
        self._timeFunc = lambda x : 0
        self.data = self.generateData()

    def _mask(self, x):
        mask = (x>self._domain[0])*(x<self._domain[1])
        return mask

    def __timeFunc(self, x):
        return self._mask(x)*self._timeFunc(x)

    def generateData(self):
        dt=1/self.sampleRate
        x = np.arange(self._domain[0]+dt/2, self._domain[1], dt)
        _data = self.__timeFunc(x)
        data = np.array(_data)
        return data

    def _blank(self,length=0):
        n = int(abs(length)*self.sampleRate)
        data = np.zeros(n)
        return data

    def len(self):
        return self.len

    def setLen(self,length):
        n = int(abs(length)*self.sampleRate)
        l = int(self.len*self.sampleRate)
        if n >l:
            append_data=np.zeros(n-l)
            self.data = np.append(self.data, append_data)
            self.len = length
        else:
            self.data = self.data[:n]
            self.len = length

    def __pos__(self):
        return self
    #
    def __neg__(self):
        w = Wavedata()
        w.sampleRate = self.sampleRate
        w.len = self.len
        w.data = -self.data
        return w

    def __abs__(self):
        w = Wavedata()
        w.sampleRate = self.sampleRate
        w.len = self.len
        w.data = np.abs(self.data)
        return w

    def __rshift__(self, t):
        if abs(t)>self.len:
            raise Error('shift is too large !')
        w = Wavedata()
        w.sampleRate = self.sampleRate
        w.len = self.len
        shift_data=self._blank(abs(t))
        left_n = int((self.len-abs(t))*self.sampleRate)
        if t>0:
            w.data = np.append(shift_data, self.data[:left_n])
        else:
            w.data = np.append(self.data[-left_n:], shift_data)
        return w

    def __lshift__(self, t):
        return self >> (-t)

    def __or__(self, other):
        if not isinstance(other,Wavedata):
            raise TypeError('not Wavedata class !')
        elif not self.sampleRate == other.sampleRate:
            raise Error('sampleRate not equal !')
        else:
            w = Wavedata()
            w.sampleRate = self.sampleRate
            w.len = self.len + other.len
            w.data = np.append(self.data,other.data)
            return w

    def __add__(self, other):
        if isinstance(other,Wavedata):
            if not self.sampleRate == other.sampleRate:
                raise Error('sampleRate not equal !')
            else:
                w = Wavedata()
                w.sampleRate = self.sampleRate
                length = max(self.len, other.len)
                self.setLen(length)
                other.setLen(length)
                w.data = self.data + other.data
                w.len = length
                return w
        else:
            return other + self

    def __radd__(self, v):
        w = Wavedata()
        w.sampleRate = self.sampleRate
        w.len = self.len
        w.data = self.data +v
        return w

    def __sub__(self, other):
        return self + (- other)

    def __rsub__(self, v):
        return v + (-self)

    def __mul__(self, other):
        if isinstance(other,Wavedata):
            if not self.sampleRate == other.sampleRate:
                raise Error('sampleRate not equal !')
            else:
                w = Wavedata()
                w.sampleRate = self.sampleRate
                length = max(self.len, other.len)
                self.setLen(length)
                other.setLen(length)
                w.data = self.data * other.data
                w.len = length
                return w
        else:
            return other * self

    def __rmul__(self, v):
        w = Wavedata()
        w.sampleRate = self.sampleRate
        w.len = self.len
        w.data = self.data * v
        return w

    def __truediv__(self, other):
        if isinstance(other,Wavedata):
            if not self.sampleRate == other.sampleRate:
                raise Error('sampleRate not equal !')
            else:
                w = Wavedata()
                w.sampleRate = self.sampleRate
                length = max(self.len, other.len)
                self.setLen(length)
                other.setLen(length)
                w.data = self.data / other.data
                w.len = length
                return w
        else:
            return other / self

    def __rtruediv__(self, v):
        w = Wavedata()
        w.sampleRate = self.sampleRate
        w.len = self.len
        w.data = v / self.data
        return w

    def plot(self):
        dt=1/self.sampleRate
        x = np.arange(dt/2, self.len, dt)
        y = self.data
        plt.plot(x, y)
