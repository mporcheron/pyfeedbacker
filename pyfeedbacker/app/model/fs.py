# -*- coding: utf-8 -*-

from pyfeedbacker.app import config
from pyfeedbacker.app.model import model, outcomes

from collections import OrderedDict

import json



class FileSystemModel(model.Model):
    def __init__(self):
        """Store all marking information in CSV, JSON and text files."""
        super().__init__()

        self._load_raw_data()

    def _load_raw_data(self):
        """Load the data from the JSON files."""
        # load feedbacks
        try:
            file_feedbacks = config.ini['model_file']['file_feedbacks']
            with open(file_feedbacks, 'r') as json_file:
                for submission, stages in json.load(json_file).items():
                    for stage_id, data in stages.items():
                        for score_id, feedback in data.items():
                            self.feedbacks[submission][stage_id][score_id] =\
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

                            self.outcomes[submission][stage_id][outcome_id]=\
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

                        self.marks[stage_id][outcome_id] = mark
        except json.decoder.JSONDecodeError:
            pass
        except FileNotFoundError:
            pass

    def _get_csv_title(self, marks):
        """Generate the first row of the CSV file.
        
        Arguments:
        marks -- True if this is the marks output, otherwise this is for the 
            scores CSV.
        """
        return config.ini['app']['name'] + \
               (' marks' if marks else ' scores')

    def _get_csv_header(self, marks):
        """Generate the full header of the CSV for scores/marks. Generates
        three rows:
        1) a title row
        2) a row listing stages
        3) a listing each outcome ID
        
        Arguments:
        marks -- True if this is the marks output, otherwise this is for the 
            scores CSV.
        """
        # calculate mapping
        mapping = OrderedDict()
        for submission, stages in self.outcomes.items():
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
        """Save all the feedbacks, outcomes, and outcomes marks to JSON files 
        and the scores and marks per submission to CSV. Feedbacks can also be
        saved to text files, one per submission.
        
        Keyword arguments:
        force_finalise -- Forces the saving of marks per submission to CSV files
            and feedbacks to individual text files if True.
        """
        self._save_scores(force_finalise=force_finalise)
        self._save_feedbacks(force_finalise=force_finalise)
        self._save_outcomes()
        self._save_outcomes_marks()

    def _save_scores(self, force_finalise=False, save_marks=False):
        """Save scores, and optionally marks, to CSV files.
        
        Keyword arguments:
        force_finalise -- Forces the saving of marks to a separate CSV file
            if True.
        save_marks -- Only save marks to a CSV file, not scores, if True.
        """
        file_name = config.ini['model_file']['file_scores']
        if save_marks:
            file_name = config.ini['model_file']['file_marks']

        title_header_str = config.ini['app']['name'] + \
                           (' marks\n' if save_marks else ' scores\n')

        column_header = OrderedDict()
        for submission, outcomes in self.outcomes.items():
            for stage_id in sorted(outcomes.keys()):
                column_header[stage_id] = None
        column_header['sum'] = None

        with open(file_name, 'w') as f:
            f.write(title_header_str)

            f.write('submission')
            for stage_id in column_header.keys():
                f.write(',' + str(stage_id))

            for submission, outcomes in self.outcomes.items():
                f.write('\n' + str(submission))
                i = 1
                for stage_id in column_header.keys():
                    if stage_id in outcomes:
                        if save_marks:
                            f.write(',' + str(outcomes[stage_id].mark))
                        else:
                            f.write(',' + str(outcomes[stage_id].score))
                    else:
                        f.write(',')

                    i += 1

                if save_marks:
                    f.write(str(outcomes.mark))
                else:
                    f.write(str(outcomes.score))

        if not save_marks:
            if config.ini['assessment'].getboolean('scores_are_marks', False) \
                    or force_finalise:
                self._save_scores(False, True)
        elif force_finalise:
            self._save_scores(False, True)

    def _save_feedbacks(self, force_finalise=False):
        """Save the feedbacks model to a JSON file, and optionally generate
        individual text files per submission.
        
        Keyword arguments:
        force_finalise -- Forces the saving of feedbacks to individual text 
            files if True.
        """
        file_name = config.ini['model_file']['file_feedbacks']
        with open(file_name, 'w') as json_file:
            json_file.write(json.dumps(self.feedbacks))

        if config.ini['assessment'].getboolean('scores_are_marks', False) \
                or force_finalise:
            for submission, stages in self.feedbacks.items():
                path = config.ini['model_file']['file_final_feedback'].replace(
                    '##submission##', submission)

                with open(path, 'w') as f:
                    data = {}
                    data['score'] = self.outcomes[submission].score
                    data['mark'] = self.outcomes[submission].mark

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
                        data[f'stage_{stage_id}_score'] = stage_scores.score
                        data[f'stage_{stage_id}_mark'] = stage_scores.mark

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

                    feedback = str(self.feedbacks[submission])
                    for key, value in data.items():
                        feedback = feedback.replace(f'##{key}##', str(value))

                    f.write(feedback)

    def _save_outcomes(self):
        """Save the outcomes model to a JSON file."""
        file_name = config.ini['model_file']['file_outcomes']
        with open(file_name, 'w') as json_file:
            json_file.write(json.dumps(self.outcomes.dict))

    def _save_outcomes_marks(self):
        """Save the outcomes marks model to a JSON file."""
        file_name = config.ini['model_file']['file_outcomes_marks']
        with open(file_name, 'w') as json_file:
            json_file.write(json.dumps(self.marks.dict))