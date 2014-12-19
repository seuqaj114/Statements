# Pattern to isolate words in text set(re.compile(r"[^a-zA-Z]+").split(text))

from bs4 import BeautifulSoup
import urllib2
import re
import sys

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://admin:admin@kahana.mongohq.com:10009/courier_db")
db = client.courier_db

def create_word_list():
	cursor = db.statements.find()
	print "%s statements to be searched..." % (cursor.count())

	word_list = []

	for i in range(cursor.count()):
		statement = cursor.next()
		statement_words = list(set(re.compile(r"[^a-zA-Z]+").split(statement["text"])))
		word_list+=statement_words
		word_list = list(set(word_list))
		print len(word_list)

	return word_list

def calculate_word_category_probability():
	"""
		P(word|category)= #
	"""