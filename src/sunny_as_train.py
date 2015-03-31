#! /usr/bin/env python

'''
Created on 27/mar/2015

@author: Fabio Biselli

sunny_as_train [OPTIONS] <SCENARIO>

Options
=======
  --feat-range <LB, UB>
    The features range values. The default value is [-1,1].
  --feat-def <VALUE>
    The feature value. The default is -1.
  --kb-path <PATH>
    The SCENARIO PATH, default on current folder ($PWD).
  --kb-name <NAME>
    The output folder name. The default value of the folder is kb_SCENARIO.
    
Output
======
  A folder called kb_NAME containing 3 files: NAME_info, NAME_lims (same as
  current version) and NAME_args (list of definitions to be included).
'''

import sys
import os
import getopt
import csv
import json
from math import isnan

# ASLib version.
VERSION = '1.0.1'
                  

def parse_arguments(args):
    '''
    Parse the options specified by the user and returns the corresponding
    arguments properly set.
    '''
    try:
        long_options = ['feat-range', 'feat-def', 'kb-path', 'kb-name', 'help']
        opts, args = getopt.getopt(args, 'h:', long_options)
    except getopt.GetoptError as msg:
        print(msg)
        print('For help use --help', sys.stderr)
        sys.exit(2)
        
    if len(args) == 0:         
        print(opts, args)
        for o in opts:
            if o in ('-h', '--help'):
                print(__doc__)
                sys.exit(0)
        print('Error! No arguments given.', sys.stderr)
        print('For help use --help', sys.stderr)
        sys.exit(2)
    
    scenario = args[0]
    # Initialize variables with default values.
    lb = -1
    ub = 1
    feat_val = -1
    path = os.getcwd()
    name = 'kb_' + scenario
    
    # Options parsing.
    for o, a in opts:
        if o in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        elif o == '--feat-range':
            s = a.split(',')
            lb = s[0]
            ub = s[1]
        elif o == 'feat-def':
            feat_val = a
        elif o == 'kb-path':
            if not os.path.exists(a):
                print >> sys.stderr, 'Error! Directory ' + a + ' not exists.'
                print >> sys.stderr, 'For help use --help'
                sys.exit(2)
            if a[-1] == '/':
                path = a[0: -1]
            else:
                path = a
        elif o == 'kb-name':
            name = a
    
    return scenario, lb, ub, feat_val, path, name


def parse_description(path):
    '''
    Assuming path is the current SCENARIO path, parse the description
    and returns the following values: TIMEOUT, n. of FEATURES,
    PORTFOLIO and n. of ALGORITHM.
    '''
    #FIXME use csv.reader
    with open(path + 'description.txt', 'r') as f:
        for line in f:
            [key, value] = line.split(': ', 1)
            if key == 'algorithm_cutoff_time':
                timeout = int(value.rstrip('\n'))
            elif key == 'features_deterministic':
                features = len(value.split(','))
            elif key == 'algorithms_deterministic':
                portfolio = value.strip(' \n').split(',')
    f.close()                                                
    return timeout, features, portfolio


# Initialize Feature and Knowledge Base variables.
SCENARIO, LB, UB, DEF_FEAT_VALUE, KB_PATH, KB_NAME = \
parse_arguments(sys.argv[1:])

# Working direcory path. TODO: fix on tool deploy.
WD_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + \
    '/data/aslib_' + VERSION + '/' + SCENARIO + '/'

TIMEOUT, FEATURES, PORTFOLIO = \
parse_description(WD_PATH)


print(SCENARIO, LB, UB, DEF_FEAT_VALUE, KB_PATH, KB_NAME, TIMEOUT, FEATURES,
      PORTFOLIO)


# Creating SCENARIO.info
writer = csv.writer(open(KB_PATH + SCENARIO + '.info', 'w'), delimiter = '|')

# Processing runtime informations.
reader = csv.reader(open(WD_PATH + 'algorithm_runs.arff'), delimiter = ',')
for row in reader:
    if row and row[0].strip().upper() == '@DATA':
        # Iterates until preamble ends.
        break
kb = {}
n = 0
for row in reader:
    n += 1
    inst = row[0]
    solver = row[2]
    info = row[4]
    if info != 'ok':
        time = TIMEOUT
    else:
        time = float(row[3])
    assert time != 'ok' or time < TIMEOUT
    if inst not in kb.keys():
        kb[inst] = {}
    kb[inst][solver] = {'info': info, 'time': time}
    
# Processing features.
reader = csv.reader(open(WD_PATH + 'feature_values.arff'), delimiter = ',')
for row in reader:
    if row and row[0].strip().upper() == '@DATA':
        # Iterates until preamble ends.
        break
features = {}
lims = {}
for row in reader:
    inst = row[0]
    nan = float("nan")
    feat_vector = eval(row[1])
    if not lims:
        for k in range(0, len(feat_vector)):
            lims[k] = [float('+inf'), float('-inf')]
        # Computing min/max value for each feature.
        for k in range(0, len(feat_vector)):
            if not isnan(feat_vector[k]):
                if feat_vector[k] < lims[k][0]:
                    lims[k][0] = feat_vector[k]
                elif feat_vector[k] > lims[k][1]:
                    lims[k][1] = feat_vector[k]
        features[inst] = feat_vector
        assert len(feat_vector) == FEATURES
        
for (inst, feat_vector) in features.items():
    if not [s for s, it in kb[inst].items() if it['info'] == 'ok']:
        continue
    new_feat_vector = []
    for k in range(0, len(feat_vector)):
        if lims[k][0] == lims[k][1]:
            # Ignore constant features.
            continue
        if isnan(feat_vector[k]):
            new_val = DEF_FEAT_VALUE
        else:
            min_val = lims[k][0]
            max_val = lims[k][1]
            # Scale feature value in [LB, UB].
            x = (feat_vector[k] - min_val) / (max_val - min_val)
            new_val = LB + (UB - LB) * x
        assert LB <= new_val <= UB
        new_feat_vector.append(new_val)
    assert nan not in new_feat_vector
    kb_row = [inst, new_feat_vector, kb[inst]]
    writer.writerow(kb_row)
  
# Creating SCENARIO.info
lim_file = KB_PATH + '/' + KB_NAME + '/' + SCENARIO + '_lims'
with open(lim_file, 'w') as outfile:
    json.dump(lims, outfile)
    