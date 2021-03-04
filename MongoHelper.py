# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import HOST_DES,PORT_DES,USER_DES,PASSWORD_DES,DBNAME_DES
import json
import datetime

class MongoHelper(object):

    def __init__(self,tableName):
        self.tbName = tableName
        self.conn = None
        self.collection = None

        self.__connect()

    def __connect(self):
        try:
            uri = 'mongodb://' + USER_DES + ':' + PASSWORD_DES + '@' + HOST_DES + ':' + str(PORT_DES) +'/'+ DBNAME_DES
            self.conn = MongoClient(uri)
            db = self.conn.get_database(DBNAME_DES)
            self.collection = db[self.tbName]
        except Exception as e:
            print 'MongoDB connection error : %s' % e.message

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def select(self,findkey):
        try:   
            if self.collection is not None:

                rows = self.collection.find(findkey)

                if rows.count() > 0:
                    print "{0}   查询 mongodb 相同记录：{1} 条，跳过此次插入......".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),rows.count())
                    

                return 1 if rows.count() > 0 else 0

        except Exception as e:
            print 'Select data error: %s' % e.message
            self.close()

    def select2(self,findkey):
        try:   
            if self.collection is not None:

                rows = self.collection.find(findkey)

                if rows.count() > 0:
                    print "{0}   查询 mongodb 相同记录：{1} 条，跳过此次插入......".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),rows.count())
                    

                return rows

        except Exception as e:
            print 'Select data error: %s' % e.message
            self.close()

    def insert(self,insertData):
        try:   
            if self.collection is not None:

                # 插入新的记录
                self.collection.save(insertData)

        except Exception as e:
            print 'Insert data error: %s' % e.message
            self.close()

    def update(self,findkey,updateData):
        try:
            rows = self.collection.find(findkey)
            if rows.count() > 0:
                self.collection.update_one(findkey,{'$set':updateData})
            else:
                self.collection.save(updateData)
              
        except Exception as e:
            print 'Update data error: %s' % e.message
        
    def delete(self,findkey):
        try:
            rows = self.collection.find(findkey)
            if rows.count() > 0:
                self.collection.delete_many(findkey)
            else:
                self.collection.save(findkey)
              
        except Exception as e:
            print 'Update data error: %s' % e.message
  