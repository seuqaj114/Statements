# Pattern to isolate words in text set(re.compile(r"[^a-zA-Z]+").split(text))

from bs4 import BeautifulSoup
import re
import sys

from pymongo import MongoClient
from bson.objectid import ObjectId

import parse

client = MongoClient("mongodb://admin:admin@kahana.mongohq.com:10009/courier_db")
db = client.courier_db

number_to_text = {1:"one",2:"two",3:"three",4:"four",5:"five"}
text_to_number = {"one":1,"two":2,"three":3,"four":4,"five":5}
statements_with_star = {1:db.new_statements.find({"stars":1}).count(),
						2:db.new_statements.find({"stars":2}).count(),
						3:db.new_statements.find({"stars":3}).count(),
						4:db.new_statements.find({"stars":4}).count(),
						5:db.new_statements.find({"stars":5}).count()}


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

def add_word_list_to_statements():
	cursor = db.statements.find()
	print "%s statements to be updated..." % (cursor.count())

	for i in range(cursor.count()):
		print "Statement %s" % i

		statement = cursor.next()
		statement_words = list(set(re.compile(r"[^a-zA-Z]+").split(statement["text"])))
		statement_words.remove("")
		db.statements.update({"_id":ObjectId(statement["_id"])},{"words":statement_words})

	print "Statements updated."

def populate_word_appearence():
	cursor = db.statements.find()
	print "%s statements to be searched..." % (cursor.count())

	word_list = db.word_list.find_one()["word_list"]
	classifications = { word:{"one":0,"two":0,"three":0,"four":0,"five":0} for word in word_list}

	#	Not so slow anymore!
	for i in range(cursor.count()):
		print "Statement %s" % i

		statement = cursor.next()
		statement_words = list(set(re.compile(r"[^a-zA-Z]+").split(statement["text"])))
		statement_words.remove("")
		for word in statement_words:
			if word in classifications:
				classifications[word][number_to_text[statement["stars"]]]+=1
	
	for word in word_list:
		db.words.update({"name":word},{"$inc":{"one":classifications[word]["one"],
												"two":classifications[word]["two"],
												"three":classifications[word]["three"],
												"four":classifications[word]["four"],
												"five":classifications[word]["five"]}})

	print "Words' categories populated."
	return 1


def calculate_document_probabilities(raw_text):
	words = parse.raw_text_to_words(raw_text)
	print "Words to be calculated: %s" % (len(words))

	probs = {1:1,2:1,3:1,4:1,5:1}
	cursor = db.words.find({"name":{"$in":words}})

	total_statements = db.new_statements.find().count()
	cat_probs = { i:float(db.new_statements.find({"stars":i}).count())/total_statements for i in range(1,6)}

	for i in range(cursor.count()):
		#print "calculating word %s" % i
		word = cursor.next()
		if word["conditionals"]["one"]==0 or \
			word["conditionals"]["two"]==0 or \
			word["conditionals"]["three"]==0 or \
			word["conditionals"]["four"]==0 or \
			word["conditionals"]["five"]==0:
			pass
		else:
			for j in probs:
				probs[j]*=word["conditionals"][number_to_text[j]]

	for j in probs:
		probs[j]*=cat_probs[j]

	prob_list = [probs[key] for key in probs]
	stars = prob_list.index(max(prob_list))+1
	exac = 1.0-max(prob_list)/sum(prob_list)

	return stars,exac,probs

def calculate_word_probabilities(word):
	""" word must be a db.words query """

	probabilities = {"one":0,"two":0,"three":0,"four":0,"five":0}

	for star in range(1,6):
		conditional = float(word[number_to_text[star]])/statements_with_star[star]
		probabilities[number_to_text[star]]=conditional*10

	db.words.update({"_id":ObjectId(word["_id"])},{"$set":{"conditionals":probabilities}})

	return 1

def populate_word_probabilities():
	cursor = db.words.find()
	print "%s words to be searched..." % (cursor.count())

	for i in range(cursor.count()):
		print "Word %s" % i

		word = cursor.next()

		calculate_word_probabilities(word)

	print "Populate complete."