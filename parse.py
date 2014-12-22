from bs4 import BeautifulSoup
import re
import sys

from pymongo import MongoClient
from bson.objectid import ObjectId

def clean_text(string):
	striped = [c for c in string if 0<ord(c)<127]
	return "".join(striped)

# THE MASTER PARSING OPERATION: FROM TEXT TO WORDS
def raw_text_to_words(string):
	clean_lower = clean_text(string.lower())
	word_list = list(set(re.compile(r"[^a-zA-Z]+").split(clean_lower)))
	if "" in word_list:
		word_list.remove("")

	return word_list

def clean_statements():
	client = MongoClient("mongodb://admin:admin@kahana.mongohq.com:10009/courier_db")
	db = client.courier_db

	for item in db.new_statements.find():
		print item["subject"]
		db.new_statements.update({"_id":ObjectId(item["_id"])},{"$set":{"words":raw_text_to_words(item["raw_text"])}})
		#db.statements.update({"_id":ObjectId(item["_id"])},{"$set":{"text":clean_text(item["text"].lower())}})

	print "Parsing complete!"