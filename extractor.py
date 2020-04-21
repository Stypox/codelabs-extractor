from bs4 import BeautifulSoup as Html
from bs4.element import NavigableString
from urllib.request import urlopen
import re
import os


def getHtmlFile(filename):
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


class Element:
	def __init__(self):
		self.children = []
	def addChild(self, child):
		self.children.append(child)

	def __repr__(self):
		return f"[{', '.join([c.__repr__() for c in self.children])}]"
	def markdown(self):
		return "".join([c.markdown() for c in self.children])

class Text(Element):
	def __init__(self, text: str):
		self.text = text

	def __repr__(self):
		return f"{{Text, \"{self.text}\"}}"
	def markdown(self):
		return self.text

class Step(Element):
	def __init__(self, label: str, index: int):
		super().__init__()
		self.label = label
		self.index = index

	def __repr__(self):
		return f"{{Step {self.index}, \"{self.label}\", {super().__repr__()}}}"
	def markdown(self):
		return f"# {self.index}. {self.label}\n{super().markdown()}"

class Paragraph(Element):
	def __repr__(self):
		return f"{{Paragraph, {super().__repr__()}}}"
	def markdown(self):
		return f"\n{super().markdown()}\n"

class Header(Element):
	def __init__(self, size: int):
		super().__init__()
		self.size = size

	def __repr__(self):
		return f"{{Header, size={self.size}, {super().__repr__()}}}"
	def markdown(self):
		return f"{'#'*self.size} {super().markdown()}\n"

class Link(Element):
	def __init__(self, link: str):
		super().__init__()
		self.link = link

	def __repr__(self):
		return f"{{Link, \"{self.link}\", {super().__repr__()}}}"
	def markdown(self):
		content = super().markdown()
		if content.strip() == "":
			content = self.link
		return f"[{content}]({self.link})"

class ListItem(Element):
	def __init__(self):
		super().__init__()
	def set_index(self, index):
		self.index = index

	def __repr__(self):
		return f"{{ListItem, index={self.index}, {super().__repr__()}}}"
	def markdown(self):
		if self.index == -1:
			return f"- {super().markdown()}\n"
		else:
			content = super().markdown().replace("\n", "<br>")
			return f"{self.index}. {content}\n"

class List(Element):
	def __init__(self, ordered_index: int):
		super().__init__()
		self.ordered_index = ordered_index
	def addChild(self, child: ListItem):
		if not hasattr(child, "set_index"):
			if not hasattr(child, "text") or child.text != "\n":
				print(f"ERR: element inside list is not a list item: {str(child)}")
			return

		if self.ordered_index is None:
			child.set_index(-1)
		else:
			child.set_index(self.ordered_index + len(self.children))

		self.children.append(child)

	def __repr__(self):
		return f"{{List, ordered_index={self.ordered_index}, {super().__repr__()}}}"
	def markdown(self):
		return f"{super().markdown()}\n"

class Aside(Element):
	def __init__(self, attribute: str):
		super().__init__()
		self.attribute = attribute

	def __repr__(self):
		return f"{{Aside, {self.attribute}, {super().__repr__()}}}"
	def markdown(self):
		content = super().markdown().replace("\n", "\n> ")
		re.sub(r"^[\s\>]+", "\n> ", content)
		return content + "\n\n"

class Bold(Element):
	def __repr__(self):
		return f"{{Bold, {super().__repr__()}}}"
	def markdown(self):
		return f"<strong>{super().markdown()}</strong>"

class Italic(Element):
	def __repr__(self):
		return f"{{Italic, {super().__repr__()}}}"
	def markdown(self):
		return f"<em>{super().markdown()}</em>"

class Underline(Element):
	def __repr__(self):
		return f"{{Underline, {super().__repr__()}}}"
	def markdown(self):
		return f"<ins>{super().markdown()}</ins>"

