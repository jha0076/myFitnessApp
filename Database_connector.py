# -*- coding: utf-8 -*-
"""
Created on Wed May  5 16:16:51 2021

@author: HI
"""


from pymongo import MongoClient
client=MongoClient( 'mongodb+srv://Admin:Admin@cluster0-rbvkk.mongodb.net/project?retryWrites=true&w=majority')
db=client.get_database('IIITteamData')
records=db.user
print(records.count_documents({}))
print(list(records.find()))
