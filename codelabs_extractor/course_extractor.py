from .codelab_extractor import CodelabExtractor
from .utils import commonStartingSubstring, extractHost
import os

class CourseExtractor:

	def __init__(self, url_first_codelab: str, default_code_language: str):
		self.url_first_codelab = url_first_codelab
		self.default_code_language = default_code_language
		self.download_all_codelabs()
		self.extract_metadata()
		self.extract_all_codelabs()


	def __repr__(self):
		return (f"Course {self.id} \"{self.title}\":\n" +
			"\n".join([repr(c) for c in self.codelabs]))

	def pandoc(self, directory: str):
		os.makedirs(directory, exist_ok=True)
		def open_in_directory(filename: str):
			return open(os.path.join(directory, filename), "w")

		for i in range(len(self.codelabs)):
			with open_in_directory(f"{i}.md") as f:
				f.write(self.codelabs[i].pandoc())

		with open_in_directory("title.txt") as f:
			f.write("---\n")
			if self.title is not None or self.id is not None:
				f.write("title:\n")
			if self.title is not None:
				f.write(f"- type: main\n  text: {self.title}\n")
			if self.id is not None:
				f.write(f"- type: subtitle\n  text: {self.id}\n")

			f.write("creator:\n")
			f.write(f"- role: author\n  text: {self.host}\n")
			f.write(f"- role: trc\n  text: Codelabs Extractor by Stypox\n")
			f.write("...\n")


	def download_all_codelabs(self):
		last_url = self.url_first_codelab
		self.all_codelab_ids = []
		self.codelabs = []

		while last_url is not None:
			print("Downloading", last_url)
			codelab = CodelabExtractor(last_url, self.default_code_language)
			self.codelabs.append(codelab)

			last_url = codelab.next_url
			self.all_codelab_ids.append(codelab.id)

	def extract_metadata(self):
		self.host = extractHost(self.url_first_codelab)

		codelabCount = len(self.codelabs)
		if codelabCount == 0:
			self.id = None
			self.title = None
		else:
			if codelabCount == 1:
				self.id = self.codelabs[0].id
				self.title = self.codelabs[0].title
			elif codelabCount == 2:
				self.id = commonStartingSubstring(self.codelabs[0].id, self.codelabs[1].id)
				self.title = commonStartingSubstring(self.codelabs[0].title, self.codelabs[1].title)
			else:
				self.id = commonStartingSubstring(self.codelabs[1].id, self.codelabs[2].id)
				self.title = commonStartingSubstring(self.codelabs[1].title, self.codelabs[2].title)

			self.id = self.id.strip()
			self.title = self.title.strip()

			if self.id == "":
				self.id = self.codelabs[0].id.strip()
			if self.title == "":
				self.title = self.codelabs[0].title.strip()

	def extract_all_codelabs(self):
		for codelab in self.codelabs:
			print("Extracting", codelab.title)
			codelab.extract_steps(self.all_codelab_ids)
