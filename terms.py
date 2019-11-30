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
parser.add_argument("-r", "--random_skip",
                    action="store_true",
                    help="Randomly skip writing lines (default: False)")
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
if args.random_skip:
    filename += "_skip"
if args.max_lines:
    filename += "_maxlines" + str(args.max_lines)
if args.max_words_per_line:
    filename += "_maxwords" + str(args.max_words_per_line)
filename += "_py.txt"
new_file = open(os.path.join(args.new_file_dir, filename), "a", os.O_NONBLOCK)

url = args.terms_url
page = requests.get(url)
text = html2text.html2text(page.text)
# print(text)

# Read source files and store their lines in terms and poetry.
with open(args.poetry_file) as poetry:
    terms = text.splitlines()
    poetry = poetry.readlines()
    lines_seen = set()
    total_lines = 0
    while len(terms) > 0 and len(poetry) > 0:
        # Randomly select a line from the terms text and remove it from source.
        tline = random.choice(terms)
        terms.remove(tline)
        if not tline.isspace():
            # If line is all uppercase, change to lowercase.
            if tline.isupper():
                tline = tline.lower()
            # If --max_lines is passed, break out of the loop
            # as soon as the max lines have been written.
            if args.max_lines:
                if total_lines >= args.max_lines:
                    break
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
            # If --random_skip is passed, randomly skip the line
            # and continue the next iteration of the loop.
            # To increase the chance of skips, add 1s to the list.
            if args.random_skip and random.choice([0, 1]) == 1:
                print("Skip line: terms")
                continue
            # If --unique_lines is passed, check if the line was
            # seen in a previous iteration. If not, write the line
            # to new_file and add it to lines_seen.
            if args.unique_lines:
                if tline.strip().lower() in lines_seen:
                    continue
                lines_seen.add(tline.strip().lower())
            # Make sure text is from one sentence, and remove punction
            # and extra spaces.
            tline = tline.split('.')[0]
            tline = re.sub(r'[^\w\s]', ' ', tline).strip()
            tline = re.sub(' +', ' ', tline)
            new_file.write(tline + "\n")
            print("Write line: terms | Words removed: " + str(remove))
            total_lines += 1
            # Radomly write 0, 1, 2, 3, or 4 empty lines
            # to new_file, with 0 weighted heavier.
            new_file.write(random.choice([
            "", "", "", "", "\n", "\n\n", "\n\n\n", "\n\n\n\n"]))
            # new_file.write("\n\n")
            print(args.max_lines, total_lines)

        # Randomly select a line from the poetry text and remove it from source.
        pline = random.choice(poetry)
        poetry.remove(pline)
        if not pline.isspace():
            # If --max_lines is passed, break out of the loop
            # as soon as the max lines have been written.
            if args.max_lines:
                if total_lines >= args.max_lines:
                    break
            # If --random_skip is passed, randomly skip the line
            # and continue the next iteration of the loop.
            # To increase the chance of skips, add 1s to the list.
            if args.random_skip and random.choice([0, 1]) == 1:
                print("Skip line: poetry")
                continue
            # If --unique_lines is passed, check if the line was
            # seen in a previous iteration. If not, write the line
            # to new_file and add it to lines_seen.
            if args.unique_lines:
                if pline.strip().lower() in lines_seen:
                    continue
                lines_seen.add(pline.strip().lower())
            new_file.write(pline.rstrip(punctuation))
            print("Write line: poetry")
            total_lines += 1
            # Radomly write 0, 1, 2, 3, or 4 empty lines
            # to new_file, with 0 weighted heavier.
            new_file.write(random.choice([
            "", "", "", "", "\n", "\n\n", "\n\n\n", "\n\n\n\n"]))
            # new_file.write("\n\n")
            print(args.max_lines, total_lines)


print("File {} created".format(filename))
print("Total lines: {}".format(total_lines))
