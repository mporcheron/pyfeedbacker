# -*- coding: utf-8 -*-

from .model import outcomes
from . import config

from collections import OrderedDict

import abc
import importlib
import json



class StageInfo:
    STATE_INACTIVE, STATE_ACTIVE, STATE_COMPLETE, STATE_FAILED = range(0,4)

    def __init__(self,
                 controller,
                 stage_id,
                 label,
                 handler,
                 selectable    = True,
                 score_min     = None,
                 score_max     = None,
                 feedback_pre  = None,
                 feedback_post = None,
                 halt_on_error = False,
                 state         = STATE_INACTIVE):
        """
        A marking stage can be a particular element, or point in marking that
        groups together a number of marks for the student.

        Arguments:
        controller -- Controller component for the application
        stage_id   -- Textual simple id for the stage
        label      -- Application UI label
        handler    -- The specific type this stage takes (e.g., is it Python
                      code, or a form)

        Keyword arguments:
        selectable    -- Whether this stage can be selected for execution
        score_min     -- Minimum score for this stage as a float or None
        score_max     -- Maximum score for this stage as a float or None
        feedback_pre  -- Prepend this text to the feedback or None
        feedback_post -- Append this text to the feedback or None
        halt_on_error -- Halt all marking if this stage fails
                         (boolean; default: False)
        state         -- Current state of this stage (default: STATE_INACTIVE)
        """
        self.controller = controller
        self.model      = controller.model
        self.view       = controller.view

        self.debug = config.ini['app'].getboolean('debug', False)

        self.stage_id   = stage_id
        self.label      = label

        self.thread     = None

        class_name      = 'Stage' + stage_id.capitalize()

        # import the stage class
        try:
            module = importlib.import_module('stages.' + stage_id, '..')
            self.handler = getattr(module, class_name)

            if handler == 'HandlerNone':
                self.state  = Stage.STATE_COMPLETE
            else:
                self.state  = state

            self.selectable = True
        except ModuleNotFoundError:
            print('No file/module called ' +
                  stage_id +
                  '.py in stages/ directory')
            self.handler    = HandlerNone
            self.state      = StageInfo.STATE_FAILED
            self.selectable = False
        except AttributeError as e:
            print('Error loading class ' + class_name +
                  ' in stages/' + stage_id + '.py file:\n\t' + str(e))
            self.handler    = HandlerNone
            self.state      = StageInfo.STATE_FAILED
            self.selectable = False

            if self.debug:
                raise e

        self.score_min      = score_min
        self.score_max      = score_max
        self.feedback_pre   = feedback_pre
        self.feedback_post  = feedback_post
        self.halt_on_error  = halt_on_error

    def set_state(self, state):
        self.state = state



class StageResult:
    RESULT_CRITICAL      = 0
    RESULT_ERROR         = 1
    RESULT_FAIL          = 2
    RESULT_PASS          = 3
    RESULT_PASS_NONFINAL = 4
    RESULT_PARTIAL       = 5

    def __init__(self, result):
        """
        Store the result from a stage. This should only be returned
        when a stage can no longer change. So stages such as forms may never
        return this because the form is always mutable.
        """
        self.result       = result
        self.score        = 0
        self.feedback     = ''
        self.outcome      = None
        self.error        = ''
        self.output       = None

    def add_score(self, score):
        """
        Add to the score for this stage. Any min/max limits on score are
        applied in the model and not here.
        """
        self.score       += score

    def add_feedback(self, feedback):
        """
        Add to the feedback for this stage.
        """
        self.feedback    += ''

    def set_outcome(self, outcome):
        """
        Set the outcome for the stage.
        """
        self.outcome     = outcome

    def set_output(self, output):
        """
        Set the final output for the stage. This should be one of the Output*
        classes in app.stage.
        """
        self.output      = output

    def set_error(self, error):
        """
        If the stage failed to execute, show an error prompt in an alert. If the
        stage is marked as required to continue to execute in the configuration
        file, the user will have to abandon marking.
        """
        self.error       += error



class HandlerBase:
    def __init__(self, stage_id):
        """
        A handler is a class that a stage should inherit from and implement
        the required functions. Every stage must be a handler of some form.
        """
        self.output      = OutputNone()
        self.interactive = False
        self.stage_id    = stage_id

    def set_framework(self, controller):
        """
        Set the controller (and by proxy the model and the view). Called by
        the marker controller.
        """
        self.controller       = controller
        self.model            = controller.model
        self.view             = controller.view

        try:
            self.submission   = self.controller.submission
        except AttributeError:
            pass

        self.outcomes         = {}
        self.calculate_outcomes()

        self._dir_temp        = config.ini['app']['dir_temp']
        self._dir_submissions = config.ini['app']['dir_submissions']

    def add_outcome(self, key, explanation, value):
        self.outcomes[key] = outcomes.Outcome(key, explanation, value)

    def update_ui(self):
        """
        Trigger a UI update at any time for this stage.
        """
        return self.controller.set_stage_output(self.stage_id, self.output)

    @abc.abstractmethod
    def calculate_outcomes(self):
        pass

    @abc.abstractmethod
    def run(self):
        """
        Execute the stage. Return a StageResult if the stage execution finished.
        """
        pass

    @abc.abstractmethod
    def refresh(self):
        """
        Refresh the stage. This may need to be called if the stage draws on
        data that may change externally (e.g. the model, or some part of the
        submission may change due to an external event).
        """
        pass



