from bs4 import BeautifulSoup as Html
from urllib.request import urlopen
import re

def getFileHtml(filename):
	with open(filename, "rb") as f:
		return Html(f.read(), features='html.parser')

def getPageHtml(url):
	# TODO remove this
	if "kotlin-android-training-welcome" in url:
		return getHtmlFile("kotlin0.html")
	elif "kotlin-android-training-install-studio" in url:
		return getHtmlFile("kotlin1.html")
	elif "kotlin-android-training-get-started" in url:
		return getHtmlFile("kotlin2.html")

	html = urlopen(url).read()
	return Html(html, features='html.parser')

def optionalGet(dictionary_like, key):
	try:
		return dictionary_like[key]
	except KeyError:
		return None

def firstMatchRegex(string, regex):
	if string is None or regex is None:
		return None

	parser = re.compile(regex)
	match = parser.search(string)
	if match is None:
		return None
	else:
		return match.group(1)

def detectLanguage(code):
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

	return detectLanguage.default_language

detectLanguage.default_language = ""