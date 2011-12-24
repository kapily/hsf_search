#!/usr/bin/python2.7
"""
Generates HTML from JSON files
"""
import db_util
import tag_json
import re

from progressbar import ProgressBar, SimpleProgress

tag_list = None

MAX_TAGS = 10 # not a real limitation but a color in preview limitation

def find_all(substr, full_string):
  indicies = []
  start = 0
  while True:
    start = full_string.find(substr, start)
    if start == -1: break
    indicies.append(start)
    start += len(substr)
  return indicies
    

def insert_highlight(text, start, end, tag_number):
  output = text[:start]
  output += '<span class="tag%i">' % (tag_number)
  output += text[start:end]
  output += '</span>'
  output += text[end:]
  return output

def get_highlighted_text(text_block, tags_idx_list):
  """
  Returns "highlighted" text: a list of tuples with the
  tuple[0] = a string, tuple[1] = bool. If tuple[1] == True
  it means that it needs to be "highlighted"
  Text will be highlighted if it has a match
  """
  #print text_block
  assert(len(tags_idx_list) <= MAX_TAGS)
  for idx,tag_idx in enumerate(tags_idx_list):
    # TODO: assign each tag a color
    #print "looking at tag:",tag_idx
    tags = tag_list[tag_idx]
    for tag in tags:
      #print "looking for tag:",tag
      instances = find_all(tag, text_block)
      for i in range(len(instances)):
        # You have to recompute this because as you insert each
        # element, their indicies change
        instances = find_all(tag, text_block)
        instance = instances[i]
        # TODO: this is wrong, the indicies will change
        start = instance
        end = instance + len(tag)
        text_block = insert_highlight(text_block, start, end, idx)
        #print "found",tag,"at location:",instance
        
      # see if you can find it & add in the html

  return text_block

def format_div(content, class_name):
  html = '<div class="%s">\n %s \n</div>\n' % (class_name, content)
  return html

def format_tag(content, tag_num):
  html = '<span class="tag%i">\n %s \n</span>\n' % (tag_num, content)
  return html

def generate_html():
  global tag_list
  tag_list = tag_json.get_tag_list()
  records = db_util.get_all_records()
  htmlfile = open("tags_preview.html", "w")
  htmlfile.write('<html>\n<head>\n')
  htmlfile.write('<link rel="stylesheet" type="text/css" href="preview.css" />')
  htmlfile.write('</head>\n<body>\n')
  pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(records)).start()
  for idx,record in enumerate(records):
    record = db_util.open_NASARecord(record)
    htmlfile.write('<p>\n')
    record_w_link = '<a href="%s">%s</a>' %(record.med_image, record.record_id)

    category = get_highlighted_text(record.category, record.tags)
    description = get_highlighted_text(record.description, record.tags)

    htmlfile.write(format_div(record_w_link, 'record_id'))
    htmlfile.write(format_div(category, 'category'))
    htmlfile.write('<br/>')
    htmlfile.write(format_div(description, 'description'))
    htmlfile.write('<br/>')
    htmlfile.write(format_div('Tags:', 'tag_divider'))
    # TODO: make the tags the same colors
    
    if len(record.tags) > 0:
      tag_text = ', '.join(format_tag(tag_list[tag_id][0], tag_num) for tag_num,tag_id in enumerate(record.tags))
    else:
      tag_text = 'None'
      #tag_text = ", ".join(tag_list[i][0] for i in record.tags)
      #print "canonical tag:",canonical_tag
    htmlfile.write(format_div(tag_text, 'tag_text'))
    htmlfile.write('<br/>')
    
    htmlfile.write('</p>\n')
    pbar.update(idx + 1)
  pbar.finish()
  htmlfile.write('</body></html>\n')


if __name__ == "__main__":
  generate_html()