#!/usr/bin/python2.7
import re
import unicodedata
import time
import datetime
import string
import db_util
import os.path

from dateutil import parser
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin

BASE_URL = "http://spaceflight.nasa.gov/gallery/"

# Read in unique files
fname_url_map = {}
with open('unique_urls.txt', 'r') as f:
  for line in f:
    url = line.strip()
    fname = url.split('/')[-1]
    fname_url_map[fname] = url

def try_date(date, format):
  try:
    dt = datetime.datetime.strptime(date, format)
    if dt.year > 2012:
        #print "**** Warning: year is:",dt.year
        dt = dt.replace(dt.year-100)
        #print "replacing with:",dt
    if (dt.year < 1900):
      return None
    return dt
  except ValueError:
    return None

def parse_date(date):
  # it's one of two formats
  # dt= datetime.datetime.strptime(date, "%Y-%m-%d")
  #17 Feb. 2010
  # September 11, 2001
  # 23 Sept. 2010
  # 8 June 2011, Kazakhstan time
  # 12-18 Jan. 1986
  #02/05/62
  # Feb. 20, 1961
  date = date.lower()
  remove_chars = [',', '.']
  for char in remove_chars:
    date = date.replace(char, ' ')
  # get rid of multiple spaces
  date = " ".join(date.split())
  date = date.replace('sept ','sep ') # Sep is abbrv. for September
  slash_count = date.count('/')
  if slash_count == 1:
    # For dates like 13/14 March 2008
    date = date.split('/')[1]
  
  #print date
  colon_count = date.count(':')
  """
  if colon_count == 1:
    # Take the part after the colon
    date = date.split(':')[1]
  """
  if colon_count > 1:
    # To parse dates like:
    # (11 September 2005, 19:31:09 GMT)
    date = " ".join(date.split()[:3])

  
  remove_words = ['for', 'release', 'date', 'kazakhstan', 'time']
  for word in remove_words:
    date = date.replace(word, '')
  # To take care of time ranges in dates
  hyphen_count = date.count('-')
  #print "before hyphen parsing:",date
  if hyphen_count > 0:
    if hyphen_count == 1:
      # Always take the second half of a two-part date
      # Reason being some dates are like this:
      # Aug 23 - Aug 27 1987
      # where the year is in the second part of the date
      date = date.split('-')[1]
    else:
      # In this case, it's a date like
      # 12-03-93
      date = date.replace('-','/')
  
  # Take the first 3 words of a date
  # This is to remove stuff like "Khazakstan time"
  date = date.split()
  
  if len(date) > 3:
    #print "******************************"
    #print "truncated date"
    #print date
    #print "******************************"
    date = date[-3:]
    #print "new date:", date
  date = " ".join(date)
  date = date.strip()

  # if it's a date with 2 numbers for the year:
  # TODO. Need to fix this
  #print "trying to parse:",date
  """
  slash_count = date.count('/')
  if slash_count == 2:
    date = date.split('/')
    if len(date[2]) == 2:
      print "Fix:",date
      exit()
  """

  # accepted formats for dates
  formats = ["%d %B %Y", "%m/%d/%Y", "%B %d %Y", "%B %Y", "%d %b %Y", "%m/%d/%y", "%b %d %Y", "%b %Y", "%Y"]
  for format in formats:
    dt = try_date(date, format)
    #print "---------------\n\n\n"
    #print dt
    if dt:
      return dt
  # If you couldn't find anything
  return None

def clean(val):
  # http://stackoverflow.com/questions/816285/where-is-pythons-best-ascii-for-this-unicode-database
  punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
  val = val.translate(punctuation).encode('ascii', 'ignore')
  #val = unicodedata.normalize('NFKD', val).encode('ascii','ignore')
  val = " ".join(val.split())
  return str(val).strip()

def dt_to_iso(dt):
  return int(dt.strftime('%Y%m%d'))

def iso_to_dt(iso):
  return datetime.datetime.strptime(str(iso),'%Y%m%d')

def dt_to_epoch(dt):
  # http://stackoverflow.com/questions/2775864/python-datetime-to-unix-timestamp
  return int(time.mktime(dt.timetuple()))

def epoch_to_dt(dt):
  # http://stackoverflow.com/questions/3694487/python-initialize-a-datetime-object-with-seconds-since-epoch
  return datetime.datetime.fromtimestamp(dt)


