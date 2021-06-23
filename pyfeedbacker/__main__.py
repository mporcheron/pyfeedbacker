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
    help     = 'Directory where a submission is copied during feedback generation')

parser.add_argument(
    '-m', '--mark',
    type     = str,
    help     = 'Submission for feedback generation (name of a directory in --dir-submissions)')

args = vars(parser.parse_args())
pyfeedbacker.start_marker(submission      = args['mark'],
                          dir_submissions = args['dir_submissions'],
                          dir_temp        = args['dir_temp'],
                          dir_output      = args['dir_output'])