# -*- coding: utf-8 -*-

from . import config

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

        self.stage_id   = stage_id
        self.label      = label

        self.thread     = None

        class_name      = 'Stage' + stage_id.capitalize()

        # import the stage class
        try:
            module = importlib.import_module('stages.' + stage_id, '..')
            self.handler = getattr(module, class_name)

            self.handler.set_framework(self.handler, self.controller)

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

    def set_output(self, output):
        """
        Set the final output for the stage. This should be one of the Output*
        classes in app.stag.e
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
    TAG = '__'

    def __init__(self):
        """
        A handler is a class that a stage should inherit from and implement
        the required functions. Every stage must be a handler of some form.
        """
        self.output          = OutputNone()
        self.score_info      = None
        self.interactive     = False

    def set_framework(self, controller):
        """
        Set the controller (and by proxy the model and the view). Called by
        the marker controller.
        """
        self.controller = controller
        self.model      = controller.model
        self.view       = controller.view

        self.submission       = self.controller.submission
        self._dir_temp        = config.ini['app']['dir_temp']
        self._dir_submissions = config.ini['app']['dir_submissions']

    def update_ui(self):
        """
        Trigger a UI update at any time for this stage.
        """
        return self.controller.set_stage_output(self.TAG, self.output)

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
                 read_only = False):
        """
        Show 1 or more edit text fields that allow the user to read/edit
        text.
        """
        # FIXME readonly mode not implemented
        if read_only:
            raise NotImplementedError('Read only text is not implemented yet')

        super().__init__()

        self.interactive     = True



class HandlerReadText(HandlerEditText):
    def __init__(self):
        """
        Show 1 or more text fields that allow the user to read text.
        """
        super().__init__(True)



class HandlerForm(HandlerBase):
    def __init__(self):
        """
        Show an interactive form the user can complete.
        """
        super().__init__()
        
        self.output      = OutputForm(self.TAG)
        self.interactive = True



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

        score_min = 0
        score_max = 0

        for k, v in cfg.items():
            if not k.startswith('question'):
                continue
                
            question_score_min = 0
            question_score_max = 0

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
                        
                        if question.required:
                            question_score_min = min(question_score_min,
                                                     this_score)
                        question_score_max = min(question_score_max, this_score)

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
                    min_score = cfg.getfloat('min' + num, None)
                    
                    if question.required:
                        question_score_min = min(question_score_min, min_score)
                except KeyError:
                    min_score = False

                try:
                    max_score = cfg.getfloat('max' + num, None)
                    question_score_max = min(question_score_max, max_score)
                except KeyError:
                    max_score = False

                q.set_input_score(min_score, max_score)

            elif type_str == 'input_feedback':
                q.set_input_feedback()
            else:
                raise StageError('Unrecognised question type: ' + \
                                       type_str + ' for question ' + num + \
                                       '.')

            score_min = min(score_min, question_score_min)
            score_max = min(score_max, score_max)
            self.questions.append(q)

        
        cfg_score_min = config.ini[f'stage_{stage_id}'].getfloat(
            'score_max', None)
        cfg_score_max = config.ini[f'stage_{stage_id}'].getfloat(
            'score_max', None)
        
        if cfg_score_min is not None:
            score_min = max(score_min, cfg_score_min)
        
        if cfg_score_max is not None:
            score_min = min(score_min, cfg_score_max)

        self.scores_info.add_outcome(
            score_min,
            'The minimum possible score after completing the form')
        self.scores_info.add_outcome(
            score_max,
            'The maximum possible score after completing the form')

    def _calculate_scores_info(self):
        for question_id, question in enumerate(output.questions):
        
        self.scores_info = stage.ScoresInfo()
        self.scores_info.add_outcome(
            score_min,
            'The student did NOT make a submission')
        self.scores_info.add_outcome(
            self._score_pass,
            'The student made a submission')


    class Question:
        TYPE_SCALE, TYPE_INPUT_SCORE, TYPE_INPUT_FEEDBACK = range(0,3)

        def __init__(self, num, text, required):
            self.num       = num
            self.text      = text
            self.required  = required
            self.min_score = False
            self.max_score = False

        def set_scale(self, scale, scores, feedback):
            self.type      = OutputForm.Question.TYPE_SCALE
            self.scale     = scale
            self.scores    = scores
            self.min_score = False
            self.max_score = False
            self.feedback  = feedback

        def set_input_score(self, min_score, max_score):
            self.type      = OutputForm.Question.TYPE_INPUT_SCORE
            self.min_score = min_score
            self.max_score = max_score

        def set_input_feedback(self):
            self.type      = OutputForm.Question.TYPE_INPUT_FEEDBACK
            self.min_score = False
            self.max_score = False



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



class ScoresInfo:
    def __init__(self, outcomes=set()):
        self._outcomes = outcomes

    score_min = property(lambda self:min(self._outcomes,
                                         key=lambda outcome: outcome.score),
        doc="""
            Read-only minimum score in the outcomes set.
            """)

    score_max = property(lambda self:min(self._outcomes,
                                         key=lambda outcome: outcome.score),
        doc="""
            Read-only minimum score in the outcomes set.
            """)

    outcomes = property(lambda self:sorted(self._outcomes,
                                           key=lambda outcome: outcome.score),
        doc="""
            Read-only set of outcomes, sorted by score.
            """)

    def add_outcome(self, score, explanation):
        self._outcomes.add(ScoresInfo.Outcome(score, explanation))

    class Outcome:
        def __init__(self, score, explanation):
            self.score       = score
            self.explanation = explanation
