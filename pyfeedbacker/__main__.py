# -*- coding: utf-8 -*-

import argparse
import pyfeedbacker

parser = argparse.ArgumentParser(description = 'pyfeedbacker')

parser.add_argument(
    '-ds', '--dir-submissions',
    type     = str, 
    default  = './_submissions/',
    help     = 'Directory containing all the submissions to ' +
               'provide feedback on')

parser.add_argument(
    '-do', '--dir-output',
    type     = str, 
    default  = './_output/',
    help     = 'Directory where all output should be saved')

parser.add_argument(
    '-dt', '--dir-temp',
    type     = str, 
    default  = './_temp/',
    help     = 'Directory where a submission is copied to during marking')

parser.add_argument(
    '-m', '--mark',
    type     = str,
    help     = 'Submission for marking (name of a dir in --dir-submissions)')

parser.add_argument(
    '-w', '--weight',
    action   = 'store_true',
    help     = 'Run weighting application for converting scores to marks')

args = vars(parser.parse_args())

if args['mark'] and not args['weight']:
    pyfeedbacker.start_marker(submission      = args['mark'],
                              dir_submissions = args['dir_submissions'],
                              dir_temp        = args['dir_temp'],
                              dir_output      = args['dir_output'])
elif not args['mark'] and args['weight']:
    pyfeedbacker.start_weighter(dir_output    = args['dir_output'])
else:
    raise AttributeError('Cannot run marking and weighting apps simulatenously')