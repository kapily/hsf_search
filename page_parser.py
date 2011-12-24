import parser_util
import db_util
import parser_util
import os
import os.path

PAGE_EXTENSION = '.html'

def get_record_list():
	record_list = [x.strip() for x in open('record_list.txt','r').readlines()]
	assert(len(record_list) == 32841)
	return record_list

def parse_all_records(overwrite=True):
  record_list = get_record_list()
  for idx,record in enumerate(record_list):
    if not overwrite and os.path.isfile(db_util.SOURCE_DIRECTORY+record+db_util.JSON_EXTENSION):
      # TODO: this does not work well because the name format is different between
      # the html file name names and the record in the HTML file
      continue
      # check to see that the file is there
    
    fname = db_util.SOURCE_DIRECTORY + record + PAGE_EXTENSION
    print idx,':',fname
    #assert(os.path.exists(fname))
    r = parser_util.parse_data(fname)
    r.save()

if __name__ == "__main__":
  
  
  #fname = 'jsc2001e07997.html'

  #fname = 's111e5224.html'
  #fname = 'iss005-366-029.html'

  """
  fname = 'iss011e12835.html'
  x = parser_util.parse_data(fname)
  x.save()
  """

  #print x.description
  #pages = os.listdir('nasa_gallery/')
  
  parse_all_records()
  #print record_list
  #print len(record_list)

