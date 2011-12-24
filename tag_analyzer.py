#!/usr/bin/python
import os.path
import db_util
import operator
from progressbar import ProgressBar, SimpleProgress
import string
import csv

NUM_ENTRIES = 32841
ignored_words = None
MAX_WORD_LENGTH = 25 # Everything should actually meet this
MAX_PHRASE_LENGTH = 5

# TODO: replace word_hash with a set

def load_ignored_words():
  global ignored_words
  with open('ignored_words.txt','r') as f:
    ignored_words = dict([(str(x.strip()),None) for x in f.readlines()])

class Occurence():
  def __init__(self):
    self.cf = {}  # cf = collection frequency
    self.documents = set()  # documents the word has occured in

  def add_occurence(self, record_id, word):
    self.documents.add(record_id)
    # the below is used to keep track of most seen occurence of the word
    if word in self.cf:
      self.cf[word] += 1
    else:
      self.cf[word] = 1

  # returns the key with th most common occurence
  def common_occurence(self):
    tuple_list = self.cf.items()
    # Return the most occuring key
    return max(tuple_list, key=lambda item: item[1])[0]

  def __len__(self):
    # returns document frequency, NOT collection frequency
    #return sum(self.cf.values()) # If you want to take a sum of all the values.
    return len(self.documents)

""" Strips all the punctuation from a word """
def clean_words(words):
  # Don't keep any hypenated words, instead split them
  # into multiple words
  # Note this means "single word" list could have multiword
  # words in them
  words = words.replace('-', ' ')
  words = words.replace('/', ' ')
  
  # replace multiple spaces with one
  words = " ".join(words.split())
  # Replace punctuation chars
  words = words.translate(None, string.punctuation)
  words = words.lower()
  return words

def valid_word(word):
  # make sure the first and last word are not "the", etc
  global ignored_words
  if not ignored_words:
    load_ignored_words()
  words = word.split()
  large_word = bool([True for x in words if len(x) > MAX_WORD_LENGTH])
  if large_word:
    print words
  if len(words) == 0:
    return False
  # the first of last word should not be one of the ignored words
  for word in words:
    if word in ignored_words:
      return False
  return True

""" Sort hash by value (highest to lowest) and output
to a CSV file"""
def output_file(word_hash, fname):
  sorted_words = sorted(word_hash.iteritems(), key=lambda a: len(a[1]), reverse=True)
  f = open(fname, 'w')
  freq_writer = csv.writer(open(fname, 'w'))
  for word in sorted_words:
    common_word = word[1].common_occurence()
    common_word = common_word.replace(',', '') # because it messes up CSV printing
    common_word = common_word.replace('\n', '')  # this shouldn't be necessary
    #f.write(common_word + ',' + str(len(word[1])) + '\n')
    freq_writer.writerow([common_word, str(len(word[1]))])


# hashes num_words from a string into word_hash
def hash_string(json_record, num_words, word_hash):
  tag_text = json_record.category + ' ' + json_record.description + ' ' + json_record.image_alt_text
  tag_text = tag_text.split()
  tag_text_words = len(tag_text)
  for i in range(tag_text_words - num_words):
    words = " ".join(tag_text[i:i+num_words]).strip()
    """
    # Split based on comma because 2 clauses joined by a comma are not one tag
    # if len > 1, this tag is contained elsewhere
    if len(words.split(',')) > 1:
      continue
    """

    if ':' in words:
      # if there's a ':' it means it is a time
      continue
    # Remove periods and commas in the original
    words = words.replace(',', '')

    cleaned_word = clean_words(words)

    if valid_word(cleaned_word):
      if cleaned_word not in word_hash:
        word_hash[cleaned_word] = Occurence()
      word_hash[cleaned_word].add_occurence(json_record.record_id, words)
      

def get_input_file_list():
  record_list = [os.path.splitext(x.strip())[0] for x in open('record_list.txt','r').readlines()]
  assert(len(record_list) == NUM_ENTRIES)
  return record_list

def find_word_occurences(word_len, out_file):
  json_list = get_input_file_list()
  word_hash = {}
  pbar = ProgressBar(widgets=[SimpleProgress()], maxval=NUM_ENTRIES).start()
  for idx,json in enumerate(json_list):
    json_record = db_util.open_NASARecord(json)
    hash_string(json_record, word_len,word_hash)
    pbar.update(idx + 1)
  pbar.finish()
  output_file(word_hash, out_file)

if __name__ == "__main__":
  #load_ignored_words() # I'm handling this above
  for word_len in range(1, MAX_PHRASE_LENGTH + 1):
    out_file = str(word_len) + 'words.csv'
    find_word_occurences(word_len, out_file)
  """
  a = Occurence()
  a.add_occurence('hey')
  a.add_occurence('hey')
  a.add_occurence('hey')
  a.add_occurence('there')
  a.add_occurence('there')
  a.add_occurence('again')
  print a.common_occurence()
  print a.cf
  """

  

