# -*- coding:utf-8 -*-
# @Time : 2021/3/1 16:37
# @Author: luxl
# @python-v: 2.7
# @File : 07haxi.py.py
class Array():
    def __init__(self,size =4):
        self.__size = size
        self.__item = [None]*size
        self.__length = 0
    def __setitem__(self, key, value):
        self.__item = value
        self.__length +=1
    def __getitem__(self, key):
        return self.__item[key]
    def __len__(self):
        return self.__length
    def __iter__(self):
        for value in self.__item:
            yield value

class Slot():
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __str__(self):
        return 'key:{} value:{}'. format(self.key,self.value)
class HashTable():
    def __init__(self):
        self.size =4
        self.items = Array(self.size)

    def get_index(self,key):
        return hash(key) % self.size
    def put(self,key,value):
        s = Slot(key,value)
    def get(self,key):
        index = self.get_index(key)
        return self.items[index]




if __name__ == "__main__":
    h = HashTable()
    h.put('name','吕布')
    h.put('sex','男')