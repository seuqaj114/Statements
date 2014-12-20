# Pattern to isolate words in text set(re.compile(r"[^a-zA-Z]+").split(text))

from bs4 import BeautifulSoup
import urllib2
import re
import sys

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://admin:admin@kahana.mongohq.com:10009/courier_db")
db = client.courier_db

number_to_text = {1:"one",2:"two",3:"three",4:"four",5:"five"}
text_to_number = {"one":1,"two":2,"three":3,"four":4,"five":5}

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

def populate_word_appearence():
	cursor = db.statements.find()
	print "%s statements to be searched..." % (cursor.count())

	#	This part is super sloooooooooow!
	for i in range(cursor.count()):
		print "Statement %s" % i

		statement = cursor.next()
		statement_words = list(set(re.compile(r"[^a-zA-Z]+").split(statement["text"])))
		for word in statement_words:
			db.words.update({"name":word},{"$inc":{number_to_text[statement["stars"]]}})

	print "Words' categories populated."
	return 1


def calculate_word_category_probability():
	"""
		P(word|category)= #
	"""
	return 0