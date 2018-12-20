import copy
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft,ifft

__all__ = ['Wavedata', 'Blank', 'DC', 'Gaussian', 'CosPulse', 'Sin', 'Cos',]

class Wavedata(object):

    def __init__(self,domain=(0,1),sRate=1e2):
        '''domain: 定义域，即采点的区域，不能是inf'''
        self._domain = domain
        self.sRate = sRate
        # self._timeFunc = lambda x : 0
        self.data = self.generateData()

    def _mask(self, x):
        mask = (x>self._domain[0])*(x<self._domain[1])
        return mask

    def _timeFunc(self, x):
        return 0

    def __timeFunc(self, x):
        return self._mask(x)*self._timeFunc(x)

    def generateData(self):
        dt=1/self.sRate
        x = np.arange(self._domain[0]+dt/2, self._domain[1], dt)
        _data = self.__timeFunc(x)
        data = np.array(_data)
        return data

    def _blank(self,length=0):
        n = round(abs(length)*self.sRate)
        data = np.zeros(n)
        return data

    @property
    def len(self):
        length = self.size/self.sRate
        return length

    @property
    def size(self):
        size = len(self.data)
        return size

    def setLen(self,length):
        n = round(abs(length)*self.sRate)
        s = self.size
        if n > s:
            append_data=np.zeros(n-s)
            self.data = np.append(self.data, append_data)
        else:
            self.data = self.data[:n]
        return self

    def setSize(self,size):
        n = round(size)
        s = self.size
        if n > s:
            append_data=np.zeros(n-s)
            self.data = np.append(self.data, append_data)
        else:
            self.data = self.data[:n]
        return self

    def __pos__(self):
        return self
    #
    def __neg__(self):
        w = Wavedata()
        w.sRate = self.sRate
        w.data = -self.data
        return w

    def __abs__(self):
        w = Wavedata()
        w.sRate = self.sRate
        w.data = np.abs(self.data)
        return w

    def __rshift__(self, t):
        if abs(t)>self.len:
            raise Error('shift is too large !')
        w = Wavedata()
        w.sRate = self.sRate
        shift_data=self._blank(abs(t))
        left_n = self.size-len(shift_data)
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
        elif not self.sRate == other.sRate:
            raise Error('sRate not equal !')
        else:
            w = Wavedata()
            w.sRate = self.sRate
            w.data = np.append(self.data,other.data)
            return w

    def __add__(self, other):
        if isinstance(other,Wavedata):
            if not self.sRate == other.sRate:
                raise Error('sRate not equal !')
            else:
                w = Wavedata()
                w.sRate = self.sRate
                length = max(self.len, other.len)
                self.setLen(length)
                other.setLen(length)
                w.data = self.data + other.data
                return w
        else:
            return other + self

    def __radd__(self, v):
        w = Wavedata()
        w.sRate = self.sRate
        w.data = self.data +v
        return w

    def __sub__(self, other):
        return self + (- other)

    def __rsub__(self, v):
        return v + (-self)

    def __mul__(self, other):
        if isinstance(other,Wavedata):
            if not self.sRate == other.sRate:
                raise Error('sRate not equal !')
            else:
                w = Wavedata()
                w.sRate = self.sRate
                length = max(self.len, other.len)
                self.setLen(length)
                other.setLen(length)
                w.data = self.data * other.data
                return w
        else:
            return other * self

    def __rmul__(self, v):
        w = Wavedata()
        w.sRate = self.sRate
        w.data = self.data * v
        return w

    def __truediv__(self, other):
        if isinstance(other,Wavedata):
            if not self.sRate == other.sRate:
                raise Error('sRate not equal !')
            else:
                w = Wavedata()
                w.sRate = self.sRate
                length = max(self.len, other.len)
                self.setLen(length)
                other.setLen(length)
                w.data = self.data / other.data
                return w
        else:
            return (1/other) * self

    def __rtruediv__(self, v):
        w = Wavedata()
        w.sRate = self.sRate
        w.data = v / self.data
        return w

    def convolve(self, other, mode='full'):
        if isinstance(other,Wavedata):
            _kernal = other.data
        elif isinstance(other,(np.ndarray,list,tuple)):
            _kernal = other
        k_sum = sum(_kernal)
        kernal = _kernal / k_sum
        w = Wavedata()
        w.sRate = self.sRate
        w.data = np.convolve(self.data,kernal,mode)
        return w

    def FFT(self):
        w = Wavedata()
        w.sRate = self.size/self.sRate
        w.data =abs(fft(self.data))
        return w

    def plot(self):
        dt=1/self.sRate
        x = np.arange(dt/2, self.len, dt)
        y = self.data
        plt.plot(x, y)


class Blank(Wavedata):
    '''产生一个给定长度的0波形，长度可以为负或0'''
    def __init__(self, width=0, sRate=1e2):
        self.start = min(0,width)
        self.stop = max(0,width)
        super(Blank, self).__init__(domain=(self.start, self.stop),sRate=sRate)

class DC(Wavedata):
    '''产生一个给定长度的方波脉冲，高度为1'''
    def __init__(self, width=0, sRate=1e2):
        self.start = min(0,width)
        self.stop = max(0,width)
        self._timeFunc = lambda x : 1
        super(DC, self).__init__(domain=(self.start, self.stop),sRate=sRate)

class Gaussian(Wavedata):
    def __init__(self, width, sRate=1e2):
        c = width/(4*np.sqrt(2*np.log(2)))
        self._timeFunc = lambda x: np.exp(-0.5*(x/c)**2)
        super(Gaussian, self).__init__(domain=(-0.5*width,0.5*width),sRate=sRate)

class CosPulse(Wavedata):
    def __init__(self, width, sRate=1e2):
        self._timeFunc = lambda x: (np.cos(2*np.pi/width*x)+1)/2
        super(CosPulse, self).__init__(domain=(-0.5*width,0.5*width),sRate=sRate)

class Sin(Wavedata):
    def __init__(self, w, phi=0, width=0, sRate=1e2):
        self._timeFunc = lambda t: np.sin(w*t+phi)
        super(Sin, self).__init__(domain=(0,width),sRate=sRate)

class Cos(Wavedata):
    def __init__(self, w, phi=0, width=0, sRate=1e2):
        self._timeFunc = lambda t: np.cos(w*t+phi)
        super(Cos, self).__init__(domain=(0,width),sRate=sRate)


if __name__ == "__main__":
    a=Sin(w=1, width=10, phi=0, sRate=100000)
    b=Gaussian(2,sRate=100000)
    c=Wavedata(sRate=100000)

    m=(0.5*a|c|b|c|b+1|c|a+0.5).setLen(20)>>5
    n=m.convolve(b)
    m.plot()
    n.plot()
    plt.show()