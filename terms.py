"""Create a new file with a random permutation of lines from a
text file with a combination of terms/privacy/data policy-type web pages
and a text file with poetry, with options to set a max number of lines,
set a max number of words per line, and use only unique lines

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
    description = """Create a new file with a random permutation of lines from a
    text file with a combination of terms/privacy/data policy-type web pages
    and a text file with poetry, with options to set a max number of lines,
    set a max number of words per line, and use only unique lines."""
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
    "--privacy_file",
    help = """Source privacy text file (default: source/privacy.txt)""",
    default = "source/privacy.txt"
)
parser.add_argument(
    "-pof",
    "--poetry_file",
    help = "Source poetry text file (default: source/poetry.txt)",
    default = "source/poetry.txt"
)
parser.add_argument(
    "-d",
    "--new_file_dir",
    help = """Path to the directory where the new file will be created
    (default: generated_files)""",
    default = "generated_files"
)
parser.add_argument(
    "-u",
    "--unique_lines",
    action = "store_true",
    help = "Use each unique line from the source file only once (default: False)"
)
parser.add_argument(
    "-ml",
    "--max_lines",
    type = int,
    help = "Max number of lines of text in total"
)
parser.add_argument(
    "-mw",
    "--max_words_per_line",
    type = int,
    help= """Max number of words per line, retaining words from the
    start, middle, or end of the line""",
    default = 8
)
parser.add_argument(
    "-ns",
    "--no_stanzas",
    action = "store_true",
    help = "Do not break lines into stanza. Default is idiosyncractic stanazs."
)
args = parser.parse_args()


poetry = open(args.poetry_file).readlines()
privacy = open(args.privacy_file).readlines()
lines_seen = set()
total_lines = 0


def capture_policy(url):
    """
    Get html from a web page, convert it to markdown, and append it to a file.
    """
    t_maker = html2text.HTML2Text()
    t_maker.ignore_links = True
    t_maker.ignore_images = True
    t_maker.ignore_emphasis = True
    html = requests.get(url)
    print(html)
    text = t_maker.handle(html.text)
    file = open(os.path.join("source", "privacy.txt"), "a")
    file.write(text)


def choose_line(text):
    """
    Choose a random line from a source text, write it to a file, and remove it
    from the source text.
    """
    global poetry
    global privacy
    global lines_seen
    global total_lines
    tline = random.choice(text)
    text.remove(tline)
    if len(tline) > 0:
        if tline.isupper():
            tline = tline.lower()
        # If line contains multiple sentences, randomly choose one
        # and remove extra spaces and punction.
        tline = random.choice(tline.split('.'))
        tline = re.sub(r"[^\w\'\-\s]", "", tline).strip()
        print(tline)
        # If the line exceeds --max_words_from_line, randomly choose the
        # specified num of words from the start, middle, or end of the line.
        remove = 0
        if args.max_words_per_line:
            if len(tline.split()) > args.max_words_per_line:
                remove = len(tline.split()) - args.max_words_per_line
                start = ' '.join(tline.split(' ')[:-remove])
                middle = ' '.join(tline.split(' ')[remove // 2:-(remove // 2)])
                end = ' '.join(tline.split(' ')[remove:])
                tline = random.choice([start, middle, end]).strip()
        print(tline)
        # If --unique_lines is set, check if the line was seen in a previous
        # iteration. If not, write the line to new_file and add it to lines_seen.
        if args.unique_lines:
            if tline.lower() in lines_seen:
                return
            lines_seen.add(tline.lower())
        if tline.isspace() or len(tline) < 1:
            print("Skip empty line\n")
            return
        if not tline.isascii():
            print("Skip non-ascii line\n")
            return
        new_file.write(tline + "\n")
        print("Write line | Words removed: ", str(remove))
        total_lines += 1
        print(total_lines, "/", args.max_lines, "\n")
        # Unless --no_stanzas is set, radomly write 0, 1, 2, 3, or 4 empty lines
        # to new_file, with 0 weighted heavier.
        if not args.no_stanzas:
            new_file.write(random.choice([
            "", "", "", "", "", "\n", "\n\n", "\n\n\n", "\n\n\n\n"]))


# If --privacy_url is set, capture the text from a (policy-type) web page,
# append it to source/privacy.txt, and then quit.
if args.privacy_url:
    capture_policy(args.privacy_url)

# Create a new directory for generated files, if it doesn't exist.
if not os.path.exists(args.new_file_dir):
    os.makedirs(args.new_file_dir)

# Create a new file named with the current timestamp and flags passed.
filename = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
if args.unique_lines:
    filename += "_unique"
if args.max_lines:
    filename += "_maxlines" + str(args.max_lines)
if args.max_words_per_line:
    filename += "_maxwords" + str(args.max_words_per_line)
filename += "_py.txt"
new_file = open(os.path.join(args.new_file_dir, filename), "a", os.O_NONBLOCK)

while len(privacy) > 0 and len(poetry) > 0:
    if args.max_lines:
        if total_lines >= args.max_lines:
            break
    choose_line(privacy)
    choose_line(poetry)
    # choose_line(random.choice([privacy, poetry]))

print("File {} created".format(filename))
print("Total lines: {}".format(total_lines))
