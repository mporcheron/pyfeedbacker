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

            for submission, stages in self.outcomes.items():
                scores = [str(submission)]
                sum = 0
 
                for (stage_id, score_id) in mapping:
                    score = 0.0
                    try:
                        score = float(stages[stage_id][score_id]['value'])
                    except:
                        pass

                    if save_marks:
                        try:
                            group = self.marks[stage_id][score_id]
                            
                            if isinstance(group, dict):
                                if len(group) == 0:
                                    raise

                            try:
                                key = stages[stage_id][score_id]['key']
                                score = group[str(key)]
                            except:
                                # if there is no key, but a value then
                                # it is a input field, in which case
                                # we multiple the mark value by the
                                # score value
                                value = stages[stage_id][score_id]['value']
                                if value is None:
                                    score = group
                                else:
                                    score = value * group
                        except:
                            try:
                                value = stages[stage_id][score_id]['value']
                                if value is not None:
                                    score *= value
                            except:
                                pass

                    sum += score
                    scores.append(str(score))

                f.write(','.join(scores) + ',' + str(sum))
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
                    data['score'] = self.outcomes[submission].sum
                    data['mark'] = self.marks.sum(self.outcomes[submission])

                    data['score_min'] = config.ini['assessment'].getfloat(
                        'score_min', None)
                    data['score_max'] = config.ini['assessment'].getfloat(
                        'score_max', None)

                    data['mark_min'] = config.ini['assessment'].getfloat(
                        'mark_min', None)
                    data['mark_max'] = config.ini['assessment'].getfloat(
                        'mark_max', None)

                    scores = self.outcomes[submission]
                    for stage_id, stage_scores in scores.items():
                        data[f'stage_{stage_id}_score'] = stage_scores.sum
                        data[f'stage_{stage_id}_mark'] = \
                            self.marks[stage_id].sum(stage_scores)

                        data[f'stage_{stage_id}_score_max'] = \
                            config.ini[f'stage_{stage_id}'].getfloat(
                                'score_max', None)
                        data[f'stage_{stage_id}_mark_max'] = \
                            config.ini[f'stage_{stage_id}'].getfloat(
                                'mark_max', None)

                        data[f'stage_{stage_id}_score_min'] = \
                            config.ini[f'stage_{stage_id}'].getfloat(
                                'score_min', None)
                        data[f'stage_{stage_id}_mark_min'] = \
                            config.ini[f'stage_{stage_id}'].getfloat(
                                'mark_min', None)

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