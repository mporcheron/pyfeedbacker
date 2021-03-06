# -*- coding: utf-8 -*-

from pyfeedbacker.app import config
from pyfeedbacker.app.model import outcomes

import abc
import importlib
import json
import os
import subprocess


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
            module = importlib.import_module('pyfeedbacker.stages.' + stage_id)
            self.handler = getattr(module, class_name)

            if handler == 'HandlerNone':
                self.state  = StageInfo.STATE_COMPLETE
            else:
                self.state  = state

            self.selectable = True
        except ModuleNotFoundError:
            print('No or invalid file/module called ' +
                  stage_id +
                  '.py in stages/ directory. If file exists, check imports.')
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
        self.feedback     = {}
        self.outcome      = None
        self.error        = ''
        self.output       = None

    def add_feedback(self, id, feedback):
        """
        Add to the feedback for this stage.
        """
        self.feedback[id] = feedback

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
        """Set the controller (and by proxy the model and the view). Called by
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

    def add_outcome(self,
                    outcome_id,
                    key = None,
                    explanation = None,
                    value = None,
                    all_values = None,
                    user_input = False):
        self.outcomes[outcome_id] = outcomes.Outcome(
            outcome_id  = outcome_id,
            key         = key,
            explanation = explanation,
            value       = value,
            all_values  = all_values,
            user_input  = user_input)

    def update_ui(self):
        """Trigger a UI update at any time for this stage."""
        return self.controller.set_stage_output(self.stage_id, self.output)

    @abc.abstractmethod
    def calculate_outcomes(self):
        pass

    @abc.abstractmethod
    def run(self):
        """Execute the stage. Return a StageResult if the stage execution 
        finished.
        """
        pass

    @abc.abstractmethod
    def on_close(self):
        """End a stage (allows for any exit-time computation). Note this runs on
        the main thread so nothing too taxing!
        """
        pass

    @abc.abstractmethod
    def refresh(self):
        """Refresh the stage. This may need to be called if the stage draws on
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
            text = cfg.get('question' + num)

            type_str = cfg['type' + num]
            if type_str == 'scale':
                try:
                    scale = OutputForm.get_scale(self.stage_id, num)
                    scores = cfg['score' + num].split(',')

                    all_values = [(scale[x], float(scores[x]))
                                  for x in range(0, len(scale))]

                    self.add_outcome(
                        outcome_id  = num,
                        explanation = text,
                        all_values  = all_values)
                except KeyError:
                    pass

            elif type_str == 'input_score':
                score_min = ''
                try:
                    score_min = str(cfg.getfloat('min' + num, None))
                except KeyError:
                    pass

                score_max = ''
                try:
                    score_max = str(cfg.getfloat('max' + num, None))
                except KeyError:
                    pass
                    
                self.add_outcome(
                    outcome_id  = num,
                    explanation = f'{text} ({score_min}???{score_max})',
                    user_input  = True)



class HandlerPython(HandlerBase):
    pass



class HandlerProcess(HandlerBase):
    def __init__(self, stage_id):
        """Run a command as a subprocess.
        
        Override setup() to setup the command, and either set the member 
        variables or call this class's function (i.e. super().setup(???)) to do
        the setup.
        """
        super().__init__(stage_id)

    def set_framework(self, controller):
        result = super().set_framework(controller)
        self.setup()
        return result

    @abc.abstractmethod
    def setup(self,
              command  = ['pwd'],
              run_once = False,
              cwd      = None,
              shell    = False):
        """Override this function to setup the command, and either set the member variables or call this class's function (i.e. super().setup(???)) to dos the setup.
        
        Note the command should be given as a array of words/arguments. Handle the response through the response 
        method, which takes 3 arguments: exit code, stdout and stderr.

        Blocks during execution.
        
        Arguments:
        stage_id -- The current stage in the process (we should know this as   
            this is the file for this stage, but this is just passed in for 
            clarity).
        command -- Array of the command to run.
        run_once -- If True, will only run on the first execution of the stage
            otherwise runs everytime stage is loaded (default: False).
        cwd -- Directory to run command from, if None uses the temporary    
            working directory (the default behaviour).
        shell -- Run the command using the default system shell.
        """
        self.command  = command
        self.run_once = run_once
        self.cwd      = cwd
        self.shell    = shell

    @abc.abstractmethod
    def response(self, returncode, stdout, stderr):
        """Handle the response. By default this always marks the outcome of the 
        stage as a pass.
        
        Arguments:
        returncode -- Exit status from the execution of the command.
        stdout -- Standard output of the command.
        stderr -- Error output of the command.
        """
        result = StageResult(StageResult.RESULT_PASS)
        result.set_output(self.output)
        return result

    def _exec(self):
        if hasattr(self, 'command') and self.command is not None:
            result = subprocess.run(self.command,
                                    cwd            = self.cwd,
                                    capture_output = True,
                                    shell          = self.shell)
            return self.response(result.returncode,
                                 result.stdout,
                                 result.stderr)
        else:
            result = StageResult(StageResult.RESULT_CRITICAL)
            result.set_error(f'No command provided to setup function for '
                             f'{self.stage_id} stage.')
            return result

    def refresh(self):  
        if not self.run_once:
            return self._exec()

    def run(self):
        return self._exec()



