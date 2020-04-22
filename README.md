# Google Codelabs course extractor

This tool extracts data from a Google Codelab course (e.g. [this one](https://codelabs.developers.google.com/codelabs/kotlin-android-training-welcome/index.html?index=..%2F..android-kotlin-fundamentals#0)) and exports it into various offline formats (currently html, markdown and pandoc-markdown). This enables to build an ebook in many formats (using for example [pandoc](https://pandoc.org/)) that can then be used on any device, without internet connection and without formatting issues.

## Usage

This tools requires [Python 3.7+](https://www.python.org/downloads/). To convert the generated markdown files into ebooks [pandoc](https://pandoc.org/installing.html) is also required.
<br>Using `cd` head over to the root directory of this project and type `python3 -m codelabs_extractor` to run it. By appending `--help` to the previous command you will get this help screen:
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
If the provided output format was `pandoc`, when the script has done downloading, extracting and exporting, it provides the pandoc command to use in order to create an ebook (or other things supported by pandoc). This is an example for the above command:
```
pandoc --verbose -o OUTPUT_FILE KotlinAndroidFundamentals/title.txt KotlinAndroidFundamentals/0.md KotlinAndroidFundamentals/1.md KotlinAndroidFundamentals/2.md KotlinAndroidFundamentals/3.md KotlinAndroidFundamentals/4.md KotlinAndroidFundamentals/5.md KotlinAndroidFundamentals/6.md KotlinAndroidFundamentals/7.md KotlinAndroidFundamentals/8.md KotlinAndroidFundamentals/9.md KotlinAndroidFundamentals/10.md KotlinAndroidFundamentals/11.md KotlinAndroidFundamentals/12.md KotlinAndroidFundamentals/13.md KotlinAndroidFundamentals/14.md KotlinAndroidFundamentals/15.md KotlinAndroidFundamentals/16.md KotlinAndroidFundamentals/17.md KotlinAndroidFundamentals/18.md KotlinAndroidFundamentals/19.md KotlinAndroidFundamentals/20.md KotlinAndroidFundamentals/21.md KotlinAndroidFundamentals/22.md KotlinAndroidFundamentals/23.md KotlinAndroidFundamentals/24.md KotlinAndroidFundamentals/25.md KotlinAndroidFundamentals/26.md KotlinAndroidFundamentals/27.md KotlinAndroidFundamentals/28.md KotlinAndroidFundamentals/29.md KotlinAndroidFundamentals/30.md KotlinAndroidFundamentals/31.md KotlinAndroidFundamentals/32.md KotlinAndroidFundamentals/33.md KotlinAndroidFundamentals/34.md
```
Just replace `OUTPUT_FILE` with the name of the ebook you want to produce (e.g. `AndroidKotlinFundamentals.epub`) and pandoc will take care of the rest of the work!