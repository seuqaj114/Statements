from bs4 import BeautifulSoup
import urllib2
import re

base_url = "https://www.studential.com"

# url of subjects: https://www.studential.com/personal-statement-examples/subjects
page = urllib2.urlopen("https://www.studential.com/personal-statement-examples/subjects")
soup = BeautifulSoup(page.read())
chunk=soup.find("div",{"id":"content"})
content=chunk.find("div",{"class":"content"})

# regex to find valid href's: ^/personal-statement-examples/.*-personal-statements$
subject_list = content.find_all("a",href = re.compile(r'^/personal-statement-examples/.*-personal-statements$'))

# subjects[i]["href"] to access href