class StageError(Exception):
    def __init__(self, mesg):
        """An error that occurs during stage execution that means the stage
        has failed.
        """
        self.mesg = mesg

    def __str(self):
        return self._mesg



class StageIgnorableError(StageError):
    def __init__(self, mesg):
        """A warning that occurs during stage execution but the stage/user can
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



class OutputBase:
    def __init__(self):
        """Base output specifier that all output classes must extend."""
        pass



class OutputNone(OutputBase):
    def __init__(self):
        """There is no output for a given stage."""
        pass



class OutputText(OutputBase):
    def __init__(self, text = ''):
        """An output for a stage that is simply some text to display.

        This can be a single string or a list of string.
        """
        self.text = text



class OutputEditText(OutputBase):
    def __init__(self, texts = []):
        """An output consisting of one or more edit text fields.

        A callback should be called when a field is modified if one is set 
        using the `callback` member variable.

        Empty texts will be displayed as a field, unless the `skip_empty` is 
        set to `True`, in which case, they should be ommited from the output.

        Argument:
        texts -- A series of texts to allow editing of.
        """
        self.texts      = texts
        self.callback   = None
        self.skip_empty = False



class OutputForm(OutputBase):
    def __init__(self, stage_id):
        """An output for a stage consisting of a form to complete, based on 
        values set in the application configuration.
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
                scale = OutputForm.get_scale(stage_id, num)
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
                    for f_id, fb_str in enumerate(feedback):
                        if fb_str == '-':
                            feedback[f_id] = ''
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

    def get_scale(stage_id, num):
        """Calculate the scale for a given question and stage in the application configuration.

        Argument:
        stage_id -- The unique stage identifier.
        num -- The configuration unique question number.
        """
        try:
            cfg = config.ini['stage_' + stage_id]
        except KeyError:
            raise StageError('No stage config for id: ' + stage_id)

        try:
            return json.loads(cfg[cfg['answer' + num]])
        except KeyError:
            try:
                return json.loads(cfg['answer' + num])
            except json.JSONDecodeError as e:
                raise StageError('Invalid scale JSON ' +
                                 'for question ' + num + ': ' +
                                 str(e))
        except json.JSONDecodeError as e:
            raise StageError('Invalid scale JSON: ' +
                             cfg['scale' + num] + ': ' +
                             str(e))


    class Question:
        TYPE_SCALE, TYPE_INPUT_SCORE, TYPE_INPUT_FEEDBACK = range(0,3)

        def __init__(self, num, text, required):
            """A question container. You should create the `Question` and then 
            call one of `set_scale`, `set_input_score`, or `set_input_feedback`.

            Arguments:
            num -- The configured number for the question (not the unique 
                question identifier, which is assigned at runtime based on 
                ordering.
            text -- The instruction/question text
            required -- A boolean value determining if the question is required
                or not.
            """
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



class OutputChecklist(OutputBase):
    def __init__(self, progress = []):
        """
        An output for a stage is a checklist of progress of execution.

        Each item in a progress list is (Bool, String)
        """
        self.progress = progress

    def __getitem__(self, item):
        return self.progress[item]

    def __setitem__(self, item, value):
        self.progress[item] = value

    def set_label(self, label, index):
        self.progress[index] = (self.progress[index][0], label)

    def set_state(self, state, index):
        self.progress[index] = (state, self.progress[index][1])



class OutputMarker(OutputBase):
    def __init__(self, model, stage_id, outcomes):
        """
        Weighting output for a stage, based on its registered outcomes
        and outcomes awarded to each submission.
        """
        self.model       = model
        self.stage_id    = stage_id
        self.outcomes    = outcomes
        self.performance = self.calculate_performance(outcomes)

    def calculate_performance(self, outcomes):
        performance = {}

        # pass through all outomes first to ensure even outcomes
        # where no student got the outcome are still included
        for outcome_id, outcome in outcomes.items():
            # key = outcome['key']
            if outcome['all_values']:
                performance[outcome_id] = {}
                for value in outcome['all_values']:
                    performance[outcome_id][value[0]] = int(0)
            else:
                performance[outcome_id] = int(0)

        # pass thorugh all outcomes
        for _, stages in self.model.outcomes.items():
            for outcome_id, outcome in stages[self.stage_id].items():

                if outcome['all_values'] is not None:
                    key = int(outcome['key'])
                    key = list(outcome['all_values'])[key]
                    key = key[0]
                    try:
                        performance[outcome_id][key] += 1
                    except KeyError:
                        performance[outcome_id][key] = 1    
                else:
                    try:
                        if not isinstance(performance[outcome_id], dict):
                            performance[outcome_id] += 1
                    except KeyError:
                        performance[outcome_id] = 1

        return performance