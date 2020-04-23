from .course_extractor import CourseExtractor
from .codelab_extractor import MARKDOWN_LINE_BREAK
from .utils import detectLanguage
import re
import os
import argparse

def parseArgs(namespace):
	argParser = argparse.ArgumentParser(fromfile_prefix_chars="@",
		description="Extracts data from a Google Codelab course and save it into various formats")

	argParser.add_argument_group("Default options")
	argParser.add_argument("-c", "--course", type=str, required=True, metavar="URL",
		help="Url to the first Codelab of the course")
	argParser.add_argument("-o", "--output-directory", type=str, required=True, metavar="DIR",
		help="Output directory in which to save all generated files")
	argParser.add_argument("-f", "--format", type=str, required=True, metavar="FMT",
		help="The format of the output. Supported FMT values: repr, md, html, pandoc")
	argParser.add_argument("-l", "--language", type=str, default="", metavar="LANG",
		help="The programming language used in the course,"
		+ " to use with code blocks whose language could not be automatically detected."
		+ " Supported LANG values: java, kotlin (and the others supported by Markdown)."
		+ " Defaults to an empty string (i.e. no syntax highlighting).")

	argParser.add_argument_group("Debugging-related options")
	argParser.add_argument("--count", type=int, required=False, metavar="N",
		help="Limit the count of extracted codelabs to the first N")
	argParser.add_argument("--cache-pages", action="store_true",
		help="Save downloaded pages to html files or load from them if they already exist")

	argParser.parse_args(namespace=namespace)

	if namespace.count is None:
		namespace.count = 999999 # infinity

def main():
	class Args: pass
	parseArgs(Args)

	course = CourseExtractor(Args.course, Args.language, Args.count,
		Args.output_directory if Args.cache_pages else None)

	if Args.format == "pandoc":
		course.pandoc(Args.output_directory)
	else:
		os.makedirs(Args.output_directory, exist_ok=True)
		def open_file(filename: str):
			return open(os.path.join(Args.output_directory, filename), "w")

		if   Args.format == "repr":
			for i in range(len(course.codelabs)):
				with open_file(f"{i}.txt") as f:
					f.write(repr(course.codelabs[i]))
		elif Args.format == "md":
			for i in range(len(course.codelabs)):
				with open_file(f"{i}.md") as f:
					f.write(MARKDOWN_LINE_BREAK.join(course.codelabs[i].markdown_pages()))
		else:
			print(f"ERR: unknown format {Args.format}")

if __name__ == "__main__":
	main()