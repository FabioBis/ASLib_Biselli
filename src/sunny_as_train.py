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
    with open(path + '/description.txt', 'r') as f:
        for line in f:
            [key, value] = line.split(': ', 1)
            if key == 'algorithm_cutoff_time':
                timeout = value
            elif key == 'features_deterministic':
                features = len(value.split(','))
            elif key == 'algorithms_deterministic':
                portfolio = value.split(',')
                algorithms = len(portfolio)
    f.close()                                                
    return timeout, features, portfolio, algorithms


# Initialize Feature and Knowledge Base variables.
SCENARIO, LB, UB, DEF_FEAT_VALUE, KB_PATH, KB_NAME = \
parse_arguments(sys.argv[1:])

TIMEOUT, FEATURES, PORTFOLIO, ALGORITHMS = \
parse_description(os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + 
                  '/data/aslib_' + VERSION + '/' + SCENARIO)

print(TIMEOUT, FEATURES, PORTFOLIO, ALGORITHMS)