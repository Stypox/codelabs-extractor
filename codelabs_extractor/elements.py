from bs4 import BeautifulSoup as Html
from .utils import detectLanguage
import re

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
		return res + f"></p>\n"

class Monospace(Element):
	def __repr__(self):
		return f"{{Monospace, {super().__repr__()}}}"
	def markdown(self):
		return f"<code>{super().markdown()}</code>"

class Code(Element):
	def __init__(self, html: Html, default_code_language: str):
		self.html = html
		self.default_code_language = default_code_language

	def __repr__(self):
		return f"{{Code, \"{self.html.text}\"}}"
	def markdown(self):
		code = self.html.text
		language = detectLanguage(code, self.default_code_language)
		return f"```{language}\n{code}\n```\n"

class Table(Element):
	def __repr__(self):
		return f"{{Table, {super().__repr__()}}}"
	def markdown(self):
		return f"<table>{super().markdown()}</table>\n"

class TableRow(Element):
	def __repr__(self):
		return f"{{TableRow, {super().__repr__()}}}"
	def markdown(self):
		return f"<tr>{super().markdown()}</tr>\n"

class TableCell(Element):
	def __repr__(self):
		return f"{{TableCell, {super().__repr__()}}}"
	def markdown(self):
		return f"<td>{super().markdown()}</td>\n"
