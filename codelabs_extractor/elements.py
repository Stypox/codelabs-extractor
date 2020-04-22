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
	def html(self):
		return "".join([c.html() for c in self.children])
	def pandoc(self):
		return "".join([c.pandoc() for c in self.children])

class Text(Element):
	def __init__(self, text: str):
		self.text = text

	def __repr__(self):
		return f"{{Text, \"{self.text}\"}}"
	def markdown(self):
		return self.text
	def html(self):
		return self.text
	def pandoc(self):
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
	def html(self):
		return f"<h1>{self.index}. {self.label}</h1>{super().html()}"
	def pandoc(self):
		return f"<h1>{self.index}. {self.label}</h1>{super().pandoc()}"

class Paragraph(Element):
	def __init__(self, align):
		super().__init__()
		self.align = align

	def __repr__(self):
		return f"{{Paragraph, self.align, {super().__repr__()}}}"
	def markdown(self):
		if self.align is None:
			return f"\n{super().markdown()}\n"
		return f"<p align=\"{self.align}\">{super().markdown()}</p>\n"
	def html(self):
		if self.align is None:
			return f"<p>{super().html()}</p>"
		return f"<p align=\"{self.align}\">{super().html()}</p>\n"
	def pandoc(self):
		if self.align is None:
			return f"\n{super().pandoc()}\n"
		return f"<p align=\"{self.align}\">{super().pandoc()}</p>\n"

class Header(Element):
	def __init__(self, size: int):
		super().__init__()
		self.size = size

	def __repr__(self):
		return f"{{Header, size={self.size}, {super().__repr__()}}}"
	def markdown(self):
		return f"{'#'*self.size} {super().markdown()}\n"
	def html(self):
		return f"<h{self.size}>{super().html()}</h{self.size}>"
	def pandoc(self):
		return f"{'#'*(self.size+1)} {super().pandoc()}\n"

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
	def html(self):
		content = super().html()
		if content.strip() == "":
			content = self.link
		return f"<a href=\"{self.link}\">{content}</a>"
	def pandoc(self):
		content = super().pandoc()
		if content.strip() == "":
			content = self.link
		return f"<a href=\"{self.link}\">{content}</a>"

class Reference(Element):
	def __init__(self, codelab_index: int):
		super().__init__()
		self.codelab_index = codelab_index

	def __repr__(self):
		return f"{{Reference, codelab_index={self.codelab_index}, {super().__repr__()}}}"
	def markdown(self):
		link = f"./{self.codelab_index}.md"
		content = super().markdown()
		if content.strip() == "":
			content = link
		return f"[{content}]({link})"
	def html(self):
		link = f"./{self.codelab_index}.html"
		content = super().html()
		if content.strip() == "":
			content = link[2:]
		return f"<a href=\"{link}\">{content}</a>"
	def pandoc(self):
		link = f"./ch{self.codelab_index:>03}.xhtml"
		content = super().markdown()
		if content.strip() == "":
			content = link[2:]
		return f"[{content}]({link})"


class ListItem(Element):
	def __init__(self):
		super().__init__()
	def set_index(self, index):
		self.index = index

	def __repr__(self):
		return f"{{ListItem, index={self.index}, {super().__repr__()}}}"
	def markdown(self):
		content = super().markdown().replace("\n", "<br>")
		if self.index == -1:
			return f"- {content}\n"
		else:
			return f"{self.index}. {content}\n"
	def html(self):
		return f"<li>{super().html()}</li>"
	def pandoc(self):
		content = super().pandoc().replace("\n", "<br>")
		if self.index == -1:
			return f"- {content}\n"
		else:
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
	def html(self):
		if self.ordered_index is None:
			return f"<ul>{super().markdown()}</ul>"
		else:
			return f"<ol start=\"{self.ordered_index}\">{super().html()}</ol>"
	def pandoc(self):
		return f"{super().pandoc()}\n"

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
	def html(self):
		return f"<aside>{super().html()}</aside>"
	def pandoc(self):
		return f"<aside>{super().html()}</aside>\n" # TODO add background color

