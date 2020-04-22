# Google Codelabs course extractor

This tool extracts data from a Google Codelab course (e.g. [this one](https://codelabs.developers.google.com/codelabs/kotlin-android-training-welcome/index.html?index=..%2F..android-kotlin-fundamentals#0)) and exports it into various offline formats (currently html, markdown and pandoc-markdown). This enables to build an ebook in many formats (using for example [pandoc](https://pandoc.org/)) that can then be used on any device, without internet connection and without formatting issues.

## Usage

This tools requires python3.7+. Using `cd` head over to the root directory of this project and type `python3 -m codelabs_extractor` to run it. By appending `--help` to the previous command you will get this help screen:
```man
usage: __main__.py [-h] -c URL -o DIR -f FMT [-l LANG]

Extracts data from a Google Codelab course and save it into various formats

optional arguments:
  -h, --help            show this help message and exit
  -c URL, --course URL  Url to the first Codelab of the course
  -o DIR, --output-directory DIR
                        Output directory in which to save all generated files
  -f FMT, --format FMT  The format of the output. Supported FMT values: repr,
                        md, html, pandoc
  -l LANG, --language LANG
                        The programming language used in the course, to use
                        with code blocks whose language could not be
                        automatically detected. Supported LANG values: java,
                        kotlin (and the others supported by Markdown).
                        Defaults to an empty string (i.e. no syntax
                        highlighting).
```

Example usage for [this](https://codelabs.developers.google.com/codelabs/kotlin-android-training-welcome) codelab:
```
python3 -m codelabs_extractor --course https://codelabs.developers.google.com/codelabs/kotlin-android-training-welcome/index.html#0 --output-directory AndroidKotlinFundamentals --format pandoc --language kotlin
```