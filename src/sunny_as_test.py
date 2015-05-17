#! /usr/bin/env python

'''
Created on 28/mar/2015

@author: Fabio Biselli

sunny_as_test [OPTIONS] <FEAT_VECTOR>

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
import json
import ast
from math import sqrt
from combinations import binom, get_subset

def parse_arguments(args):
  '''
  Parse the options specified by the user and returns the corresponding
  arguments properly set.
  '''
  try:
    long_options = ['help']
    opts, args = getopt.getopt(args, 'K:s:c:k:P:b:T:o:h:', long_options)
  except getopt.GetoptError as msg:
    print msg
    print 'For help use --help'
    sys.exit(2)

  if len(args) == 0:
    print(opts, args)
    for o in opts:
      if o in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    print 'Error! No arguments given.'
    print 'For help use --help'
    sys.exit(2)
    
  feature_values = args[0].split(',')
    
  # Initialize variables with default values.
  kb_path = os.getcwd()
  if kb_path[-1] != '/':
    kb_path += '/'
  kb_name = kb_path.split('/')[-2]
  # KB option parsing.
  for o, a in opts:
    if o == '-K':
      if os.path.exists(a):
        kb_path = a
        if kb_path[-1] != '/':
          kb_path += '/'
        kb_name = kb_path.split('/')[-2]
      else:
        print 'Error: ' +a+ ' does not exists.'
        print 'Using default folder (cwd).'
  # Read arguments.
  if not os.path.exists(kb_path + kb_name + '.args'):
    print 'Error: ' + kb_path + kb_name + '.args does not exists.'
    sys.exit(2)    
  reader = csv.reader(open(kb_path + kb_name + '.args'), delimiter = '|')
  for row in reader:
    lb = int(row[0])
    ub = int(row[1])
    def_feat_value = float(row[2])
    timeout = float(row[3])
    portfolio = ast.literal_eval(row[5])
    instances = float(row[6])
    
  feature_cost = 0
  static_schedule = [] # TODO: not defined.
  k = int(round(sqrt(instances)))
  backup = None
  out_file = None

  # Options parsing.
  for o, a in opts:
    if o in ('-h', '--help'):
      print(__doc__)
      sys.exit(0)
    elif o == '-s':
      static_schedule = a
    elif o == '-k':
      k = int(a)
    elif o == '-c':
      feature_cost = float(a)
    elif o == '-P':
      s = a.split(',')
      for sol in s:
        portfolio.append(sol)
    elif o == '-b':
      backup = a
    elif o == '-T':
      timeout = float(a)
    elif o == '-o':
      out_file = a

  return lb, ub, def_feat_value, kb_path, kb_name, static_schedule, timeout, \
    k, portfolio, backup, out_file, feature_values, feature_cost, instances


def normalize(feat_vector, lims, inf, sup, def_feat_value):
  norm_vector = []
  i = 0
  for f in feat_vector:
    lb = lims[str(i)][0]
    ub = lims[str(i)][1]
    i += 1
    if lb == ub:
      continue
    if f == '?':
      f = def_feat_value
    else:
      f = float(f)
      if f < lb:
        f = inf
      elif f > ub:
        f = sup
      else:
        x = (f - lb) / (ub - lb)
        f = inf + (sup - inf) * x
        assert inf <= f <= sup
    norm_vector.append(f)
  return norm_vector


def get_neighbours(feat_vector, kb, portfolio, k, timout, instances):
  """
  Returns a dictionary (inst_name, inst_info) of the k instances closer to the 
  feat_vector in the knowledge base kb.
  """
  reader = csv.reader(open(kb, 'r'), delimiter = '|')
  infos = {}
  distances = []
  solved = dict((s, [0, 0.0]) for s in portfolio)
  for row in reader:
    inst = row[0]
    for (s, it) in eval(row[2]).items():
      if it['info'] == 'ok':
        solved[s][0] += 1
        solved[s][1] += float(it['time'])
      else:
        solved[s][1] += timout
    d = euclidean_distance(feat_vector, map(float, row[1][1 : -1].split(',')))
    distances.append((d, inst))
    infos[inst] = row[2]
    
  best = min((instances - solved[s][0],
              solved[s][1], s) for s in solved.keys())
  backup = best[2]
  # FIXME: Unused sorted_dist?
  sorted_dist = distances.sort(key = lambda x : x[0])
  return dict((inst, infos[inst]) for (d, inst) in distances[0 : k]), backup


def euclidean_distance(fv1, fv2):
  """
  Computes the Euclidean distance between two feature vectors fv1 and fv2.
  """
  assert len(fv1) == len(fv2)
  distance = 0.0
  for i in range(0, len(fv1)):
    d = fv1[i] - fv2[i]
    distance += d * d
  return sqrt(distance)


def get_schedule(neighbours, timeout, portfolio, k, backup):
  """
  Given the neighborhood of a given problem and the backup solver, returns the 
  corresponding SUNNY schedule.
  """
 
  # Dictionaries for keeping track of the instances solved and the runtimes. 
  solved = {}
  times  = {}
  for solver in portfolio:
    solved[solver] = set([])
    times[solver]  = 0.0
  for inst, item in neighbours.items():
    item = eval(item)
    for solver in portfolio:
      time = item[solver]['time']
      if time < timeout:
        solved[solver].add(inst)
      times[solver] += time
  # Select the best sub-portfolio, i.e., the one that allows to solve more 
  # instances in the neighborhood.
  max_solved = 0
  min_time = float('+inf')
  best_pfolio = []
  m = len(portfolio)
  for i in range(1, m + 1):
    old_pfolio = best_pfolio
    
    for j in range(0, binom(m, i)):
      solved_instances = set([])
      solving_time = 0
      # get the (j + 1)-th subset of cardinality i
      sub_pfolio = get_subset(j, i, portfolio)
      for solver in sub_pfolio:
        solved_instances.update(solved[solver])
        solving_time += times[solver]
      num_solved = len(solved_instances)
      
      if num_solved >  max_solved or \
        (num_solved == max_solved and solving_time < min_time):
          min_time = solving_time
          max_solved = num_solved
          best_pfolio = sub_pfolio
          
    if old_pfolio == best_pfolio:
      break
    
  # n is the number of instances solved by each solver plus the instances 
  # that no solver can solver.
  n = sum([len(solved[s]) for s in best_pfolio]) + (k - max_solved)
  schedule = {}
  # Compute the schedule and sort it by number of solved instances.
  for solver in best_pfolio:
    ns = len(solved[solver])
    if ns == 0 or round(timeout / n * ns) == 0:
      continue
    schedule[solver] = timeout / n * ns
  
  tot_time = sum(schedule.values())
  # Allocate to the backup solver the (eventual) remaining time.
  if round(tot_time) < timeout:
    if backup in schedule.keys():
      schedule[backup] += timeout - tot_time
    else:
      schedule[backup]  = timeout - tot_time
  sorted_schedule = sorted(schedule.items(), key = lambda x: times[x[0]])
  assert sum(t for (s, t) in sorted_schedule) - timeout < 0.001
  return sorted_schedule


def main(args):
  lb, ub, def_feat_value, kb_path, kb_name, static_schedule, timeout, k, \
    portfolio, backup, out_file, feature_values, feature_cost, \
    instances = parse_arguments(args)    
    
  with open(kb_path + kb_name + '.lims') as infile:
    lims = json.load(infile)
  
  feats = normalize(feature_values, lims, lb, ub, def_feat_value)
  kb = kb_path + kb_name + '.info'
  neighbours, new_backup = get_neighbours(feats, kb, portfolio, k, timeout,
                                          instances)
  if not backup:
    backup = new_backup
  if timeout > feature_cost: 
    schedule = get_schedule(neighbours, timeout - feature_cost,
                              portfolio, k, backup)
  else:
    schedule = []
  if out_file:
    writer = csv.writer(open(out_file, 'w'), delimiter = ',')
    # FIXME: output: instanceID,runID,solver,timeLimit
    for sch in schedule:
      writer.writerow(sch)
  else:
    # FIXME: output: instanceID,runID,solver,timeLimi
    runID = 1
    for sch in schedule:
      print runID,sch[0],sch[1]
      runID += 1

if __name__ == '__main__':
  main(sys.argv[1:])