#!/usr/bin/python2.7

"""
Since there are duplicate files in all_urls.txt, this script will go through
the file and keep only the unique files.
"""

urls = [x.strip() for x in open('all_urls.txt','r').readlines()]
stored_urls = {}
save_urls = []
for url in urls:
  short_url = url.split('/')[-1]
  if short_url not in stored_urls:
    stored_urls[short_url] = 1
    save_urls.append(url)

f = open('unique_urls.txt','w')
for url in save_urls:
  f.write(url + '\n')


print "save:",len(save_urls)

