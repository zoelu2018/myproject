# -*- coding:utf-8 -*-
# @Time : 2021/3/1 16:19
# @Author: luxl
# @python-v: 3.9
# @File : 08队列.py.py
# 队列 先进先出
class Queue():
    def __init__(self,size =4):
        self.item = DoubleLinkedList()
        self.size = size
        self.length = 0
    def put(self,value):
        self.item