class Strikethrough(Element):
	def __repr__(self):
		return f"{{Strikethrough, {super().__repr__()}}}"
	def markdown(self):
		return f"<del>{super().markdown()}</del>"

class Image(Element):
	def __init__(self, url: str, width: int, description: str):
		self.url = url
		self.width = width
		self.description = description

	def __repr__(self):
		return f"{{Image, {self.url}, width={self.width}, \"{self.description}\"}}"
	def markdown(self):
		res = f"<p align=\"center\"><img src=\"{self.url}\""
		if self.width is not None:
			res += f" width=\"{self.width}px\""
		if self.description is not None:
			res += f" alt=\"{self.description}\""
		return res + f"></p>"

class Monospace(Element):
	def __repr__(self):
		return f"{{Monospace, {super().__repr__()}}}"
	def markdown(self):
		return f"`{super().markdown()}`"

class Code(Element):
	def __init__(self, html: Html):
		self.html = html

	def __repr__(self):
		return f"{{Code, \"{self.html.text}\"}}"
	def markdown(self):
		code = self.html.text
		language = detectLanguage(code)
		return f"```{language}\n{code}\n```\n"


class CodelabExtractor:
	@classmethod
	def setup_func_table(cls):
		cls.func_table = {
			'google-codelab-step': cls.step,
			'p': cls.p,
			'a': cls.a,
			'h1': cls.h,
			'h2': cls.h,
			'h3': cls.h,
			'h4': cls.h,
			'h5': cls.h,
			'h6': cls.h,
			'ol': cls.ol,
			'ul': cls.ul,
			'li': cls.li,
			'aside': cls.aside,
			'b': cls.bold,
			'strong': cls.bold,
			'i': cls.italic,
			'em': cls.italic,
			'u': cls.underline,
			'ins': cls.underline,
			'strike': cls.strikethrough,
			'del': cls.strikethrough,
			'paper-button': cls.element,
			'img': cls.img,
			'tt': cls.monospace,
			'code': cls.monospace,
			'kbd': cls.monospace,
			'var': cls.monospace,
			'samp': cls.monospace,
			'pre': cls.pre,
			'br': cls.br,
		}

	@classmethod
	def get_all_codelabs(cls, url_first_codelab: str):
		last_url = url_first_codelab
		codelabs = []
		while last_url is not None:
			print("Extracting", last_url)
			codelab = cls(last_url)
			codelabs.append(codelab)
			last_url = codelab.next_url
		return codelabs


	def __init__(self, url: str):
		html = getPageHtml(url)
		codelab = html.body.find('google-codelab')
		self.extract_base_url(codelab, url)

		self.extract_steps(codelab)
		self.extract_metadata(codelab)


	def __repr__(self):
		return (f"Codelab \"{self.title}\":\n" +
			"\n".join([repr(step) for step in self.steps]))

	def markdown_pages(self):
		titlePage = f"# {self.title}\n"
		if self.next_url is not None:
			titlePage += f"\nNext: [{self.next_title}]({self.next_url})\n"
		if self.other_url is not None:
			titlePage += f"\n[{self.other_title}]({self.other_url})\n"

		stepPages = [step.markdown() for step in
			self.steps[:(None if self.next_url is None else -1)]]
		return [titlePage] + stepPages


	def extract_base_url(self, codelab: Html, url: str):
		self.base_url = url[0:url.rfind("/")+1]
		codelab_id = codelab["id"]

		if codelab_id not in self.base_url:
			self.base_url += codelab_id + "/"

	def extract_steps(self, codelab: Html):
		stepsHtml = codelab.find_all('google-codelab-step')
		self.steps = []
		for i in range(len(stepsHtml)):
			self.steps.append(self.step(stepsHtml[i], i+1))

	def extract_metadata(self, codelab: Html):
		self.title = codelab['title']

		lastStep = codelab.find_all('google-codelab-step')[-1]
		try:
			pars = lastStep.find_all('p')
			self.next_url = pars[0].find('a')["href"]
			self.next_title = pars[0].find('a').find("paper-button").text

			try:
				self.other_url = pars[1].find('a')["href"]
				if self.other_url == self.next_url: raise Exception()
				self.other_title = pars[1].find('a').text
			except:
				self.other_title = None
				self.other_url = None
		except:
			self.next_title = None
			self.next_url = None
			self.other_title = None
			self.other_url = None


	def parse_element(self, obj: Html) -> Element:
		if isinstance(obj, NavigableString):
			return Text(obj.string)
		if obj is None or obj.name is None:
			return None

		if obj.name in self.func_table:
			return self.func_table[obj.name](self, obj)
		else:
			print(f"ERR: unknown html element: {obj.name}")
			return None

	def propagate(self, obj: Html, parent: Element) -> Element:
		for childHtml in obj.contents:
			child = self.parse_element(childHtml)
			if child is not None:
				parent.addChild(child)
		return parent


	def element(self, obj: Html) -> Element:
		return self.propagate(obj, Element())

	def step(self, obj: Html, index: int) -> Element:
		return self.propagate(obj, Step(obj['label'], index))

	def p(self, obj: Html) -> Paragraph:
		classAttr = optionalGet(obj, "class")
		if classAttr is not None and "image-container" in classAttr:
			return self.img(obj.find("img"))

		return self.propagate(obj, Paragraph())

	def h(self, obj: Html) -> Header:
		return self.propagate(obj, Header(int(obj.name[1])))

	def a(self, obj: Html) -> Link:
		return self.propagate(obj, Link(obj['href']))

	def ol(self, obj: Html) -> List:
		try:
			return self.propagate(obj, List(int(obj["start"])))
		except:
			return self.propagate(obj, List(1))

	def ul(self, obj: Html) -> List:
		return self.propagate(obj, List(None))

	def li(self, obj: Html) -> ListItem:
		return self.propagate(obj, ListItem())

	def aside(self, obj: Html) -> Aside:
		return self.propagate(obj, Aside(obj['class']))

	def bold(self, obj: Html) -> Bold:
		return self.propagate(obj, Bold())

	def italic(self, obj: Html) -> Italic:
		return self.propagate(obj, Italic())

	def underline(self, obj: Html) -> Underline:
		return self.propagate(obj, Underline())

	def strikethrough(self, obj: Html) -> Strikethrough:
		return self.propagate(obj, Strikethrough())

	def img(self, obj: Html) -> Image:
		return Image(
			self.base_url + obj["src"],
			firstMatchRegex(optionalGet(obj, "style"), r"width\: ((?:[0-9]*\.)?[0-9]+)px"),
			optionalGet(obj, "alt"))

	def monospace(self, obj: Html) -> Monospace:
		return self.propagate(obj, Monospace())

	def pre(self, obj: Html) -> Code:
		return Code(obj)

	def br(self, obj: Html) -> Text:
		return Text("\n")

CodelabExtractor.setup_func_table()


def savePageToFile(filename, url):
	with open(filename, "wb") as f:
		f.write(urlopen(url).read())

if __name__ == "__main__":
	url = input("Url of first codelab: ")
	default_code_language = input("Default programming language covered in the codelab (java/kotlin): ")
	output_directory = input("Output directory: ")
	language = input("Language of output (md/repr): ")

	os.makedirs(output_directory, exist_ok=True)
	def open_file(filename: str):
		return open(os.path.join(output_directory, filename), "w")

	detectLanguage.default_language = default_code_language
	codelabs = CodelabExtractor.get_all_codelabs(url)

	if   language == "repr":
		for i in range(len(codelabs)):
			with open_file(f"{i}.txt") as f:
				f.write(repr(codelabs[i]))
	elif language == "md":
		for i in range(len(codelabs)):
			with open_file(f"{i}.md") as f:
				f.write("\n<div style=\"page-break-after: always; visibility: hidden\">\n\\pagebreak\n</div>\n\n".join(codelabs[i].markdown_pages()))
