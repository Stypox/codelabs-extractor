from bs4 import BeautifulSoup as Html
from urllib.request import urlopen
from urllib.parse import urlparse
import re

def getPageHtml(url: str):
	html = urlopen(url).read()
	return Html(html, features='html.parser')

def extractHost(url: str):
	parsed = urlparse(url)
	return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed)

def optionalGet(dictionary_like, key):
	try:
		return dictionary_like[key]
	except KeyError:
		return None

def firstMatchRegex(string: str, regex: str):
	if string is None or regex is None:
		return None

	parser = re.compile(regex)
	match = parser.search(string)
	if match is None:
		return None
	else:
		return match.group(1)

def detectLanguage(code: str, default_code_language: str):
	def count_occourences(strings: list):
		sum = 0
		for string in strings:
			sum += code.count(string)
		return sum

	xmlCount = count_occourences(["<", ">", "/", "\""])
	javaKotlinCount = count_occourences(["(", ")", "{", "}", "."])
	javaCount = count_occourences([";", "@"])
	kotlinCount = count_occourences(["?", "!", ":"])

	if xmlCount > javaKotlinCount:
		if xmlCount >= 4:
			return "xml"
	elif javaCount > kotlinCount:
		if javaCount >= 3:
			return "java"
	else:
		if kotlinCount >= 3:
			return "kotlin"

	return default_code_language

def commonStartingSubstring(str1: str, str2: str):
	for i in range(min(len(str1), len(str2))):
		if str1[i] != str2[i]:
			return str1[:i]
	return str2 if len(str1) > len(str2) else str1

# see https://stackoverflow.com/q/1091945
def escapeXml(string: str):
	for ch, rep in [("&","&amp;"), ('"',"&quot;"), ("'","&apos;"), ("<","&lt;"), (">","&gt;")]:
		string = string.replace(ch, rep)
	return string
