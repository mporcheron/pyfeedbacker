# -*- coding: utf-8 -*-

import argparse
import pyfeedbacker



parser = argparse.ArgumentParser(description = 'pyfeedbacker')

parser.add_argument(
    '-s', '--score',
    type     = str,
    help     = 'Submission for marking (name of a subdirectory in the ' +
               'configured submissions directory)')

parser.add_argument(
    '-m', '--mark',
    action   = 'store_true',
    help     = 'Run weighting application for converting scores to marks')

args = vars(parser.parse_args())

if args['score'] and not args['mark']:
    pyfeedbacker.start_scorer(args['score'])
elif not args['score'] and args['mark']:
    pyfeedbacker.start_marker()
else:
    raise AttributeError('Cannot run scoring and marking apps simulatenously')