# -*- coding:utf-8 -*-
# @Time : 2020/12/9 17:15
# @Author: luxl
# @python-v: 2.7
# @File : RESIZE.py.py
from PIL import Image
import os
def main(file):
    img = Image.open(file)
    img = img.resize((4096, 4096))
    filename = os.path.splitext(file)[0]+'.jpg'
    img.save(filename)
if __name__ == '__main__':
    filedir = "C:/Users/30494/Desktop/test/tile/all/"
    for dir, root, filelist in os.walk(filedir):
        for filename in filelist:
            main(os.path.join(dir,filename))

