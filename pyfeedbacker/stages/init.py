# -*- coding: utf-8 -*-

from pyfeedbacker.app import config, stage

import os
import shutil



class StageInit(stage.HandlerPython):
    STEP_EMPTY, STEP_COPYSUB, STEP_COPYFWK = range(0,3)

    def __init__(self, stage_id):
        """A stage which the submission from the submissions directory into a temporary directory.

        Arguments:
        stage_id -- The current stage in the process (we should know this as   
            this is the file for this stage, but this is just passed in for 
            clarity)
        """
        super().__init__(stage_id)

        # This stage consists of a checklist of computed actions
        self.output = stage.OutputChecklist([
            (False, 'Create/empty existing directory'),
            (False, 'Copy submission into temporary directory'),
            (False, 'Copy framework into temporary directory')
        ])
        
    def calculate_outcomes(self):
        """Return the set of possible outcomes for this stage. In this stage, 
        they are both predetermiend (student submitted, or student didn't)."""
        self._score_pass = config.ini[f'stage_{self.stage_id}'].getfloat(
            'score_max', None)
        score_min = config.ini[f'stage_{self.stage_id}'].getfloat(
            'score_min', None)
        
        self.add_outcome(
            outcome_id  = 'nosubmission',
            explanation = 'The student did NOT make a submission',
            value       = score_min)
        self.add_outcome(
            outcome_id  = 'submitted',
            explanation = 'The student made a submission',
            value       = self._score_pass)

    def run(self):
        """Delete any previous data from the temp directory and reset it. This 
        is run in a separate thread. The UI can be updated throughout or just 
        once at the end."""
        # Push a UI update now
        self.update_ui()

        try:
            self._create_empty_temp_directory()

            self._copy_submission_to_temp()

            self._copy_framework_to_temp()
        except stage.StageError as se:
            # Return an error result to the application
            # As this is a critical error, the scoring will stop
            result = stage.StageResult(stage.StageResult.RESULT_CRITICAL)
            result.set_outcome(self.outcomes['nosubmission'])
            result.set_output(self.output)
            result.set_error(str(se))
            return result

        # Return a pass result to the application
        # This will enable the next stage to be executed
        result = stage.StageResult(stage.StageResult.RESULT_PASS)
        result.set_outcome(self.outcomes['submitted'])
        result.set_output(self.output)
        return result

    def _rmdir(self, directory):
        """Recursively empty a directory.
        
        Arguments:
        directory -- Path to directory to empty.
        """
        if os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    os.remove(os.path.join(root, file))

            shutil.rmtree(directory)

    def _create_empty_temp_directory(self):
        """Create an empty temporary directory to store the submission while 
        scoring."""
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
        """Copy the submission from the submission directory to the temp 
        directory."""
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
        """If there is a framework specified in the configuration, copy this 
        into the temporary directory."""
        dir_submission = self._dir_submissions + os.sep + self.submission
        dir_submission = os.path.abspath(dir_submission)

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

