import numpy as np
from ._wavedata import Wavedata
import scipy.signal as signal
import matplotlib.pyplot as plt


class Filter(object):
    """Filter baseclass, filt nothing."""
    def __init__(self, process=None):
        super(Filter, self).__init__()
        if process is not None:
            self.process = process

    def process(self,data,sRate):
        '''Filter处理函数，输入输出都是(data,sRate)格式'''
        return data,sRate

    def filt(self,w):
        '''传入Wavedata，返回滤波后的Waveda'''
        assert isinstance(w,Wavedata)
        data,sRate = self.process(w.data,w.sRate)
        return Wavedata(data,sRate)


def series(*arg):
    '''串联多个Filter'''
    def process(data,sRate):
        for f in arg:
            data,sRate = f.process(data,sRate)
        return data,sRate
    F = Filter()
    F.process=process
    return F


def parallel(*arg):
    '''并联多个Filter'''
    def process(data,sRate):
        d_list = [f.process(data,sRate)[0] for f in arg]
        d = np.array(d_list).sum(axis=0)/len(arg)
        return d,sRate
    F = Filter()
    F.process=process
    return F


class WGN(Filter):
    '''White Gaussian Noise adder: 向波形w中添加一个信噪比为 snr dB 的高斯白噪声'''
    def __init__(self, snr):
        super(WGN, self).__init__()
        self.snr = snr

    def process(self,data,sRate):
        x=data
        snr = 10**(self.snr/10.0)
        xpower = np.sum(x**2)/len(x)
        npower = xpower / snr
        n = np.random.randn(len(x)) * np.sqrt(npower)
        _data = x + n
        return _data,sRate

class IIRfilter(Filter):
    """docstring for IIRfilter."""
    def __init__(self, N=1, Wn=[49e6, 51e6], rp=0.01, rs=100, btype='band',
                     ftype='ellip', fs=1e9):
        # 默认参数是一个50MHz的 ellip 滤波器
        super(IIRfilter, self).__init__()
        # IIRfilter 配置字典, default: output='ba',analog=False,
        self.dict=dict(N=N, Wn=Wn, rp=rp, rs=rs, btype=btype,
                        analog=False, ftype=ftype, output='ba', fs=fs)
        self.ba = signal.iirfilter(**self.dict)

    def process(self,data,sRate):
        assert sRate == self.dict['fs']
        b,a = self.ba
        _data = signal.filtfilt(b, a, data)
        return _data, sRate

    def freqz(self):
        '''返回数字滤波器频率响应'''
        w,h = signal.freqz(*self.ba,fs=self.dict['fs'])
        return w,h

    def plot(self):
        '''画出频率响应曲线'''
        w,h=self.freqz()
        plt.plot(w, np.abs(h))
        plt.xlabel('Frequency')
        plt.ylabel('factor')
