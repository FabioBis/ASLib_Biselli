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
        print >> sys.stderr, 'For help use --help'
        sys.exit(2)
        
    if len(args) == 0:         
        print(opts, args)
        for o in opts:
            if o in ('-h', '--help'):
                print(__doc__)
                sys.exit(0)
        print >> sys.stderr, 'Error! No arguments given.'
        print >> sys.stderr, 'For help use --help'
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
    
    return lb, ub, feat_val, path, name

