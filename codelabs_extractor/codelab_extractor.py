from bs4 import BeautifulSoup as Html
from bs4.element import NavigableString
from .utils import *
from .elements import *
import re
import os


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
