"""Create a new file with a random permutation of lines from a
terms/privacy/data policy-type webpage and text file with poetry, with
options to set a max number of lines, set a max number of words per line
from the webpage, use only unique lines, and/or randomly skip lines.

Help: python3 terms.py --help

Example usage:

Using the default webpage (Instagram data policy) and a poetry file,
generate 10 lines, 8 words max per line from the webpage, with unique lines:
    python3 terms.py -ml 10 -mw 8 -u
Same as above, but using the Getty Images privacy policy webpage:
    python3 terms.py -ml 10 -mw 8 -u -turl "https://www.gettyimages.com/company/privacy-policy"
"""

import argparse
import html2text
import os
import re
import random
import requests
from string import punctuation
from time import gmtime, strftime

parser = argparse.ArgumentParser(
    description="""Create a new file with a random permutation of lines from a
    terms/privacy/data policy-type webpage and text file with poetry, with
    options to set a max number of lines, set a max number of words per line
    from the webpage, use only unique lines, and/or randomly skip lines.""")
parser.add_argument("-turl", "--terms_url",
                    help="""URL of a terms/privacy/data policy-type webpage
                    (default: Instagram's data policy)""",
                    default="https://help.instagram.com/519522125107875")
parser.add_argument("-pf", "--poetry_file",
                    help="Source poetry text file (default: source/source.txt)",
                    default="source/source.txt")
parser.add_argument("-d", "--new_file_dir",
                    help="""Path to the directory where the new file will be
                    created (default: generated_files)""",
                    default="generated_files")
parser.add_argument("-u", "--unique_lines",
                    action="store_true",
                    help="""Use each unique line from the source file only once
                    (default: False)""")
parser.add_argument("-ml", "--max_lines", type=int,
                    help="Max number of lines of text in total")
parser.add_argument("-mw", "--max_words_per_line", type=int,
                    help="""Max number of words per line, randomly retaining
                    words from the start, middle, or end of the line""",
                    default=8)
args = parser.parse_args()

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


# Set up the html-to-text maker.
t_maker = html2text.HTML2Text()
t_maker.ignore_links = True
t_maker.ignore_images = True
t_maker.ignore_emphasis = True

# Get html from webpage and conver to plaintext.
html = requests.get(args.terms_url)
text = t_maker.handle(html.text)
# print(text)

# Read texts and store their lines in terms and poetry.
terms = text.splitlines()
poetry = open(args.poetry_file).readlines()
lines_seen = set()
total_lines = 0
while len(terms) > 0 and len(poetry) > 0:
    # If --max_lines is passed, break out of the loop
    # as soon as the max lines have been written.
    if args.max_lines:
        if total_lines >= args.max_lines:
            break
    # Randomly select a line from the terms text and remove it from source.
    tline = random.choice(terms)
    terms.remove(tline)
    if not tline.isspace() or len(tline) < 1:
        # If line is all uppercase, change to lowercase.
        if tline.isupper():
            tline = tline.lower()
        # Make sure text is from one sentence and remove punction.
        tline = tline.split('.')[0]
        print(tline)
        tline = re.sub(r"[^\w\'\-\s]", "", tline).strip()
        print(tline)
        # If --max_words_from_line is passed, randomly select the specified
        # num of words from the start, middle, or end of the line.
        remove = 0
        if args.max_words_per_line:
            if len(re.findall(r'\w+', tline)) > args.max_words_per_line:
                remove = len(re.findall(r'\w+', tline)) - args.max_words_per_line
                start = ' '.join(tline.split(' ')[:-remove])
                middle = ' '.join(tline.split(' ')[remove // 2:-(remove // 2)])
                end = ' '.join(tline.split(' ')[remove:])
                tline = random.choice([start, middle, end])
        print(tline)
        # If --unique_lines is passed, check if the line was
        # seen in a previous iteration. If not, write the line
        # to new_file and add it to lines_seen.
        if args.unique_lines:
            if tline.lower() in lines_seen:
                continue
            lines_seen.add(tline.lower())
        if tline.isspace() or len(tline) < 1:
            print("Skip empty line\n")
            continue
        if not tline.isascii():
            print("Skip non-ascii line\n")
            continue
        new_file.write(tline + "\n")
        print("Write line: terms | Words removed: ", str(remove))
        total_lines += 1
        print(total_lines, "/", args.max_lines, "\n")
        # Radomly write 0, 1, 2, 3, or 4 empty lines
        # to new_file, with 0 weighted heavier.
        new_file.write(random.choice([
        "", "", "", "", "\n", "\n\n", "\n\n\n", "\n\n\n\n"]))

    # Randomly select a line from the poetry text and remove it from source.
    pline = random.choice(poetry)
    poetry.remove(pline)
    if not pline.isspace() or len(pline) < 1:
        # Remove leading and trailing punction.
        pline = pline.strip(punctuation)
        # If --unique_lines is passed, check if the line was
        # seen in a previous iteration. If not, write the line
        # to new_file and add it to lines_seen.
        if args.unique_lines:
            if pline.lower() in lines_seen:
                continue
            lines_seen.add(pline.lower())
        new_file.write(pline)
        print("Write line: poetry")
        total_lines += 1
        print(total_lines, "/", args.max_lines, "\n")
        # Radomly write 0, 1, 2, 3, or 4 empty lines
        # to new_file, with 0 weighted heavier.
        new_file.write(random.choice([
        "", "", "", "", "\n", "\n\n", "\n\n\n", "\n\n\n\n"]))


print("File {} created".format(filename))
print("Total lines: {}".format(total_lines))
