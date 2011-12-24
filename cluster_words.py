import csv

freq_reader = csv.reader(open('1words.csv', 'r'))
word_list = []
for row in freq_reader:
  word_list.append((row[0], int(row[1])))

for word in sorted(word_list):
  print word