'''
Created on 17/mag/2015

@author: Fabio Biselli

sunny_as_test [OPTIONS] <FEAT_FILE>

Options
=======
  -K <KB_DIR>
    Knowledge base path (default: $PWD).
  -s <STATIC_SCHEDULE>
    Static schedule to be run in the presolving phase. By default is empty.
  -c <COST>
    Set the feature cost. By default is 0.
  -k <NEIGH.SIZE>
    The default value is sqrt(train set size).
  -P <S1,...,Sk>
    The default values are all the solvers.
  -b <BACKUP>
    Set the Backup Solver (default: Single Best Solver).
  -T <TIMEOUT>
    Set the timeout of SUNNY algorithm (default: the time limit of the
    scenario).
  -o <FILE>
    Prints the predictions in <FILE> instead of std output
    
Output
======
  The prediction on std output as specified in the competition rules.
'''

import sys
import os
import getopt
import csv
import subprocess

def parse_arguments(args):
  if len(args) == 0:
    print 'Error! No arguments given.'
    print 'For help use --help'
    sys.exit(2)
    
  if os.path.exists(args[-1]):
    # Processing runtime informations.
    reader = csv.reader(open(args[-1]), delimiter = ',')
    for row in reader:
      if row and row[0].strip().upper() == '@DATA':
        # Iterates until preamble ends.
        break
    costDictionary = {}
    for row in reader:
      feat_string = ''
      for f in row[2:]:
        feat_string += f + ','
      feat_string = feat_string[:-1]
      costDictionary[row[0]] = feat_string
  else:
    print('Error! ' + args[-1] + ' does not exixst.', sys.stderr)
    sys.exit(2)
    
  string = "".join(str(e) + ' ' for e in args[0:-1])
  return costDictionary, string

def main(args):
  ## costDictionary = {'instance': 'feat1,feat2,...,featN'}.
  costDictionary, argString = parse_arguments(args)
  for key in costDictionary:
    proc = subprocess.Popen(["./sunny_as_test.py " + argString
                               + " " + costDictionary[key]],
                               shell=True, stdout=subprocess.PIPE)
    while True:
      line = proc.stdout.readline()
      if not line:
        break;
      else:
        row = line.split(' ')
        print key + ',' + row[0] + ',' + row[1] + ',' + row[2].strip()

if __name__ == '__main__':
  main(sys.argv[1:])




