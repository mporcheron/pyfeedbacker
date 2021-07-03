# -*- coding: utf-8 -*-

import argparse
import pyfeedbacker



parser = argparse.ArgumentParser(description = 'pyfeedbacker')

parser.add_argument(
    '-m', '--mark',
    type     = str,
    help     = 'Submission for marking (name of a subdirectory in the ' +
               'configured submissions directory)')

parser.add_argument(
    '-w', '--weight',
    action   = 'store_true',
    help     = 'Run weighting application for converting scores to marks')

args = vars(parser.parse_args())

if args['mark'] and not args['weight']:
    pyfeedbacker.start_marker(args['mark'])
elif not args['mark'] and args['weight']:
    pyfeedbacker.start_weighter()
else:
    raise AttributeError('Cannot run marking and weighting apps simulatenously')