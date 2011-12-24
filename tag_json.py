#!/usr/bin/python2.7
"""
Tags JSON files ccording to valid_tags.txt and saves new tags
onto the JSON files.
"""
import db_util
import tag_analyzer
from progressbar import ProgressBar, SimpleProgress

TAGS_FILE = 'valid_tags.txt'
canonical_tags = {}
canonical_set = None  # helps make set intersections easier
tag_index = {}

def get_tag_list():
  with (open(TAGS_FILE,'r')) as f:
    # strip each element in the resulting list
    # ignore comments - lines which start with #
    tag_list = [[y.strip() for y in x.split(',')] for x in f.readlines() if not x.startswith('#') and len(x.strip()) > 0]
  return tag_list

def tag_list_to_json():
  # TODO: write a function to parse the tag list file
  pass

def read_tags():
  global canonical_tags
  global canonical_set
  global tag_index
  
  tags_list = get_tag_list()
  for idx,tags in enumerate(tags_list):
    base = tags[0].strip()
    tag_index[base] = idx
    for tag in tags:
      tag = tag.strip()
      # key will be the lower case, "cleaned" version for easy hashing
      # value will be the canonical value it should translate to
      canonical_tags[tag_analyzer.clean_words(tag)] = base
  canonical_set = frozenset(canonical_tags.keys())
    #print canonical_tags

def tag_json():
  """
  Tags all the files in the JSON directory
  """
  records = db_util.get_all_records()
  pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(records)).start()
  for idx, record in enumerate(records):
    record = db_util.open_NASARecord(record)
    # it's OK to concatenate all the text since we're using a 
    # bag of words approach
    record_words = set() # set of all the words & phrases in the record
    for i in range(1, tag_analyzer.MAX_PHRASE_LENGTH+1):
      word_hash = {}
      tag_analyzer.hash_string(record, i, word_hash)
      record_words = record_words.union(set(word_hash.keys()))
    
    # now, you have a hash of all the word combinations
    #print "Description:"
    #print record.description
    #print record_words
    found_tags = list(canonical_set.intersection(record_words))
    #print "\n------------------------------------------------"
    #print "Tags found:"
    indicies = [tag_index[canonical_tags[x]] for x in found_tags]
    record.tags = indicies
    record.save()
    # TODO: save back into the file
    # TODO: create a tag_list.txt file which has all the possible tags
    # in a list, so that you don't have to write the whole string into
    # the file
    pbar.update(idx + 1)
  pbar.finish()


if __name__ == "__main__":
  read_tags()
  tag_json()