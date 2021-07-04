# -*- coding: utf-8 -*-

import os
import shutil
import time

from app import config, stage
from app.controller import marker



class StageInit(stage.HandlerPython):
    TAG = 'init'
    STEP_EMPTY, STEP_COPYSUB, STEP_COPYFWK = range(0,3)

    def __init__(self):
        """
        Copy the submission from the submissions directory into a temporary
        directory.
        """
        super().__init__()

        self.output = stage.OutputChecklist([
            (False, 'Create/empty existing directory'),
            (False, 'Copy submission into temporary directory'),
            (False, 'Copy framework into temporary directory')
        ])
        
        self._score_pass = config.ini[f'stage_{StageInit.TAG}'].getfloat(
            'score_max', None)
        score_min = config.ini[f'stage_{StageInit.TAG}'].getfloat(
            'score_max', None)
        
        self.scores_info.add_outcome(
            score_min,
            'The student did NOT make a submission')
        self.scores_info.add_outcome(
            self._score_pass,
            'The student made a submission')

    def run(self):
        """Delete any previous data from the temp directory and reset it"""
        self.update_ui()

        try:
            # time.sleep(1)

            self._create_empty_temp_directory()

            self._copy_submission_to_temp()

            # time.sleep(1)

            self._copy_framework_to_temp()
        except stage.StageError as se:
            result = stage.StageResult(stage.StageResult.RESULT_CRITICAL)
            result.set_output(self.output)
            result.set_error(str(se))
            return result

        result = stage.StageResult(stage.StageResult.RESULT_PASS)
        result.add_score(self._score_pass)
        result.set_output(self.output)
        return result

    def _rmdir(self, directory):
        """Recursively empty a directory"""
        if os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    os.remove(os.path.join(root, file))

            shutil.rmtree(directory)

    def _create_empty_temp_directory(self):
        dir_temp = os.path.abspath(self._dir_temp)

        if not os.path.isdir(dir_temp):
            self.output.set_label('Create temporary directory',
                                  StageInit.STEP_EMPTY)

            os.mkdir(dir_temp)
            if not os.path.isdir(dir_temp):
                raise stage.StageError('Error copying submission: could ' + \
                                       'not create: ' + dir_temp)
            else:
                self.output.set_state(True, StageInit.STEP_EMPTY)

        try:
            self._rmdir(dir_temp)

            self.output.set_state(True, StageInit.STEP_EMPTY)
            self.update_ui()
        except FileNotFoundError:
            raise stage.StageError('Could not find directory: ' + \
                                   dir_temp)

    def _copy_submission_to_temp(self):
        dir_temp = os.path.abspath(self._dir_temp)

        dir_submission = self._dir_submissions + os.sep + self.submission
        dir_submission = os.path.abspath(dir_submission)

        try:
            shutil.copytree(dir_submission, dir_temp)

            self.output.set_state(True, StageInit.STEP_COPYSUB)
            self.update_ui()
        except FileNotFoundError:
            raise stage.StageError('Error copying submission: '  + \
                                   dir_submission + ' does not exist')
        except shutil.Error as e:
            raise stage.StageError('Error copying submission: ' + str(e))

    def _copy_framework_to_temp(self):
        if config.ini['stage_init'].get('framework_directory') != None:
            src_dir = config.ini['stage_init'].get('framework_directory')
            try:
                for dir_, dirs, files in os.walk(src_dir):
                    dst_dir = dir_.replace(src_dir, dir_submission, 1)

                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)

                    for file in files:
                        src_file = os.path.join(dir_, file)
                        dst_file = os.path.join(dst_dir, file)
                        shutil.copy(src_file, dst_file)
            except shutil.Error as e:
                raise stage.StageError('Error copying framework: '  + \
                                        str(e))
            self.output.set_state(True, StageInit.STEP_COPYFWK)
        else:
            self.output.set_state(None, StageInit.STEP_COPYFWK)

