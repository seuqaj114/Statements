from bs4 import BeautifulSoup
import urllib3
import re
import sys

from pymongo import MongoClient

client = MongoClient("mongodb://admin:admin@kahana.mongohq.com:10009/courier_db")
db = client.courier_db

base_url = "https://www.studential.com"

# url of subjects: https://www.studential.com/personal-statement-examples/subjects
page = urllib3.urlopen("https://www.studential.com/personal-statement-examples/subjects")
soup = BeautifulSoup(page.read())
chunk=soup.find("div",{"id":"content"})
content=chunk.find("div",{"class":"content"})

# regex to find valid href's: ^/personal-statement-examples/.*-personal-statements$
subjects = content.find_all("a",href = re.compile(r'^/personal-statement-examples/.*-personal-statements$'))

# subjects[i]["href"] to access href
for a in subjects[:]:

	subject = re.match(r"^/personal-statement-examples/(.*)-personal-statements$",a["href"]).group(1)
	print subject

	subject_page = urllib3.urlopen(base_url+a["href"])
	subject_soup = BeautifulSoup(subject_page.read())
	statement_chunk = subject_soup.find("div",{"id":"content"})
	statements = statement_chunk.find_all("p")

	for statement in statements[:-1]:
		stars = len(statement.find_all("img"))
		print stars
		if stars != 0:
			# statement.find("a")["href"] to access href
			print statement.find("a")["href"]
			statement_page = urllib3.urlopen(base_url+statement.find("a")["href"])
			statement_soup = BeautifulSoup(statement_page.read())
			statement_content = statement_soup.find("div",{"id":"editmain"})
			
			# This is the statement's final text
			unparsed_text = statement_content.text

			db.statements.insert({"text":unparsed_text,"stars":stars,"subject":subject})
			print "Insertion complete."
		else:
			pass