class Bold(Element):
	def __repr__(self):
		return f"{{Bold, {super().__repr__()}}}"
	def markdown(self):
		return f"<strong>{super().markdown()}</strong>"
	def html(self):
		return f"<strong>{super().html()}</strong>"
	def pandoc(self):
		return f"<strong>{super().pandoc()}</strong>"

class Italic(Element):
	def __repr__(self):
		return f"{{Italic, {super().__repr__()}}}"
	def markdown(self):
		return f"<em>{super().markdown()}</em>"
	def html(self):
		return f"<em>{super().html()}</em>"
	def pandoc(self):
		return f"<em>{super().pandoc()}</em>"

class Underline(Element):
	def __repr__(self):
		return f"{{Underline, {super().__repr__()}}}"
	def markdown(self):
		return f"<ins>{super().markdown()}</ins>"
	def html(self):
		return f"<ins>{super().html()}</ins>"
	def pandoc(self):
		return f"<ins>{super().pandoc()}</ins>"

class Strikethrough(Element):
	def __repr__(self):
		return f"{{Strikethrough, {super().__repr__()}}}"
	def markdown(self):
		return f"<del>{super().markdown()}</del>"
	def html(self):
		return f"<del>{super().html()}</del>"
	def pandoc(self):
		return f"<del>{super().pandoc()}</del>"

class Image(Element):
	def __init__(self, url: str, width: int, description: str):
		self.url = url
		self.width = width
		self.description = description

	def __repr__(self):
		return f"{{Image, {self.url}, width={self.width}, \"{self.description}\"}}"
	def markdown(self):
		res = f"<img src=\"{self.url}\""
		if self.width is not None:
			res += f" width=\"{self.width}px\""
		if self.description is not None:
			res += f" alt=\"{self.description}\""
		return res + f">"
	def html(self):
		return self.markdown()
	def pandoc(self):
		return self.markdown() # TODO download images and replace urls

class Monospace(Element):
	def __repr__(self):
		return f"{{Monospace, {super().__repr__()}}}"
	def markdown(self):
		return f"<code>{super().markdown()}</code>"
	def html(self):
		return f"<code>{super().html()}</code>"
	def pandoc(self):
		return f"<code>{super().pandoc()}</code>"

class Code(Element):
	def __init__(self, htmlText: Html, default_code_language: str):
		self.htmlText = htmlText
		self.default_code_language = default_code_language

	def __repr__(self):
		return f"{{Code, \"{self.htmlText.text}\"}}"
	def markdown(self):
		code = self.htmlText.text
		language = detectLanguage(code, self.default_code_language)
		return f"```{language}\n{code}\n```\n"
	def html(self):
		return repr(self.html)

class Table(Element):
	def __repr__(self):
		return f"{{Table, {super().__repr__()}}}"
	def markdown(self):
		return f"<table>{super().markdown()}</table>\n"
	def html(self):
		return f"<table>{super().html()}</table>"
	def pandoc(self):
		return f"<table>{super().pandoc()}</table>\n"

class TableRow(Element):
	def __repr__(self):
		return f"{{TableRow, {super().__repr__()}}}"
	def markdown(self):
		return f"<tr>{super().markdown()}</tr>\n"
	def html(self):
		return f"<tr>{super().html()}</tr>"
	def pandoc(self):
		return f"<tr>{super().pandoc()}</tr>\n"

class TableCell(Element):
	def __repr__(self):
		return f"{{TableCell, {super().__repr__()}}}"
	def markdown(self):
		return f"<td>{super().markdown()}</td>\n"
	def html(self):
		return f"<td>{super().html()}</td>"
	def pandoc(self):
		return f"<td>{super().pandoc()}</td>\n"
