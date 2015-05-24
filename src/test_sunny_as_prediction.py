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

class bcolor:
  OKGREEN = '\033[92m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

def main(args):
  try:
    long_options = ['help']
    opts, args = getopt.getopt(args, 'h:', long_options)
  except getopt.GetoptError as msg:
    print(msg)
    print('For help use --help', sys.stderr)
    sys.exit(2)

  if len(args) < 2:
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
      print('Error! ' + args[1] + ' does not exist.', sys.stderr)
      sys.exit(2)
  else:
    print('Error! ' + args[0] + ' does not exist.', sys.stderr)
    sys.exit(2)
  

  feat_reader = csv.reader(open(feat_values, 'r'), delimiter = ',')
  pred_reader = csv.reader(open(predictions, 'r'), delimiter = ',')
  
  diff = False
  count = 0
  for feat_row in feat_reader:
    try:
      pred_row = next(pred_reader)
      feats = feat_row[2:]
      ori_schedule = eval(pred_row[3])
      featString = "".join(str(e) + ',' for e in feats)
      featString = featString[:-1]
      proc = subprocess.Popen(["./sunny_as_test.py -K "
                               + kb_dir + " " + pred_row[0]
                               + " " + featString],
                               shell=True, stdout=subprocess.PIPE)
      my_schedule = []
      out = []
      while True:
        line = proc.stdout.readline()
        if not line:
          break;
        else:
          out.append(line)
          row = line.split(',')
          my_schedule.append(row[2])
          
      ## Check differences.
      index = 0;
      for schedule in ori_schedule:
        # To cut short time schedule.
        if schedule[1] > 0 and index < len(my_schedule):
          if schedule[0] != my_schedule[index]:
            diff = True
            count += 1
            print bcolor.FAIL + '-------------------------------------------' \
            '-----------------'
            print 'Problem on instance: ', pred_row[0]
            print '---------------------------------------------------------' \
            '---'
            print 'Original Schedule:\n', ori_schedule
            print 'New Schedule:\n', my_schedule
            print '_________________________________________________________' \
            '___' + bcolor.ENDC
          else:
            print bcolor.OKGREEN + 'OK:', out[index][:-1] + bcolor.ENDC
          index += 1
       
    except StopIteration:
      print 'Stop Iteration Exception.\n'
      print feat_row

  if not diff:
    print('Predictions are identical.\n')
  else:
    print('Error: '+ str(count) + ' predictions are NOT identical.\n')

if __name__ == '__main__':
  main(sys.argv[1:])
  