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
import csv
