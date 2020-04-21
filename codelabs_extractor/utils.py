from bs4 import BeautifulSoup as Html
from urllib.request import urlopen
import re

def getFileHtml(filename: str):
	with open(filename, "rb") as f:
		return Html(f.read(), features='html.parser')

def getPageHtml(url: str):
	# TODO remove this
	if "kotlin-android-training-welcome" in url:
		return getFileHtml("kotlin0.html")
	elif "kotlin-android-training-install-studio" in url:
		return getFileHtml("kotlin1.html")
	elif "kotlin-android-training-get-started" in url:
		return getFileHtml("kotlin2.html")

	html = urlopen(url).read()
	return Html(html, features='html.parser')

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