class HandlerNone(HandlerBase):
    pass



class HandlerEditText(HandlerBase):
    def __init__(self,
                 stage_id,
                 read_only = False):
        """
        Show 1 or more edit text fields that allow the user to read/edit
        text.
        """
        # FIXME readonly mode not implemented
        if read_only:
            raise NotImplementedError('Read only text is not implemented yet')

        super().__init__(stage_id)

        self.interactive     = True



class HandlerReadText(HandlerEditText):
    def __init__(self, stage_id):
        """
        Show 1 or more text fields that allow the user to read text.
        """
        super().__init__(stage_id, True)



class HandlerForm(HandlerBase):
    def __init__(self, stage_id):
        """
        Show an interactive form the user can complete.
        """
        super().__init__(stage_id)

        self.output      = OutputForm(self.stage_id)
        self.interactive = True

    def calculate_outcomes(self):
        try:
            cfg = config.ini['stage_' + self.stage_id]
        except KeyError:
            raise StageError('No stage config for id: ' + self.stage_id)
        
        self.questions = []

        score_min = 0
        score_max = 0

        for k, v in cfg.items():
            if not k.startswith('question'):
                continue

            num = k[8:]
            required = cfg.getboolean('required' + num, fallback=False)

            question_score_min = 0
            question_score_max = 0

            type_str = cfg['type' + num]
            if type_str == 'scale':
                try:
                    scores = cfg['score' + num].split(',')
                    for i in range(0, len(scores)):
                        this_score = float(scores[i])

                        if required:
                            question_score_min = min(question_score_min,
                                                     this_score)
                        question_score_max = min(question_score_max, this_score)
                except KeyError:
                    pass

            elif type_str == 'input_score':
                try:
                    score_min = cfg.getfloat('min' + num, None)

                    if required:
                        question_score_min = min(question_score_min, score_min)
                except KeyError:
                    pass

                try:
                    score_max = cfg.getfloat('max' + num, None)
                    question_score_max = min(question_score_max, score_max)
                except KeyError:
                    pass

            score_min = min(score_min, question_score_min)
            score_max = min(score_max, score_max)

        cfg_score_min = config.ini[f'stage_{self.stage_id}'].getfloat(
            'score_max', None)
        cfg_score_max = config.ini[f'stage_{self.stage_id}'].getfloat(
            'score_max', None)

        if cfg_score_min is not None:
            score_min = max(score_min, cfg_score_min)

        if cfg_score_max is not None:
            score_min = min(score_min, cfg_score_max)

        self.add_outcome(
            'score_min',
            'The minimum possible score after completing the form',
            score_min)
        self.add_outcome(
            'score_max',
            'The maximum possible score after completing the form',
            score_max)



class HandlerPython(HandlerBase):
    pass



class HandlerProcess(HandlerBase):
    # FIXME HandlerProcess not implemented
    pass



class StageError(Exception):
    def __init__(self, mesg):
        """
        An error that occurs during stage execution that means the stage
        has failed.
        """
        self.mesg = mesg

    def __str(self):
        return self._mesg



class StageIgnorableError(StageError):
    def __init__(self, mesg):
        """
        A warning that occurs during stage execution but the stage/user can
        continue if they desire.
        """
        self.mesg = mesg

    def __str(self):
        return self._mesg



class StageOutcomes(dict):
    def __getitem__(self, key):
        return super().__getitem__(str(key))

    def add(self, key, explanation, score):
        key = str(key)
        self[key] = outcomes.Outcome(key, explanation, score)



class OutputNone:
    def __init__(self):
        """
        There is no output for a given stage.
        """
        pass



class OutputText:
    def __init__(self, text = ''):
        """
        An output for a stage is simply text.

        This can be a single string or a list of string.
        """
        self.text = text



class OutputEditText:
    def __init__(self, texts = []):
        """
        An output for one or more edit text fields.
        """
        self.texts = texts
        self.callback = None
        self.skip_empty = False

    def set_callback(self, callback):
        self.callback = callback



