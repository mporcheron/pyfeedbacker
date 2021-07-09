# -*- coding: utf-8 -*-

from .. import config
from .. import stage
from . import model

from collections import OrderedDict

import csv
import json
import os



class FileSystemModel(model.BaseModel):
    def __init__(self):
        """
        Store all marking information in CSV, JSON and text files
        """
        super().__init__()

        self._load_raw_data()

    def _load_raw_data(self):
        # load scores
        file_scores  = config.ini['model_file']['file_scores']

        try:
            with open(file_scores, 'r') as f:
                lines = list(open(file_scores, 'r'))
                if len(lines) < 3:
                    raise ValueError(f'The scores file {file_scores} seems  ' +
                                     'to have other data in it.')

                if not lines[0].startswith(self._get_csv_title(False)):
                    raise ValueError(f'The scores file {file_scores} seems ' +
                                     'to have a different header name?')

                lines.pop(0)

                # read stage IDs and model IDs
                current_stage_id = None
                rows = list(csv.reader([lines[0], lines[1]]))

                # ignore submission column
                rows[0].pop(0)
                rows[1].pop(0)

                col_stage_id = ['']
                last_stage_id = None
                for cell in rows[0]:
                    if len(cell) > 0:
                        col_stage_id.append(cell)
                        last_stage_id = cell
                    else:
                        col_stage_id.append(last_stage_id)

                col_score_id = ['']
                for pos, cell in enumerate(rows[1]):
                    col_score_id.append(cell)

                lines.pop(0)
                lines.pop(0)

                for row in csv.reader(lines):
                    if len(row) == 0:
                        continue

                    cells = list(row)
                    submission = cells[0]
                    cells.pop(0)

                    for pos, cell in enumerate(cells):
                        stage_id = col_stage_id[pos+1]
                        score_id = col_score_id[pos+1]

                        if stage_id == 'sum' and score_id == 'sum':
                            continue

                        if len(stage_id) == 0:
                            continue

                        self['scores'][submission][stage_id][score_id] = \
                            float(cell)
        except FileNotFoundError:
            pass

        # load feedbacks
        try:
            file_feedbacks = config.ini['model_file']['file_feedbacks']
            with open(file_feedbacks, 'r') as json_file:
                for submission, stages in json.load(json_file).items():
                    for stage_id, data in stages.items():
                        for score_id, feedback in data.items():
                            self['feedbacks'][submission][stage_id][score_id] =\
                                feedback
        except json.decoder.JSONDecodeError:
            pass
        except FileNotFoundError:
            pass

        # load outcomes
        try:
            file_outcomes = config.ini['model_file']['file_outcomes']
            with open(file_outcomes, 'r') as json_file:
                for submission, stages in json.load(json_file).items():
                    for stage_id, data in stages.items():
                        if data is None:
                            continue

                        for outcome_id, outcome in data.items():
                            if outcome is None:
                                continue

                            self['outcomes'][submission][stage_id][outcome_id]=\
                                outcome
        except json.decoder.JSONDecodeError:
            pass
        except FileNotFoundError:
            pass

        # load outcomes marks
        try:
            file_outcomes_marks = \
                    config.ini['model_file']['file_outcomes_marks']
            with open(file_outcomes_marks, 'r') as json_file:
                for stage_id, stages in json.load(json_file).items():
                    for outcome_id, mark in stages.items():
                        if mark is None:
                            continue

                        self['marks'][stage_id][outcome_id] = mark
        except json.decoder.JSONDecodeError:
            pass
        except FileNotFoundError:
            pass

    def _get_csv_title(self, marks):
        return config.ini['app']['name'] + \
               (' marks' if marks else ' scores')

    def _get_csv_header(self, marks):
        # calculate mapping
        mapping = OrderedDict()
        for submission, stages in self['outcomes'].items():
            for stage_id, stage_scores in stages.items():
                stage_id = str(stage_id)

                for score_id, score in stage_scores.items():
                    score_id = str(score_id)

                    mapping[(stage_id, score_id)] = None
        mapping = mapping.keys()

        # generate headers
        title_header_str = self._get_csv_title(marks)

        stage_header = ['submission']
        for (stage_id, score_id) in mapping:
            if stage_id not in stage_header:
                stage_header.append(stage_id)
            else:
                stage_header.append('')

        stage_header_str = ','.join(stage_header) + ',sum'

        score_header = ['submission']
        for (stage_id, score_id) in mapping:
            score_header.append(score_id)
        score_header_str = ','.join(score_header) + ',sum'

        return [title_header_str, stage_header_str, score_header_str, mapping]

    def save(self, force_finalise=False):
        self._save_scores(force_finalise=force_finalise)
        self._save_feedbacks(force_finalise=force_finalise)
        self._save_outcomes()
        self._save_outcomes_marks()

    def _save_scores(self, force_finalise=False, save_marks=False):
        file_name = config.ini['model_file']['file_scores']
        if save_marks:
            file_name = config.ini['model_file']['file_marks']

        (title_header_str, stage_header_str, score_header_str, mapping) = \
            self._get_csv_header(save_marks)

        with open(file_name, 'w') as f:
            f.write(title_header_str + '\n')
            f.write(stage_header_str + '\n')
            f.write(score_header_str + '\n')

            for submission, stages in self['scores'].items():
                scores = [str(submission)]
                for (stage_id, score_id) in mapping:
                    score = stages[stage_id][score_id]
                    score = float(score)

                    try:
                        mark = self.weights[stage_id][score_id]
                    except:
                        mark = score

                    scores.append(str(float(mark)))

                f.write(','.join(scores) + ',' + str(stages.sum))
                f.write('\n')

            f.write('\n')

        if not save_marks:
            if config.ini['assessment'].getboolean('scores_are_marks', False) \
                    or force_finalise:
                self._save_scores(False, True)
        elif force_finalise:
            self._save_scores(False, True)

    def _save_feedbacks(self, force_finalise=False):
        file_name = config.ini['model_file']['file_feedbacks']
        with open(file_name, 'w') as json_file:
            json_file.write(json.dumps(self['feedbacks']))

        if config.ini['assessment'].getboolean('scores_are_marks', False) \
                or force_finalise:
            for submission, stages in self['feedbacks'].items():
                path = config.ini['model_file']['file_final_feedback'].replace(
                    '##submission##', submission)

                with open(path, 'w') as f:
                    data = {}
                    data['score'] = float(self['scores'][submission].sum)
                    data['score_max'] = config.ini['assessment'].getfloat(
                        'score_max', None)

                    scores = self['scores'][submission]
                    for stage_id, stage_scores in scores.items():
                        data[f'stage_{stage_id}_score'] = stage_scores.sum
                        data[f'stage_{stage_id}_score_max'] = \
                            config.ini[f'stage_{stage_id}'].getfloat(
                                'score_max', None)
                        data[f'stage_{stage_id}_score_min'] = \
                            config.ini[f'stage_{stage_id}'].getfloat(
                                'score_min', None)

                    feedback = str(self['feedbacks'][submission])
                    for key, value in data.items():
                        feedback = feedback.replace(f'##{key}##', str(value))

                    f.write(feedback)

    def _save_outcomes(self):
        file_name = config.ini['model_file']['file_outcomes']
        with open(file_name, 'w') as json_file:
            json_file.write(json.dumps(self['outcomes'].dict))

    def _save_outcomes_marks(self):
        file_name = config.ini['model_file']['file_outcomes_marks']
        with open(file_name, 'w') as json_file:
            json_file.write(json.dumps(self['marks'].dict))