import csv
import os
import re
import sys
import time


def read_csv_file(csv_name):
    # parse csv into a dictionary
    with open(csv_name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        reader = [r for r in reader if r]
        return {row[0]: row[1] for row in reader}


# output file path
# save_path = 'C:/intern/jekyll/ed/_texts'
save_path = '../ed/_texts'
dirname = os.path.dirname(__file__)
save_path = os.path.join(dirname, '../ed/_texts')

# use inline html to display page number in margin
pageNum1 = "<div style=\"position: absolute; left: 150px;\"> page "
pageNum2 = "</div>"

# use inline div to join two paragraph divided by page number
div1 = "<div style=\"display: inline;\">"
div2 = "</div>"


def transfer_text_file(text_filename, csvdict):
    file_object = open(text_filename, 'r', encoding='utf-8')
    count = 1
    linecount = 0
    list = []
    textdict = dict()
    strline = ""
    join = False
    for line in file_object:
        line = line.strip()
        if line.isdigit():
            if (len(list) >= 1):
                while (len(strline) == 0):
                    strline = list[-1]
                    del list[-1]
            if len(strline) > 0 and strline[-1] == '-':
                strline = strline[:-1]
            if len(strline) > 0 and strline[-1] == '.':
                strline += " "
            if len(strline) != 0:
                list.append(div1 + strline + div2)
            strline = ""
            list.append(pageNum1 + line + pageNum2)
            join = True
            continue
        if len(line) != 0:
            strline += line
            linecount += 1
        if len(line) == 0:
            if join and len(strline) != 0:
                strline = div1 + strline + div2
                join = False
            list.append(strline)
            strline = ""
        if linecount >= 90 and not join and not next(file_object).isdigit():
            textdict["Part " + str(count)] = list
            list = []
            linecount = 0
            count += 1
    list.append(strline)
    textdict["Part " + str(count)] = list
    # find each word in keyword list and turn it into link
    new_text_Dict = dict()
    for textPart, lst in textdict.items():
        newList = []
        for strline in lst:
            if div1 not in strline:
                for k in csvdict.keys():
                    strline = re.sub(k, '[' + k + '](' + csvdict[k] + ')', strline)
                newList.append(strline)
            else:
                # for keyword in joined paragraph, turn it into html a tag
                for k in csvdict.keys():
                    strline = re.sub(k, "<a href=\"" + csvdict[k] + "\">" + k + "</a>", strline)
                newList.append(strline)
        new_text_Dict[textPart] = newList
    return new_text_Dict


def write2mdfile(text_filename, newTextDict, output_dir):
    filename = text_filename.split(".")[0]
    header = []
    header.append("---")
    header.append("layout: narrative")
    header.append("title: " + filename)
    header.append("toc:")
    for c, list in newTextDict.items():
        header.append("- " + str(c))
    header.append("---")
    filename = filename + ".md"
    completeName = os.path.join(output_dir, filename)
    f = open(completeName, 'w', encoding='utf-8')
    for h in header:
        f.write(h)
        f.write('\n')
    for c, list in newTextDict.items():
        f.write("## " + str(c))
        f.write('\n')
        for line in list:
            f.write(line)
            f.write('\n')
        f.write("---")
        f.write('\n')
    f.close()
    return


# create md for header
# assume filename is valid
def create_header_md(filename, text_title, text_author, delim_list):
    header = ["---", "layout: narrative"]
    text_title.replace(" ", "_")
    # gutenber filenames are usually something like 104-0.txt, so using the
    # book title is better
    if len(text_title) > 0:
        header.append("title: " + text_title)
    else:
        header.append("title: " + filename)
    if len(text_author) > 0:
        header.append("author: " + text_author)
    header.append("toc: ")
    for delim in delim_list:
        header.append("- " + delim)
    header.append("---")
    return header


# create md file from given inputs
# assume delim_list and content_list are the same length
def create_md(text_filename, text_title, text_author, delim_list, content_list, output_dir):
    dirs = text_filename.split("/")
    filename = dirs[len(dirs) - 1].split(".")[0]
    header = create_header_md(filename, text_title, text_author, delim_list)
    filename += ".md"
    complete_name = os.path.join(output_dir, filename)
    f = open(complete_name, 'w', encoding='utf-8')
    for h in header:
        f.write(h)
        f.write("\n")
    for delim, content in zip(delim_list, content_list):
        f.write("## " + delim)
        f.write("\n")
        f.write(content)
        f.write("---")
        f.write('\n')
    f.close()
    return


# add md for key_words in content
def add_key_md(start_index_list, end_index_list, value, content):
    new_content = ""
    start_index_list_len = len(start_index_list)
    end_index_list_len = len(end_index_list)
    for index in range(0, len(content)):
        if start_index_list_len > 0 and index == start_index_list[0]:
            new_content += "[" + content[index]
            del start_index_list[0]
            start_index_list_len -= 1
        elif end_index_list_len > 0 and index == end_index_list[0]:
            new_content += content[index] + "](" + value + ")"
            del end_index_list[0]
            end_index_list_len -= 1
        else:
            new_content += content[index]
    return new_content


# given a keyword, loop through text to find matches and add md
# assume key_word is lower case and length > 1
def find_key_matches(key_word, key_word_len, value, content):
    content_copy = content.lower()
    start_index_list = [m.start() for m in re.finditer(key_word, content_copy)]
    end_index_list = [x + key_word_len - 1 for x in start_index_list]
    return add_key_md(start_index_list, end_index_list, value, content)


# iter through csv keys and content_list to add in md for keywords in content
def iter_keys_contents(content_list, csv_dict):
    new_content_list = content_list
    for key_word in csv_dict.keys():
        value = csv_dict[key_word]
        key_word_copy = key_word.lower()
        key_word_len = len(key_word)
        temp_content_list = []
        for content in new_content_list:
            new_content = find_key_matches(key_word_copy, key_word_len, value, content)
            temp_content_list.append(new_content)
        new_content_list = temp_content_list
    return new_content_list


# pass through content_list and remove any string that has length
# less than threshold and remove its corresponding delimeter
# assume both lists are equal length
def filter_content(delim_list, content_list):
    filtered_delim_list = []
    filtered_content_list = []
    threshold = 1000
    filtered_delim_list.append(delim_list[0])
    filtered_content_list.append(content_list[0])
    # we start from the second entry since first is "Front Matter"
    for i in range(1, len(delim_list)):
        content = content_list[i]
        # spaces do not count towards char count
        content_copy = content.replace(" ", "")
        if len(content_copy) > threshold:
            filtered_delim_list.append(delim_list[i])
            filtered_content_list.append(content)
    return filtered_delim_list, filtered_content_list


# returns true if string is a post-content delimeter
def is_post_content_delim(line):
    line = line.lower()
    return (
        line.startswith("epilogue")
        or line.startswith("appendix")
        or line.startswith("glossary")
        or line.startswith("footnotes")
    )


# returns true if string is a pre-content delimeter
# assume line is striped
def is_pre_content_delim(line):
    return (
        line.startswith("INTRODUCTION")
        or line.startswith("THE INTRODUCTION")
        or line.startswith("PREFACE")
        or line.startswith("THE PREFACE")
        or line.startswith("EXTRACTS")
    )


# returns true if string is of a different type of delimeter
# assume line is striped
def is_other_delim(line):
    return (
        line.startswith("Adventure ")
        or line.startswith("Book ")
        or line.startswith("BOOK ")
        or line.startswith("CASE ")
        or line.startswith("Letter ")
        or line.startswith("LETTER")
        or line.startswith("PART ")
        or line.startswith("STAVE ")
        or (line.startswith("THE ") and line.endswith(" BOOK"))
        or line.startswith("VOLUME ")
        # or (line.startswith("_") and line.endswith("_"))
    )


# returns true if line ends are properly formated, that is it starts with
# an upper case letter and ends with a letter or number
# assume line is striped
def is_proper_ends(line):
    line_len = len(line)
    if line_len > 1:
        first_char = line[0]
        last_char = line[line_len - 1]
        if (
            not first_char.isupper()
            or not (last_char.isalpha() or last_char.isdigit())
        ):
            return False
    elif line_len == 1:
        if not (line.isalpha() or line.isdigit()):
            return False
    return True


# returns true if line is a roman numeral delimeter
# ex: "I HELLO WORLD"
# ex: "IV: WORLD"
# assume line is striped
def is_roman_delim(line):
    line_len = len(line)
    if line_len == 0:
        return False
    # assume roman numbers will be in capitalized in order to avoid false
    # positives like "did", additionally assume that no chapter will go past
    # 399 so delim don't contain 'D' and 'M'
    roman_num_lst = ["I", "V", "X", "L", "C"]
    dot_index = line.find(".")
    space_index = line.find(" ")
    # for the special case when a sentence starts with "I."" or "I "
    if line[0] == 'I' and (space_index == 1 or dot_index == 1):
        return line.isupper()
    # check for proper formatting and trim everything after the first period and first space
    if dot_index != -1:
        if not is_proper_ends(line[dot_index + 1:].strip()):
            return False
        line = line[:dot_index].strip()
        space_index = line.find(" ")
    if space_index != -1:
        if not is_proper_ends(line[space_index + 1:].strip()):
            return False
        line = line[:space_index]
    # check that the remaining characters are roman digits
    for char in line:
        if char not in roman_num_lst:
            return False
    return True


# returns true if string is a 'decimal delimeter
# ex: "1. This is the first chapter"
# ex: "2 Hello World"
# assume line is striped
def is_decimal_delim(line):
    # we assume decimal chapters won't go past 200
    threshold = 200
    # check for proper formating for content after first period
    dot_index = line.find(".")
    if dot_index != -1:
        if not is_proper_ends(line[dot_index + 1:].strip()):
            return False
        line = line[:dot_index].strip()
    # check for proper formating for content after first space
    space_index = line.find(" ")
    if space_index != -1:
        if not is_proper_ends(line[space_index + 1:].strip()):
            return False
        line = line[:space_index]
    # test if it is a decimal number
    try:
        num = float(line)
        return num > 0 and num <= threshold
    except ValueError:
        return False


# returns true if string is a 'chapter' delimeter
# ex: "Chapter 3"
# ex: "CHAPTER ONE"
# ex: "chap. 2"
# assume line is striped
def is_chapter_delim(line):
    return (
        line.startswith("Chapter")
        or line.startswith("chap.")
        or line.startswith("CHAPTER")
    )


# retrive list of content-delimeters and content
def get_delim_and_content(content):
    lines = content.splitlines()
    delim_list = ["Front Matter"]
    content_list = []
    content_holder = ""
    for line in lines:
        line = line.strip()
        # see if its a delimeter, if so store the information and reset the
        # content_holder for the next section
        if (
            is_chapter_delim(line)
            or is_decimal_delim(line)
            or is_roman_delim(line)
            or is_other_delim(line)
            or is_pre_content_delim(line)
            or is_post_content_delim(line)
        ):
            delim_list.append(line)
            content_list.append(content_holder)
            content_holder = ""
        else:
            content_holder += line + "\n"
    content_list.append(content_holder)
    return delim_list, content_list


# retrive title and author from header
def get_title_and_author(header):
    lines = header.splitlines()
    text_title = ""
    text_author = ""
    text_title_found = False
    text_author_found = False
    for line in lines:
        if text_title_found and text_author_found:
            break
        if (not text_title_found) and line.startswith("Title: "):
            text_title = line[7:].strip()
            text_title_found = True
        if (not text_author_found) and line.startswith("Author: "):
            text_author = line[8:].strip()
            text_author_found = True
    return text_title, text_author


# returns true if we have reached the end of the header
# assume line is striped
def is_end_of_header(line):
    return (
        line.startswith("*** START OF THIS PROJECT")
        or line.startswith("***START OF THIS PROJECT")
        or line.startswith("*** START OF THE PROJECT")
        or line.startswith("***START OF THE PROJECT")
    )


# returns true if we have reached the end of the body
# assume line is striped
def is_end_of_body(line):
    return (
        line.startswith("End of the Project")
        or line.startswith("End of Project")
        or line.startswith("End of The Project")
        or line.startswith("*** END OF THIS PROJECT")
        or line.startswith("***END OF THIS PROJECT")
        or line.startswith("*** END OF THE PROJECT")
        or line.startswith("***END OF THE PROJECT")
    )


# retrieve header and body
def get_header_and_body(text_filename):
    file_object = open(text_filename, 'r', encoding='utf-8')
    header = ""
    body = ""
    parsing_header = True
    # parse header first, then body
    for line in file_object:
        line = line.strip()
        if parsing_header:
            if is_end_of_header(line):
                parsing_header = False
                continue
            else:
                header += line + "\n"
        else:
            if is_end_of_body(line):
                break
            else:
                body += line + "\n"
    return header, body


# parse Gutenberg text file
def parse_gutenberg_text(text_filename, csv_dict, output_dir):
    header, body = get_header_and_body(text_filename)
    title, author = get_title_and_author(header)
    delim_list, content_list = get_delim_and_content(body)
    delim_list, content_list = filter_content(delim_list, content_list)
    content_list = iter_keys_contents(content_list, csv_dict)
    delim_list = [delim[:16].strip() + "..." if len(delim) > 16 else delim[:16].strip() for delim in delim_list]
    create_md(text_filename, title, author, delim_list, content_list, output_dir)
    return


'''
def main_del():
    if len(sys.argv) < 3:
        print("Not enough arguments! Please enter text filename and csv filename.")
        print("Usage : python text2md.py text_file csv_file")
        return
    if len(sys.argv) > 3:
        print("Too many arguments! Please enter text filename and csv filename.")
        print("Usage : python text2md.py text_file csv_file")
    # input text filename
    text_filename = str(sys.argv[1])
    # input csv filename
    csv_name = str(sys.argv[2])
    csv_dict = read_csv_file(csv_name)
    text_dict = transfer_text_file(text_filename, csv_dict)
    write2mdfile(text_filename, text_dict)
    print("Success!")


def test_main():
    text_filename = str(sys.argv[1]).strip()
    csv_filenme = str(sys.argv[2]).strip()
    output_dir = str(sys.argv[3]).strip()
    csv_dict = read_csv_file(csv_filenme)
    parse_gutenberg_text(text_filename, csv_dict, output_dir)
'''


def monitor_text_directory(text_dir, csv_dir, md_dir, timestamp_cache):
    # check txt files in text_dir every 30s, and update md files
    with os.scandir(text_dir) as it:
        for entry in it:
            if entry.name.endswith(".txt"):
                entry_stats = entry.stat()
                if entry.name in timestamp_cache:
                    entry_cache_timestamp = timestamp_cache[entry.name]
                    # if the modified time is the same then we don't parse
                    if (entry_cache_timestamp == entry_stats.st_mtime):
                        continue
                timestamp_cache[entry.name] = entry_stats.st_mtime
                entry_path = text_dir + "/" + entry.name
                csv_path = csv_dir + "/voyant.csv"
                csv_dict = read_csv_file(csv_path)
                # check for the special German text
                if entry.name == "ThomasBrussig_AmKuerzerenEndeDerSonnenallee.txt":
                    text_dict = transfer_text_file(entry_path, csv_dict)
                    write2mdfile(entry.name, text_dict, md_dir)
                else:
                    parse_gutenberg_text(entry_path, csv_dict, md_dir)
    return timestamp_cache


def main():
    # directory that contains all the books in text format
    text_dir = str(sys.argv[1].strip())
    # directory that contains all the (keyword, url) csv files
    # FOR NOW WE ASSUME ONLY VOYANT.CSV IS IN csv_dir
    csv_dir = str(sys.argv[2].strip())
    # directory to insert the markdown files
    md_dir = str(sys.argv[3].strip())
    timestamp_cache = {}
    while True:
        timestamp_cache = monitor_text_directory(text_dir, csv_dir, md_dir, timestamp_cache)
        time.sleep(30)


if __name__ == "__main__":
    main()
