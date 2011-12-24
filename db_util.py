import json
import os

SOURCE_DIRECTORY = './nasa_gallery/'
JSON_DIRECTORY = './json_db/'
JSON_EXTENSION = '.txt'

def get_all_records():
  """
  Returns the file names (without extensions) of all records in the json_db folder
  """
  dir_list = [os.path.splitext(os.path.basename(x))[0] for x in os.listdir(JSON_DIRECTORY)]
  return dir_list

def open_NASARecord(record_id):
  f = open(JSON_DIRECTORY + record_id + JSON_EXTENSION, 'r').read()
  json_obj = json.loads(f)
  record = NASARecord(json_obj)
  return record
  

class NASARecord():

  def __init__(self, data=None):
    if data:
      self.record_id = str(data['record_id'])
      self.date = int(data['date'])
      self.description = str(data['description'])
      self.category = str(data['category'])
      self.tags = data['tags']  # this is an int array
      self.url = str(data['url'])
      self.image_alt_text = str(data['image_alt_text'])
      if 'sml_image' in data:
        self.sml_image = str(data['sml_image'])
      else:
        self.sml_image = ''
      if 'lrg_image' in data:
        self.lrg_image = str(data['lrg_image'])
      else:
        self.lrg_image = ''
      self.med_image = str(data['med_image'])
      self.med_image_width = int(data['med_image_width'])
      self.med_image_height = int(data['med_image_height'])

  
  def save(self):
    # Make sure all the things are set
    #print "saved to:",JSON_DIRECTORY + self.record_id + JSON_EXTENSION
    f = open(JSON_DIRECTORY + self.record_id + JSON_EXTENSION, 'w')
    json_obj = {}
    json_obj['record_id'] = self.record_id
    json_obj['date'] = self.date
    json_obj['description'] = self.description
    json_obj['category'] = self.category
    json_obj['tags'] = self.tags
    json_obj['url'] = self.url
    json_obj['image_alt_text'] = self.image_alt_text
    json_obj['sml_image'] = self.sml_image
    json_obj['lrg_image'] = self.lrg_image
    json_obj['med_image'] = self.med_image
    # Unsure if I need the ones below
    json_obj['med_image_width'] = self.med_image_width
    json_obj['med_image_height'] = self.med_image_height
    f.write(json.dumps(json_obj, sort_keys=True, indent=4))
