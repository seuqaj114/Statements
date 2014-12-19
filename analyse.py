# Pattern to isolate words in text set(map(lambda x: x.lower(),re.compile(r"\W+").split(text)))

from bs4 import BeautifulSoup
import urllib2
import re
import sys

from pymongo import MongoClient
from bson.objectid import ObjectId