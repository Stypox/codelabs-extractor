from bs4 import BeautifulSoup as Html
from bs4.element import NavigableString
from .utils import getPageHtml, firstMatchRegex, optionalGet
from .elements import *
import re
import os

MARKDOWN_LINE_BREAK = "\n<div style=\"page-break-after: always; visibility: hidden\">\n\\pagebreak\n</div>\n\n"

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
			'li': cls.default_behaviour(ListItem),
			'aside': cls.aside,
			'b': cls.default_behaviour(Bold),
			'strong': cls.default_behaviour(Bold),
			'i': cls.default_behaviour(Italic),
			'em': cls.default_behaviour(Italic),
			'u': cls.default_behaviour(Underline),
			'ins': cls.default_behaviour(Underline),
			'strike': cls.default_behaviour(Strikethrough),
			'del': cls.default_behaviour(Strikethrough),
			'paper-button': cls.default_behaviour(Element),
			'img': cls.img,
			'tt': cls.default_behaviour(Monospace),
			'code': cls.default_behaviour(Monospace),
			'kbd': cls.default_behaviour(Monospace),
			'var': cls.default_behaviour(Monospace),
			'samp': cls.default_behaviour(Monospace),
			'pre': cls.pre,
			'br': cls.br,
			'table': cls.default_behaviour(Table),
			'tr': cls.default_behaviour(TableRow),
			'td': cls.default_behaviour(TableCell),
			'th': cls.default_behaviour(TableCell),
			'tbody': cls.default_behaviour(Element),
			'thead': cls.default_behaviour(Element),
			'tfoot': cls.default_behaviour(Element),
		}

	@classmethod
	def default_behaviour(cls, element_class):
		def func(self: cls, obj: Html) -> element_class:
			return self.propagate(obj, element_class())
		return func


	def __init__(self, url: str, default_code_language: str, cache_pages_directory: str):
		self.default_code_language = default_code_language
		html = getPageHtml(url, cache_pages_directory)
		self.codelabHtml = html.body.find('google-codelab')

		self.extract_base_url(url)
		self.extract_metadata()


	def __repr__(self):
		return (f"Codelab {self.id} \"{self.title}\" chapter {self.chapter}:\n" +
			"\n".join([repr(step) for step in self.steps]))

	def markdown_pages(self) -> list:
		titlePage = f"# {self.chapter} {self.short_title}\n"
		if self.chapter is not None:
			titlePage += f"\nFull title: {self.title}\n"
		if self.next_url is not None:
			titlePage += self.steps[-1].markdown_without_title()

		stepPages = [step.markdown() for step in
			self.steps[:(None if self.next_url is None else -1)]]
		return [titlePage] + stepPages

	def pandoc(self) -> str:
		return (f"# {self.chapter} {self.short_title}\n"
			+ "\n".join([step.pandoc() for step in self.steps]))


	def extract_base_url(self, url: str):
		self.base_url = url[0:url.rfind("/")+1]
		self.id = self.codelabHtml["id"]

		if self.id not in self.base_url:
			self.base_url += self.id + "/"

	def extract_metadata(self):
		self.title = self.codelabHtml['title']
		self.chapter = firstMatchRegex(self.title, r"0*([1-9]+\.[0-9]+)")
		self.short_title = firstMatchRegex(self.title, r"\:(.+)$").strip()

		lastStep = self.codelabHtml.find_all('google-codelab-step')[-1]
		try:
			pars = lastStep.find_all('p')
			self.next_url = pars[0].find('a')["href"]
			self.next_title = pars[0].find('a').find("paper-button").text
		except:
			self.next_title = None
			self.next_url = None

	def extract_steps(self, all_codelab_ids: list):
		stepsHtml = self.codelabHtml.find_all('google-codelab-step')
		self.steps = []
		self.all_codelab_ids = all_codelab_ids

		for i in range(len(stepsHtml)):
			self.steps.append(self.step(stepsHtml[i], i+1))


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


	def step(self, obj: Html, index: int) -> Element:
		return self.propagate(obj, Step(obj['label'], index))

	def p(self, obj: Html) -> Paragraph:
		classAttr = optionalGet(obj, "class")
		if classAttr is not None and "image-container" in classAttr:
			return self.propagate(obj, Paragraph("center"))

		return self.propagate(obj, Paragraph(None))

	def h(self, obj: Html) -> Header:
		return self.propagate(obj, Header(int(obj.name[1])))

	def a(self, obj: Html) -> Link:
		link = obj['href']
		i = 0
		for id in self.all_codelab_ids:
			if id in link:
				return self.propagate(obj, Reference(i))
			i += 1

		return self.propagate(obj, Link(link))

	def ol(self, obj: Html) -> List:
		try:
			return self.propagate(obj, List(int(obj["start"])))
		except:
			return self.propagate(obj, List(1))

	def ul(self, obj: Html) -> List:
		return self.propagate(obj, List(None))

	def aside(self, obj: Html) -> Aside:
		return self.propagate(obj, Aside(obj['class']))

	def img(self, obj: Html) -> Image:
		src = obj["src"]
		if src.startswith("http") or src.startswith("www"):
			url = src
		else:
			url = self.base_url + src

		return Image(
			url,
			firstMatchRegex(optionalGet(obj, "style"), r"width\: ((?:[0-9]*\.)?[0-9]+)px"),
			optionalGet(obj, "alt"))

	def pre(self, obj: Html) -> Code:
		return Code(obj, self.default_code_language)

	def br(self, obj: Html) -> Text:
		return Text("\n")

CodelabExtractor.setup_func_table()
