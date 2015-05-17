'''
Created on 27/apr/2015

@author: Fabio Biselli

test_sunny_as_prediction <TEST_PATH> <KB_PATH>


'''

import sys
import os
import getopt
import csv
import subprocess

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
  
  ## Create dictionaries.
  ori_schedule = {}
  my_schedule = {}
  for feat_row in feat_reader:
    try:
      pred_row = next(pred_reader)
      feats = feat_row[2:]
      ori_schedule[pred_row[0]] = eval(pred_row[3])
      featString = "".join(str(e) + ',' for e in feats)
      featString = featString[:-1];
      proc = subprocess.Popen(["./sunny_as_test.py -K "
                               + kb_dir + " " + featString],
                               shell=True, stdout=subprocess.PIPE)
      schedule = []
      while True:
        line = proc.stdout.readline()
        if not line:
          break;
        else:
          row = line.split(' ')
          schedule.append(row[1])
      my_schedule[feat_row[0]] = schedule
       
    except StopIteration:
      print 'Stop Iteration Exception.\n'
      print feat_row
      
  ## Check differences.
  if len(ori_schedule.values()) != len(ori_schedule.values()):
    print('Error: predictions are NOT identical.')
    return
  diff = False
  count = 0
  for key in ori_schedule:
    index = 0
    for tupl in ori_schedule[key]:
      if tupl[1] > 50: # To cut short time schedule.
        if tupl[0] != my_schedule[key][index]:
          diff = True
          count += 1
          print '------------------------------------------------------------'
          print 'Problem on instance: ', key
          print '------------------------------------------------------------'          
          print 'Original:\n', ori_schedule[key]
          print 'My:\n', my_schedule[key]
          print '____________________________________________________________\n'
      index += 1
  if not diff:
    print('Predictions are identical.\n')
  else:
    print('Error: '+ str(count) + ' predictions are NOT identical.\n')

if __name__ == '__main__':
  main(sys.argv[1:])
  