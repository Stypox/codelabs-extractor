from .codelab_extractor import CodelabExtractor
from .utils import commonStartingSubstring

class CourseExtractor:

	def __init__(self, url_first_codelab: str, default_code_language: str):
		self.extract_all_codelabs(url_first_codelab, default_code_language)


	def __repr__(self):
		return (f"Course {self.id} \"{self.title}\":\n" +
			"\n".join([repr(c) for c in self.codelabs]))


	def extract_all_codelabs(self, url_first_codelab: str, default_code_language: str):
		last_url = url_first_codelab
		all_codelab_ids = []
		self.codelabs = []

		while last_url is not None:
			print("Downloading", last_url)
			codelab = CodelabExtractor(last_url, default_code_language)
			self.codelabs.append(codelab)

			last_url = codelab.next_url
			all_codelab_ids.append(codelab.id)

		print(all_codelab_ids)
		for codelab in self.codelabs:
			print("Extracting", codelab.title)
			codelab.extract_steps(all_codelab_ids)

	def extract_metadata(self):
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
				self.id = commonStartingSubstring(self.codelabs[-2].id, self.codelabs[-3].id)
				self.title = commonStartingSubstring(self.codelabs[-2].title, self.codelabs[-3].title)

			self.id = self.id.strip()
			self.title = self.title.strip()

			if self.id == "":
				self.id = self.codelabs[0].id.strip()
			if self.title == "":
				self.title = self.codelabs[0].title.strip()
