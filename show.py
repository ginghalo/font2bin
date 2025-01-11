# -*- coding: utf-8 -*-
from PIL import Image


if __name__ == '__main__':
    unicode = '就'.encode('utf-8')
    bin_file = 'SourceHanSerifSC-SemiBold\SourceHanSerifSC-SemiBold.bin'
    with open(bin_file,'rb') as f:
        f.seek(ord('就') * 256)
        data = f.read(256)

        img = Image.frombytes("L",(16,16),data)
        img.show()