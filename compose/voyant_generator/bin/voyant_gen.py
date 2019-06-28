import os
import shutil
import csv
import sys
import zipfile
from time import sleep
import signal
import time
import re


# Makes python list from inputted txt list
def make_list(keyword_path):
    with open(keyword_path, 'r') as f:
        return [line.strip() for line in f]


def voyant(keywords, text_path, corpora_path):
    for f in os.listdir(corpora_path):
       if f.endswith('.csv') or f.endswith('.zip'):
         os.remove(os.path.join(corpora_path, f))
    csv_path = corpora_path
    keywords = make_list(keywords)
    # Matching keywords to texts and filling the directories
    filenames = os.listdir(text_path)
    for text_file in filenames:
        full_text_path = os.path.join(text_path, text_file)
        with open(full_text_path, 'r', encoding='utf-8') as text:
            text = text.read()
            for word in keywords:
                if is_in(text, word):
                    word = word.replace(' ', '_')
                    with zipfile.ZipFile(os.path.join(corpora_path, word) + '.zip', 'a') as myzip:
                        zip_path = os.path.join(word, text_file)
                        if zip_path not in myzip.namelist():
                            myzip.write(full_text_path, zip_path)

    # Making csv of all the voyant urls
    fields = ('keyword', 'url')
    with open(csv_path + 'voyant.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

        for word in keywords:
            url_template = 'https://jsl-voyant.pennds.org/?input=https://jsl-voyant.pennds.org/corpora/{}'
            url = url_template.format(word.replace(' ', '_') + '.zip')
            writer.writerow({'keyword': word, 'url': url})


# Function to check if a word is in a text
def is_in(text, word):
    return re.findall(r"\b" + word + r"\b", text)


def main():
    def handler(signum, frame):
        sys.exit()
    signal.signal(signal.SIGTERM, handler)
    keywords = str(sys.argv[1]).strip()
    text_path = str(sys.argv[2]).strip()
    corpora_path = str(sys.argv[3]).strip()
    temp_time = 0
    recent_time = 0
    print("Watching input directory for changes every ten seconds.")
    while True:
        for text in os.listdir(text_path):
            if os.path.getmtime(os.path.join(text_path,text)) > recent_time:
                recent_time = os.path.getmtime(os.path.join(text_path, text))
        if os.path.getmtime(keywords) > recent_time:
            recent_time = os.path.getmtime(keywords)
        if recent_time > temp_time:
            temp_time = recent_time
            print("Change detected, generating corpus...")
            voyant(keywords, text_path, corpora_path)
            print("Corpus generation complete.")
            print("Watching for changes...")
        time.sleep(10)

if __name__ == '__main__':
    main()
