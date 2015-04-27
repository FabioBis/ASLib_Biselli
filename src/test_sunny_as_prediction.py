'''
Created on 27/apr/2015

@author: Fabio Biselli

test_sunny_as_prediction <TEST_PATH> <KB_PATH>

'''

import sys
import os
import getopt
import csv

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
      kb_dir = args[1]
      if kb_dir[-1] != '/':
        kb_dir += '/'
      feat_dir = args[0]
      if feat_dir[-1] != '/':
        feat_dir += '/'
      feat_values = feat_dir + 'test_feature_values.arff'
      predictions = feat_dir + 'predictions.csv'
    else:
      print('Error! ' + args[1] + ' does not exixst.', sys.stderr)
      sys.exit(2)
  else:
    print('Error! ' + args[0] + ' does not exixst.', sys.stderr)
    sys.exit(2)
  

  feat_reader = csv.reader(open(feat_values, 'r'), delimiter = ',')
  pred_reader = csv.reader(open(predictions, 'r'), delimiter = ',')
  diff = False
  for feat_row in feat_reader:
    try:
      pred_row = next(pred_reader)
      feats = feat_row[2:]
      
      # TODO: check values.
      
    except StopIteration:
      diff = True
      print 'Stop Iteration Exception.\n'
      print feat_row
  if not diff:
    print('Info files are identical.')

if __name__ == '__main__':
  main(sys.argv[1:])
  