"""
Need to find:
- page title
- med image alt text
- med image width
- med image height
- small image
- medium image
- large image
- description

"""
def parse_data(fname):

  page_data = {}
  html_name = fname.split('/')[-1]
  page_data['url'] = urljoin(BASE_URL, fname_url_map[html_name])

  f = open(fname,'r')
  data = f.read()
  soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

  #print soup.prettify()
  #assert(len(soup.html.head.title.contents) == 1)
  #page_data['page_title'] = clean(soup.html.head.title.contents[0])  # convert to ascii
  #print len(soup.html.head.title)
  #print len(page_data['page_title'])
  #print type(soup.html.head.title)
  #print type(page_data['page_title'])
  #exit()
  #print type(page_title)

  category = soup.findAll(attrs={'face' : re.compile("arial,helvetica", flags=re.IGNORECASE)})[0].contents[0]
  page_data['category'] = clean(category)

  target_area = str(soup.findAll(attrs={'align' : re.compile("center", flags=re.IGNORECASE)})[0])
  
  potential_matches = soup.findAll(attrs={'align' : re.compile("center", flags=re.IGNORECASE)})
  target_area = None
  for match in potential_matches:

    new_soup = BeautifulSoup(str(match))
    new_sections = new_soup.findAll('td', attrs={'width' : 300})
    #print '\n\n -----------------------------------'
    #print "soup:",new_soup.prettify()
    #print "len:",len(new_sections)
    #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
    #for section in new_sections:
    #  print section
    #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
    #print '-----------------------------------\n\n'
    if len(new_sections) > 0:
      target_area = str(match)
      #break
    #print '---------------------------\n\n'
  #print target_area

  if not target_area:
    print "***************** Error: No target area *******************"
    print fname
    print '\n'
    print "------------------------------------------------------------"
    exit()


  
  """
  target_area = str(soup.findAll(attrs={'align' : re.compile("center", flags=re.IGNORECASE)})[1])
  if len(target_area) < 150:
    # Sometimes the format of the page is a little different. In that case, grab
    # another target_area. I know, not quite scientific.
    print "wrong one"
    target_area = str(soup.findAll(attrs={'align' : re.compile("center", flags=re.IGNORECASE)})[0])
  """

  #print type(target_area)
  # Find the page title

  # Parse the area of interest
  soup = BeautifulSoup(target_area)
  #print soup.prettify()
  sections = soup.findAll('td', attrs={'width' : 300})
  #print sections

  # Get title, etc from sections[0]
  
  # ____DEBUG info
  #print type(sections)
  #print sections
  #print len(sections)

  try:
    data = sections[0]
  except IndexError:
    # Eg. as14-64-9089.html
    #print data
    #soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print soup.prettify()
    
    #sections = soup.findAll('td', attrs={'width' : 300})
    print sections
    print target_area
    print "***************** Warning: Index Error *******************"
    print fname
    print '\n'
    print sections
    print target_area
    print "------------------------------------------------------------"
    exit()

  image = soup.findAll('img')
  assert(len(image) == 1)
  image = image[0]
  page_data['med_image'] = urljoin(page_data['url'], clean(image['src']))
  page_data['med_image_width'] = int(image['width'])
  page_data['med_image_height'] = int(image['height'])
  page_data['image_alt_text'] = clean(image['alt']) 

  links = soup.findAll('a')
  for link in links:
    image_size = clean(link.contents[0])
    if image_size == 'high res':
      page_data['lrg_image'] = urljoin(page_data['url'], clean(link['href']))
      assert('hires' in page_data['lrg_image'])
    elif image_size == 'low res':
      page_data['sml_image'] = urljoin(page_data['url'], clean(link['href']))
      assert('lores' in page_data['sml_image'])
    else:
      print "***************** Warning: Invalid  Image *******************"
      print fname
      print '\n\n'
      print "Found invalid image:", links
      print '\n'
      print "------------------------------------------------------------"
      #exit()

  
  
  #print lrg_image
  #print sml_image

  #
  raw_text_block = sections[1].contents[0]
  #print type(raw_text_block)
  #if not isinstance(raw_text_block, 'BeautifulSoup.NavigableString'):
  #print "***((((###(#(#((#(#"

  #print sections[1].contents[0]
  #print sections[1].contents

  if len(str(sections[1].contents[0]).strip()) == 0:
    # If there was a new line
    raw_text_block = sections[1].contents[1]
  
  #print raw_text_block
  
  """
  print sections[1].contents[1]
  exit()
  for idx, entry in enumerate(sections[1].contents):
    if entry and len(entry.strip()) > 0:
      raw_text_block = sections[1].contents[idx]
      print "\n\n\n>>>>>>>>Doing something funking here!\n\n>>>>>>>>>."
      break
  exit()
  """
  try:
     # in case there is a nested <p> tag as there is in some files
    raw_text_block = raw_text_block.contents[0]
  except AttributeError:
    pass
  raw_text_block = unicode(raw_text_block)
  text_block = clean(raw_text_block)
  
  #print raw_text_block


  # Get text block from the sections[1]

  """
  if len(sections[1].contents) != 1:
    print "***************** Warning: Extra  Sections *******************\n"
    print fname
    print "Found unexpected sections when parsing page."
    print "Double check to ensure data was transferred as expected."
    print "\n-----------------------------------------------------------"
    exit()
  """

  """
  try:
    # TODO: see this:
    #http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    #.join(BeautifulSoup(page).findAll(text=True))
    text_block = clean(raw_text_block)
    #print sections[1].contents[0]
  except:
    #for sidx,section in enumerate(sections):
    #  print "\n\n $$$$$$$$$$$$$$$$ection:",sidx
    #  print section.contents
    
    #prist soup.head.nextSibling.name
    print raw_text_block

    #print sections[1].contents[0]
    #print '-----------------\n\n'
    #description_string = sections[1].contents[0]
    #print description_string

    print "\*********** Warning bad contents*************"
    print fname
    print '\n'
    print "^^^^^^^^^^^^^^^^^^^"
    print "sections:"
    print sections
    print "\n-------------------------------------------------"
    raise
  """

  #print page_data
  #print text_block

  # Previously, I tried to get the record ID from the HTML file
  #record_id = text_block.split()[0].strip()
  # Now I'm just using the file name (because the record ID wasn't always in the file)
  record_id = os.path.splitext(fname)[0]

  #print record_id
  
  #record_id = fname.split('/')[-1]  # get rid of folder path
  #record_id = record_id.split('.')[0]  # get rid of extension

  # Find record ID
  try:
    assert(len(record_id) > 4 and len(record_id) < 15)
    # If it couldn't find it, date won't be in parens
    
  except:
    #print "invalid record ID:",record_id
    #print "fname:",fname
    #print text_block
    #if "not yet been catalogued" in text_block:
    #  print fname,"not yet catalogued"
    record_id = html_name.split('.')[0]
    # TODO: Will it be able to prase the below if no date?
    #if '---' in text_block:
    #  date = text_block.split('---')[0]
    
    #else:
    #  exit()

  

  
  #assert(record_id in text_block)

  # Find Description text.
  # Description text follows after either '-----' or ')'
  try:
    description = re.search("--- .*", text_block).group()[3:]
  except:
    try:
      description = re.search('\).*',text_block).group()[1:].strip()
    except:
        description = text_block
        print "\n\n*********** Warning bad description*************"
        print fname
        print '\n'
        print text_block
        print "\n\n-------------------------------------------------"
    # TODO: insert prompt here

  #print "description:",description
  
  # Date format: YYYYMMDD: ISO_8601 (http://en.wikipedia.org/wiki/ISO_8601)

  # Find date & try to parse it
  """
  try:
    date = re.search("\(.*?\)", text_block).group()
  except AttributeError:
    date = ''
  """
  # Usually the date is in parens ()
  potential_dates = re.findall("\(.*?\)",text_block)
  # Other times it occurs before the ---
  no_parens_date = text_block.split('---')[0].strip()
  potential_dates.append(no_parens_date)

  raw_name = record_id.lower()
  if 'jsc' in raw_name:
    # if it's a JSC file which has the year encoded in the name
    # like this file: jsc2005-00107
    raw_name = raw_name[3:7]
  potential_dates.append(raw_name)

  #print potential_dates
  iso = None
  date = None
  #print potential_dates
  for date in potential_dates:
    # Remove parens
    date = date.translate(string.maketrans("",""), '()')
    #print "testing date:",date
    dt = parse_date(date)
    if dt:
      iso = dt_to_iso(dt)
      assert(dt == iso_to_dt(dt_to_iso(dt)))
      break
    #print dt

    
      
    #date = date[1:-1]  # strip parens
    
    # See if this is a date

    """
    idx = text_block.index(date)
    if idx > 25:
      # you have the wrong date
      #print "You have the wrong index:",idx
      #print text_block
      #exit()
      #print "bad date:",date
      date = text_block.split('---')[0].strip()
      if len(date.split()) < 2:
        date = ''
      #print "using date instead:",date
    """

  if not iso:
    # TODO: prompt to see if
    print "***************** Warning: Could not find Date *******************"
    #print ">>>>>>> Tried to parse date:",date
    print fname
    print '\n'
    print text_block
    print "------------------------------------------------------------"
    iso = 0
    # TODO: Don't enter date if not there, write "unknown" or something
    #print "no date available"
    #exit()
    
      

  
  page_data['record_id'] = record_id.strip()
  
  # TODO: DON'T use epoch based calculations for dates. This will mess
  # up all dates before 1970...
  page_data['date'] = iso
  page_data['description'] = description.strip()
  page_data['tags'] = []




  
  #print dt_to_epoch(dt)
  #print "image_id:",image_id
  return db_util.NASARecord(data=page_data)