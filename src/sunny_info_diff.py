#! /usr/bin/env python

'''
Created on 02/apr/2015

sunny_info_diff <FilePath_INFO_1> <FilePath_INFO_2>

@author: Fabio Biselli
'''

import sys
import os
import getopt
import csv
import json

def main(args):
  try:
    long_options = ['help']
    opts, args = getopt.getopt(args, 'h:', long_options)
  except getopt.GetoptError as msg:
    print(msg)
    print('For help use --help', sys.stderr)
    sys.exit(2)

  if len(args) != 2:
    print(opts, args)
    for o in opts:
      if o in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    print('Error! Missing one or more arguments.', sys.stderr)
    print('For help use --help', sys.stderr)
    sys.exit(2)
  
  if os.path.exists(args[0]):
    if os.path.exists(args[1]):
      source_1 = args[0]
      source_2 = args[1]
    else:
      print('Error! ' + args[1] + ' does not exixst.', sys.stderr)
      sys.exit(2)
  else:
    print('Error! ' + args[0] + ' does not exixst.', sys.stderr)
    sys.exit(2)
  

  reader_1 = csv.reader(open(source_1, 'r'), delimiter = '|')
  reader_2 = csv.reader(open(source_2, 'r'), delimiter = '|')
  diff = False
  for row1 in reader_1:
    try:
      row2 = next(reader_2)
      if row1[0] != row2[0]:
        diff = True
        print(row1[0],  row2[0])
      if row1[1] != row2[1]:
        for index in range(max(len(row1[1]), len(row2[1]))):
          if float(row1[1][index]) != float(row2[1][index]):
            diff = True
            print(float(row1[1][index]), float(row2[1][index]))
      # FIXME: json compare: JSON requires double quotes.
      #        str.replace("'", '"') should fix the validation.
      if row1[2] != row2[2]:
        diff = True
        print(row1[2], row2[2])
    except StopIteration:
      diff = True
      print row1
      for row in reader_1:
        print row
  if not diff:
    print('Info files are identical.')
    
if __name__ == '__main__':
  main(sys.argv[1:])