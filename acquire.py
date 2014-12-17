from bs4 import BeautifulSoup
import urllib2
import re

def get_statement_text(url):
	return 0

base_url = "https://www.studential.com"

# url of subjects: https://www.studential.com/personal-statement-examples/subjects
page = urllib2.urlopen("https://www.studential.com/personal-statement-examples/subjects")
soup = BeautifulSoup(page.read())
chunk=soup.find("div",{"id":"content"})
content=chunk.find("div",{"class":"content"})

# regex to find valid href's: ^/personal-statement-examples/.*-personal-statements$
subjects = content.find_all("a",href = re.compile(r'^/personal-statement-examples/.*-personal-statements$'))

# subjects[i]["href"] to access href
for a in subjects:
	subject_page = urllib2.urlopen(base_url+a["href"])
	subject_soup = BeautifulSoup(subject_page.read())
	statement_chunk = subject_soup.find("div",{"id":"content"})
	statements = statement_chunk.find_all("p")

	for statement in statements[:-1]:
		if len(statement.find_all("img")) != 0:
			stars = statement.find_all("img")
			# statement.find("a")["href"] to access href