class OutputForm:
    def __init__(self, stage_id):
        """
        An output for a stage is a form to complete, based on values set
        in the application configuration.
        """
        try:
            cfg = config.ini['stage_' + stage_id]
        except KeyError:
            raise StageError('No stage config for id: ' + stage_id)

        self.questions = []

        for k, v in cfg.items():
            if not k.startswith('question'):
                continue

            num = k[8:]
            required = cfg.getboolean('required' + num, fallback=False)

            q = OutputForm.Question(k[8:], v, required)

            type_str = cfg['type' + num]
            if type_str == 'scale':
                scale = None
                try:
                    scale = json.loads(cfg[cfg['answer' + num]])
                except KeyError:
                    try:
                        scale = json.loads(cfg['answer' + num])
                    except json.JSONDecodeError as e:
                        raise StageError('Invalid scale JSON ' +
                                         'for question ' + num + ': ' +
                                         str(e))
                except json.JSONDecodeError as e:
                    raise StageError('Invalid scale JSON: ' +
                                     cfg['scale' + num] + ': ' +
                                     str(e))

                scores = [0.0] * len(scale)
                try:
                    scores = cfg['score' + num].split(',')
                    for i in range(0, len(scores)):
                        this_score = float(scores[i])
                        scores[i] = this_score

                    if len(scores) != len(scale):
                        raise StageError('Mismatch with number ' +
                                         'of score values (' +
                                          str(len(scores)) +
                                          ') vs. number of answers (' +
                                          str(len(scale)) +
                                          ') for question ' + num +
                                          '.')
                except KeyError:
                    pass

                feedback = None
                try:
                    feedback = cfg['feedback' + num].strip().split('\n')
                    if len(feedback) != len(scale):
                        raise StageError('Mismatch with number ' +
                                         'of feedback responses (' +
                                         str(len(feedback)) +
                                         ') vs. number of answers (' +
                                         str(len(scale)) +
                                         ') in question ' + num + '.')
                except KeyError:
                    pass

                q.set_scale(scale, scores, feedback)

            elif type_str == 'input_score':
                try:
                    score_min = cfg.getfloat('min' + num, None)
                except KeyError:
                    score_min = False

                try:
                    score_max = cfg.getfloat('max' + num, None)
                except KeyError:
                    score_max = False

                q.set_input_score(score_min, score_max)

            elif type_str == 'input_feedback':
                q.set_input_feedback()
            else:
                raise StageError('Unrecognised question type: ' + \
                                       type_str + ' for question ' + num + \
                                       '.')
            self.questions.append(q)



    class Question:
        TYPE_SCALE, TYPE_INPUT_SCORE, TYPE_INPUT_FEEDBACK = range(0,3)

        def __init__(self, num, text, required):
            self.num       = num
            self.text      = text
            self.required  = required
            self.score_min = False
            self.score_max = False

        def set_scale(self, scale, scores, feedback):
            self.type      = OutputForm.Question.TYPE_SCALE
            self.scale     = scale
            self.scores    = scores
            self.score_min = False
            self.score_max = False
            self.feedback  = feedback

        def set_input_score(self, score_min, score_max):
            self.type      = OutputForm.Question.TYPE_INPUT_SCORE
            self.score_min = score_min
            self.score_max = score_max

        def set_input_feedback(self):
            self.type      = OutputForm.Question.TYPE_INPUT_FEEDBACK
            self.score_min = False
            self.score_max = False



class OutputChecklist:
    def __init__(self, progress = []):
        """
        An output for a stage is a checklist of progress of execution.

        Each item in a progress list is (Bool, String)
        """
        self.progress = progress

    def __getitem__(self, item):
        return self.progress[item]

    def __setitem__(self, item, value):
        try:
            self.progress[item] = value
        except IndexError:
            for _ in range(i-len(l)+1):
                self.progress.append(None)
            self.progress[i] = value

    def set_label(self, label, index):
        self.progress[index] = (self.progress[index][0], label)

    def set_state(self, state, index):
        self.progress[index] = (state, self.progress[index][1])



class OutputWeighting:
    def __init__(self, model, stage_id, outcomes):
        """
        Weighting output for a stage, based on its registered outcomes
        and outcomes awarded to each submission.
        """
        self.model       = model
        self.stage_id    = stage_id
        self.outcomes    = outcomes
        self.performance = self._get_outcomes_from_submissions(outcomes)

    def _get_outcomes_from_submissions(self, outcomes):
        performance = {}
        
        for outcome_id in outcomes.keys():
            performance[outcome_id] = 0
        
        for submission, stages in self.model['outcomes'].items():
            for outcome_id, outcome in stages[self.stage_id].items():
                if outcome_id not in performance:
                    performance[outcome_id] = 1
                else:
                    performance[outcome_id] += 1
        return performance