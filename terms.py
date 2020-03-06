"""Create a new file with a random permutation of lines from a
text file with content from a variety of terms/privacy/data policy-type
web pages and a text file with poetry, with options to set a max number
of lines, set a max number of words per line, and use only unique lines.

Help: python3 terms.py --help

Example usage:

Generate a file of 10 lines, 8 words max per line, with unique lines in
idiosyncratic stanza groupings, from privacy.txt and poetry.txt:
    python3 terms.py -ml 10 -mw 8 -u

Get text from a (policy-type) web page, append to privacy.txt, and then do the
same as the example above:
    python3 terms.py -ml 10 -mw 8 -u -prurl "https://help.netflix.com/legal/privacy"

Generate a file of 5 lines, 8 words max per line, with unique lines in a
single stanza, from privacy.txt and poetry.txt:
    python3 terms.py -ml 5 -mw 8 -u -ns
"""

import argparse
import html2text
import os
import re
import random
import requests
from time import gmtime, strftime


parser = argparse.ArgumentParser(
    description = """Create a new file with a random permutation of lines from
    a text file with content from a variety of terms/privacy/data policy-type
    web pages and a text file with poetry, with options to set a max number
    of lines, set a max number of words per line, and use only unique lines."""
)
parser.add_argument(
    "-prurl",
    "--privacy_url",
    help = """URL of a terms/privacy/data policy-type webpage. Use this flag
    to append the page's content to the source privacy text file before
    generating the new file."""
)
parser.add_argument(
    "-prf",
    "--privacy_source",
    help = "Source privacy text file.",
    default = "source/privacy.txt"
)
parser.add_argument(
    "-pof",
    "--poetry_source",
    help = "Source poetry text file.",
    default = "source/poetry.txt"
)
parser.add_argument(
    "-d",
    "--new_poem_dir",
    help = "Path to the directory where the new poem will be created.",
    default = "generated_files"
)
parser.add_argument(
    "-u",
    "--unique_lines",
    action = "store_true",
    help = "Use each unique line from the source texts only once."
)
parser.add_argument(
    "-ml",
    "--max_lines",
    type = int,
    help = "Max number of lines in the new poem."
)
parser.add_argument(
    "-mw",
    "--max_words_per_line",
    type = int,
    help= """Max number of words per line in the new poem, retaining words from the
    start, middle, or end of the line.""",
    default = 8
)
parser.add_argument(
    "-ns",
    "--no_stanzas",
    action = "store_true",
    help = "Do not break lines into stanza. Default is idiosyncractic stanazs."
)
args = parser.parse_args()


poetry = open(args.poetry_source).readlines()
privacy = open(args.privacy_source).readlines()
lines_seen = set()
total_lines = 0
pattern = ""


def capture_policy(url):
    """
    Get html from a webpage, convert it to markdown, and append it
    to the privacy source text file.

    Arguments:
    url -- the URL of the webpage
    """
    t_maker = html2text.HTML2Text()
    t_maker.ignore_links = True
    t_maker.ignore_images = True
    t_maker.ignore_emphasis = True
    html = requests.get(url)
    text = t_maker.handle(html.text)
    privacy_source = open(args.privacy_source, "a")
    privacy_source.write(text)


def choose_line(text):
    """
    Choose a random line from the privay text, or choose a line from
    the poetry text the includes the last three characters of the last
    word of the previously chosen line from the privay text.

    Arguments:
    text -- the source text
    """
    global poetry
    global privacy
    global lines_seen
    global pattern
    line = random.choice(text)
    if text == poetry:
        if pattern is not "":
            for l in text:
                if re.search(pattern, l) is not None:
                    line = l
                    continue
    text.remove(line)
    if len(line) > 0:
        if line.isupper():
            line = line.lower()
        # If line contains multiple sentences, randomly choose one
        # and remove extra spaces and punction.
        line = random.choice(line.split('.'))
        line = re.sub(r"[^\w\'\-\s]", "", line).strip()
        # print(line)
        # If the line exceeds --max_words_from_line, randomly choose the
        # specified num of words from the start, middle, or end of the line.
        words_removed = 0
        if text == privacy:
            if args.max_words_per_line:
                if len(line.split()) > args.max_words_per_line:
                    words_removed = len(line.split()) - args.max_words_per_line
                    start = ' '.join(line.split(' ')[:-words_removed])
                    middle = ' '.join(line.split(' ')[(words_removed // 2):-(words_removed // 2)])
                    end = ' '.join(line.split(' ')[words_removed:])
                    line = random.choice([start, middle, end]).strip()
            pattern = line[-3:]
        # If --unique_lines is set, check if the line was seen in a previous
        # iteration. If not, write the line to new_poem and add it to lines_seen.
        if args.unique_lines:
            if line.lower() in lines_seen:
                return
            lines_seen.add(line.lower())
        if line.isspace() or len(line) < 1:
            print("Skip empty line\n")
            return
        if not line.isascii():
            print("Skip non-ascii line\n")
            return
        write_line(line, text, words_removed)


def write_line(line, text, words_removed):
    """
    Write a line to a file and possibly write 1-4 empty lines.

    Arguments:
    line -- the line to write to the file
    """
    global total_lines
    global pattern
    new_poem.write(line + "\n")
    total_lines += 1
    print(total_lines, "/", args.max_lines)
    print(line)
    if text == privacy:
        print("Text: privacy")
    else:
        print("Text: poetry")
        print("Pattern: ", pattern)
        # pattern = ""
    print("Words removed: ", str(words_removed), "\n")
    # Unless --no_stanzas is set, radomly write 0, 1, 2, 3, or 4 empty lines
    # to new_poem, with 0 weighted heavier.
    if not args.no_stanzas:
        new_poem.write(random.choice([
        "", "", "", "", "", "\n", "\n\n", "\n\n\n", "\n\n\n\n"]))


# If --privacy_url is set, capture the text from a (policy-type) web page,
# append it to source/privacy.txt, and then quit.
if args.privacy_url:
    capture_policy(args.privacy_url)

# Create a new directory for generated files, if it doesn't exist.
if not os.path.exists(args.new_poem_dir):
    os.makedirs(args.new_poem_dir)

# Create a new file named with the current timestamp and flags passed.
filename = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
if args.unique_lines:
    filename += "_unique"
if args.max_lines:
    filename += "_maxlines" + str(args.max_lines)
if args.max_words_per_line:
    filename += "_maxwords" + str(args.max_words_per_line)
filename += "_py.txt"
new_poem = open(os.path.join(args.new_poem_dir, filename), "a", os.O_NONBLOCK)
new_poem.write(strftime("%Y-%m-%d-%H:%M:%S", gmtime()) + "\n\n\n")

while len(privacy) > 0 and len(poetry) > 0:
    choose_line(random.choice([privacy, poetry, poetry, poetry]))
    if args.max_lines:
        if total_lines >= args.max_lines:
            break


print("File {} created".format(filename))
print("Total lines: {}".format(total_lines))
