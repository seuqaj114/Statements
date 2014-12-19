from bs4 import BeautifulSoup
import urllib2
import re
import sys

from pymongo import MongoClient
from bson.objectid import ObjectId

def clean_text(string):
	striped = [c for c in string if 0<ord(c)<127]
	return "".join(striped)

client = MongoClient("mongodb://admin:admin@kahana.mongohq.com:10009/courier_db")
db = client.courier_db

for item in db.statements.find():
	print item["subject"]
	db.statements.update({"_id":ObjectId(item["_id"])},{"$set":{"text":clean_text(item["text"].lower())}})

print "Parsing complete!"