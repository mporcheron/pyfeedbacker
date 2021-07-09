# -*- coding: utf-8 -*-

from .. import config, stage
from ..model import outcomes
from ..controller import scorer, marker
from . import widgets as uw

import urwid



class AdapterNone:
    def __init__(self, stage_id, controller, model, window):
        """
        Root adapter class that will simply generate the a fixed text output
        error message.

        Adapters convert output, stored in Output* classes in app.stage to
        urwid widgets.
        """
        self.output    = [urwid.Text('This stage has no output.')]

        self.stage_id   = stage_id
        self.controller = controller
        self.model      = model
        self.window     = window
        self.result     = None

        # where the UI should focus
        self.view_focus   = None

        # if this is the marker, set some more variables
        self.scorer_app = isinstance(controller, scorer.Controller)
        self.marker_app = isinstance(controller, marker.Controller)

        if self.scorer_app:
            self.scores    = model['scores'][controller.submission]
            self.feedbacks = model['feedbacks'][controller.submission]
            self.outcomes  = model['outcomes'][controller.submission]
        elif self.marker_app:
            self.marks   = model['marks']

            # initial score
            score_init = config.ini[f'stage_{stage_id}'].getfloat(
                'score_init', None)
            if score_init:
                self.add_score('__init', score_init)
                self.set_outcome('__init',
                                 explanation = 'Initial score',
                                 score       = score_init)

    def set(self, output):
        """
        Update the output, forcing the adapter to re-adapt it to urwid
        components.
        """
        self.output = [urwid.Text('This stage has no output adapter.')]

    def add_score(self, score_id, score):
        """
        Add to the submission's score (calls through to the model).

        Only works in marker app.
        """
        if self.scorer_app:
            self.controller.add_score(self.stage_id,
                                      score_id,
                                      score)

    def add_feedback(self, feedback_id, feedback):
        """
        Add to the submission's feedback (calls through to the model).

        Only works in marker app.
        """
        if self.scorer_app:
            self.controller.add_feedback(self.stage_id,
                                         feedback_id,
                                         feedback)

    def set_outcome(self,
                    outcome_id,
                    outcome     = None,
                    key         = None,
                    explanation = None,
                    value       = None):
        """
        Add to the submission's outcome (calls through to the model).

        Only works in scorer app.
        """
        if outcome is None:
            outcome = outcomes.Outcome(key, explanation, value)

        if self.scorer_app:
            self.controller.set_outcome(self.stage_id,
                                        outcome_id,
                                        outcome)

    def set_mark(self, outcome_id, mark_id, mark):
        """
        Marks for the outcomes (for each outcome, not tied to a submission yet).

        Only works in marker app.
        """
        if self.marker_app:
            self.controller.set_mark(self.stage_id,
                                     outcome_id,
                                     mark_id,
                                     mark)



class AdapterBase(AdapterNone):
    def set(self, output):
        """
        Sets an output as a list of contents but nothing else. Pretty much
        every adapter will follow this pattern, which is useful for passing
        into an urwid Pile.
        """
        if isinstance(output, list):
            self.output = output
        else:
            self.output = [output]



class AdapterText(AdapterBase):
    def set(self, text):
        """
        Set a stage as a series of urwid Text widgets.
        """
        if isinstance(text, stage.OutputNone):
            text = ('An error has occured that has presented this stage from '
                    'executing.')

        if isinstance(text, stage.OutputText):
            text = text.text

        if not isinstance(text, list):
            text = [text]

        contents = []
        for line in text:
            contents.append(urwid.Text(line))

        super().set(contents)



class AdapterEditText(AdapterBase):
    def set(self, texts):
        """
        Set a stage as a series of editable text fields (urwid EditText
        widgets).
        """
        contents = []
        if isinstance(texts, stage.OutputNone):
            contents = [urwid.Text('An error has occured that has presented '
                                   'this stage fron mexecuting.')]
        else:
            self.outputedittext = texts

            for stage_id, stage_texts in texts.texts.items():
                for key, text in stage_texts.items():
                    if texts.skip_empty and len(text) == 0:
                        continue

                    w = urwid.Edit('', text, multiline=True)
                    urwid.connect_signal(w,
                                        'change',
                                        self._on_edit_change,
                                        (stage_id, key))
                    w = urwid.AttrMap(w, 'edit', 'edit selected')
                    contents.append(w)
                contents.append(urwid.Divider())

        super().set(contents)

    def _on_edit_change(self, w, old_value, user_data):
        """
        Callback when the user has updated the text widget, which then
        calls the specific event callback function.
        """
        value = w.get_edit_text()
        value = value if value is not None else ''
        self.outputedittext.callback(user_data[0], user_data[1], value)





class AdapterChecklist(AdapterText):
    def set(self, output):
        """
        Updates the output for a stage that is a checklist of computed progress.
        """
        contents = []
        for state, item in output.progress:
            line = ' ✅ ' if state \
                           else (' ❎ ' if state is None else ' ❌ ')
            line += item
            contents.append(line)

        super().set(contents)



class AdapterForm(AdapterBase):
    def set(self, output):
        """
        Create an interactive form to be completed by the user. Can contain
        scale-based questions, score input text fields, feedback input fields.
        
        If weighting is True, every field is an input score text field.
        """
        self.outputform = output

        contents = []
        current_scale = None
        min_question_width = 20

        self.questions = output.questions
        self.required_not_completed = set()
        self._last_selected_widget = None
        self._skip_on_edit_change = None
        self._possible_outcomes = {}

        # generate output
        for question_id, question in enumerate(output.questions):
            # column headings
            try:
                if current_scale == None or \
                    current_scale != question.scale:

                    if current_scale != None:
                        contents.append(urwid.Divider())
                        contents.append(urwid.Divider())

                    current_scale = question.scale

                    w = urwid.Columns([urwid.AttrWrap(
                                        urwid.Padding(urwid.Text(item),
                                                     'center', 'pack'),
                                       'table header')
                                          for item in question.scale],
                                      dividechars = 1)
                    w = urwid.Columns([
                                        urwid.AttrWrap(urwid.Divider(),
                                                      'table header'),
                                        w],
                                      min_width = min_question_width,
                                      dividechars = 1)

                    contents.append(w)

            except AttributeError:
                contents.append(urwid.Divider())
                current_scale = None

            # text label
            text = question.text
            if question.score_min != False:
                text += ' (min: ' + str(question.score_min)
                if question.score_max:
                    text += ', max: ' + str(question.score_max) + ')'
                else:
                    text += ')'
            elif question.score_max != False:
                text += ' (max: ' + str(question.score_max) + ')'

            if question.required:
                text += ' *'

            # existing values in the model?
            outcome = None
            if question.num in self.outcomes[self.stage_id]:
                outcome = self.outcomes[self.stage_id][question.num]

            # generate input fields
            inputs = []
            if question.type == stage.OutputForm.Question.TYPE_SCALE:
                inputs += self._generate_scale_question(question_id,
                                                        question,
                                                        outcome)
            elif question.type == stage.OutputForm.Question.TYPE_INPUT_SCORE:
                inputs += self._generate_input_score_question(question_id,
                                                              question,
                                                              outcome)
            elif question.type == stage.OutputForm.Question.TYPE_INPUT_FEEDBACK:
                inputs += self._generate_input_feedback_question(question_id,
                                                                 question,
                                                                 outcome)

            w_inputs        = [uw.JumpableColumns(inputs, dividechars = 1)]
            w_question_text = [urwid.AttrWrap(urwid.Text(text),
                                           'table row')]

            w = urwid.Columns(w_question_text + w_inputs,
                              min_width   = min_question_width,
                              dividechars = 1)

            contents.append(urwid.Divider())
            contents.append(w)
            contents.append(urwid.Divider())

        self.view_focus = [1]

        super().set(contents)

        if len(self.required_not_completed) == 0:
            self.status_check(False)

    def _generate_scale_question(self, question_id, question, outcome):
        existing_score = None

        if outcome is None:
            if question.required:
                self.required_not_completed.add(question.num)

            outcome = outcomes.Outcome('?', question.text)
            self._possible_outcomes[question_id] = outcome
        else:
            outcome_value = float(outcome['value'])

            # determine if score is valid, and add feedback if missing
            if float(question.scores[outcome['key']]) != outcome_value:
                raise stage.StageError(f'Score is different in outcomes when '
                                       f'compared to configuration for question'
                                       f' {question.num} in {self.stage_id}.'
                                       f'Outcome value is {outcome["value"]}'
                                       f' whereas configuration says it should'
                                       f'be {question.scores[outcome["key"]]}.')

            score_value = self.scores[self.stage_id][question.num]
            if score_value != outcome_value:
                raise stage.StageError(f'Score is different in outcomes when '
                                       f'compared to existing score for '
                                       f'question {question.num} in '
                                       f'{self.stage_id}. Outcome value is '
                                       f'{outcome["value"]} whereas saved'
                                       f' score is {score_value}.')

            existing_score = outcome['value']

            if outcome['key'] not in question.feedback:
                feedback = question.feedback[outcome['key']]
                self.add_feedback(question.num, feedback)


        # generate UI elements
        score_max = '/' + str(max(question.scores))
        radio_group = []
        inputs = []
        for score_id, score in enumerate(question.scores):
            checked = False
            try:
                if int(outcome['key']) == score_id:
                    checked = True

                    outcome = \
                        outcomes.Outcome(score_id,
                                         question.text,
                                         existing_score,)
                    self._possible_outcomes[question_id] = outcome
            except ValueError:
                pass

            button = None
            if config.ini['assessment'].getboolean('scores_are_marks',
                                                   False):
                label = str(score)
                button = urwid.RadioButton(radio_group,
                                           label,
                                           checked,
                                           self._on_radio_check,
                                           (question_id, score_id))
            else:
                button = uw.CentredRadioButton(radio_group,
                                               checked,
                                               self._on_radio_check,
                                               (question_id, score_id))

            button = urwid.Padding(button, 'center', 'pack')

            inputs.append(button)

        return inputs

    def _generate_input_score_question(self, question_id, question, outcome):
        existing_score = None

        if outcome is None:
            if question.required:
                self.required_not_completed.add(question.num)

            outcome = outcomes.Outcome('input', question.text)
            self._possible_outcomes[question_id] = outcome
        else:
            # determine if score is valid, and add feedback if missing
            score_value = self.scores[self.stage_id][question.num]
            outcome_value = float(outcome['value'])
            if score_value != outcome_value:
                raise stage.StageError(f'Score is different in outcomes when '
                                       f'compared to existing score for '
                                       f'question {question.num} in '
                                       f'{self.stage_id}. Outcome value is '
                                       f'{outcome["value"]} whereas saved'
                                       f' score is {score_value}.')

            if question.score_min > outcome_value:
                outcome['value'] = question.score_min
            elif question.score_max < outcome_value:
                outcome['value'] = question.score_max

            existing_score = outcome['value']

            self._possible_outcomes[question_id] = \
                outcomes.Outcome('input', question.text, existing_score)

        # generate UI elements
        str_existing_score = '' if existing_score is None \
                                else str(existing_score)
        w = urwid.Edit('',
                       str_existing_score,
                       align = 'center')
        urwid.connect_signal(w,
                            'postchange',
                            self._on_edit_change,
                            question_id)
        w = urwid.AttrMap(w, 'edit', 'edit selected')
        return [w]

    def _generate_input_feedback_question(self, question_id, question, outcome):
        existing_feedback = ''

        if outcome is None:
            if question.required:
                self.required_not_completed.add(question.num)

            outcome = outcomes.Outcome('input', question.text)
            self._possible_outcomes[question_id] = outcome
        else:
            # determine if score is valid, and add feedback if missing
            feedbacks_value = self.feedbacks[self.stage_id][question.num]
            outcome_value = outcome['value']
            if feedbacks_value != outcome['value']:
                raise stage.StageError(f'Feedback is different in outcomes '
                                       f'when compared to feedback for question'
                                       f' {question.num} in {self.stage_id}. '
                                       f' Feedback is "{outcome_value}" in '
                                       f'outcomes but "{feedbacks_value}" in'
                                       f'feedbacks.')

            existing_feedback = outcome['value']

            self._possible_outcomes[question_id] = \
                outcomes.Outcome('input', question.text, existing_feedback)

        # generate UI elements
        w = urwid.Edit('', existing_feedback, multiline=True)
        urwid.connect_signal(w,
                            'postchange',
                            self._on_edit_change,
                            question_id)
        w = urwid.AttrMap(w, 'edit', 'edit selected')
        return [w]

    def status_check(self, refresh_output=True):
        """
        Determine if all the required questions have been completed and if
        so, update the status of this stage.
        """
        if len(self.required_not_completed) == 0:
            focus_path = self.window.frame.get_focus_path()

            result = stage.StageResult(stage.StageResult.RESULT_PASS_NONFINAL)
            if refresh_output:
                result.set_output(self.outputform)
            self.controller.report(result, self.stage_id)

            self.window.frame.set_focus_path(focus_path)

    def _on_radio_check(self, w, state, user_data):
        """
        Callback when the user has selected a radio in a group (called for
        both when one is selected and one is deselected).
        """
        self._last_selected_widget = w

        question_id  = user_data[0]
        score_id     = user_data[1]
        
        question     = self.questions[question_id]
        required     = question.required

        if state:
            score    = float(self.questions[question_id].scores[score_id])
            feedback = self.questions[question_id].feedback[score_id]

            outcome = self._possible_outcomes[question_id]
            outcome['key']   = score_id
            outcome['value'] = score
            outcome['all_values'] = question.scale

            self.add_score(question.num, score)
            self.add_feedback(question.num, feedback)
            self.set_outcome(question.num, outcome)

            if question_id in self.required_not_completed:
                self.required_not_completed.remove(question.num)
        elif required:
            self.required_not_completed.add(question.num)

        self.status_check()

    def _on_edit_change(self, w, old_value, question_id):
        """
        Callback for when any edit text box is updated. Appropriate action
        depends on what the box is containing.
        """
        if self._skip_on_edit_change == w:
            self._skip_on_edit_change = None
            return

        self._last_selected_widget = w

        value = w.get_edit_text()
        q = self.questions[question_id]

        outcome = self._possible_outcomes[question_id]

        if q.type == stage.OutputForm.Question.TYPE_INPUT_SCORE:
            try:
                value = float(value) if value is not None else 0.0

                if q.score_min != False and value < q.score_min:
                    value = q.score_min
                    strvalue = str(value)
                    if int(value) == value:
                        strvalue = str(int(value))

                    self._skip_on_edit_change = w
                    w.set_edit_text(strvalue)

                if q.score_max != False and value > q.score_max:
                    value = q.score_max
                    strvalue = str(value)
                    if int(value) == value:
                        strvalue = str(int(value))

                    self._skip_on_edit_change = w
                    w.set_edit_text(strvalue)

                outcome['value'] = value

                self.add_score(q.num, value)
                self.set_outcome(q.num, outcome)
            except ValueError:
                if q.score_min != False:
                    outcome['value'] = value
                    self.add_score(q.num, q.score_min)
                    self.set_outcome(q.num, outcome)
                else:
                    outcome['value'] = 0.0
                    self.add_score(q.num, 0.0)
                    self.set_outcome(q.num, outcome)
        elif q.type == stage.OutputForm.Question.TYPE_INPUT_FEEDBACK:
            value = value if value is not None else ''
            self.add_feedback(q.num, value)

            outcome['value'] = value
            self.set_outcome(q.num, outcome)



class AdapterMarker(AdapterBase):
    def set(self, output):
        """
        Create an interactive form to be completed by the user. Similar to 
        AdapterForm, but every field is an input score text field.
        """
        self.outputform = output

        contents = []
        current_headings = None
        min_question_width = 20

        self.outcomes    = output.outcomes
        self.performance = output.performance

        self._last_selected_widget = None
        self._skip_on_edit_change = None
        
        if len(self.outcomes) == 0:
            contents = [urwid.Text('This stage has no outcomes on a '
                                   'submission\'s score.')]
            super().set(contents)
            return

        # generate output
        for outcome_id, outcome in self.outcomes.items():
            outcome = self.outcomes[outcome_id]

            # column headings
            try:
                if outcome['all_values'] != None:
                    headings = [k[0] for k
                                in outcome['all_values']]
                elif outcome['value'] is None:
                    headings = ['Scale Factor']
                else:
                    headings = ['Mark']
                        
                if current_headings == None or \
                    current_headings != headings:

                    if current_headings != None:
                        contents.append(urwid.Divider())
                        contents.append(urwid.Divider())

                    current_headings = headings

                    w = urwid.Columns([urwid.AttrWrap(
                                        urwid.Padding(urwid.Text(item),
                                                     'center', 'pack'),
                                       'table header')
                                          for item in headings],
                                      dividechars = 1)
                    w = urwid.Columns([
                                        urwid.AttrWrap(urwid.Divider(),
                                                      'table header'),
                                        w],
                                      min_width = min_question_width,
                                      dividechars = 1)

                    contents.append(w)

            except AttributeError:
                contents.append(urwid.Divider())
                current_headings = None

            # generate input fields
            inputs = []
            
            if outcome['all_values'] != None:
                inputs += self._generate_multi_outcome(outcome_id,
                                                       outcome,
                                                       self.performance)
            else:
                inputs += self._generate_single_outcome(outcome_id,
                                                        outcome,
                                                        self.performance)

            # bring it together
            w_inputs        = [uw.JumpableColumns(inputs, dividechars = 1)]
            w_question_text = [urwid.AttrWrap(urwid.Text(outcome.explanation),
                                           'table row')]

            w = urwid.Columns(w_question_text + w_inputs,
                              min_width   = min_question_width,
                              dividechars = 1)

            contents.append(urwid.Divider())
            contents.append(w)
            contents.append(urwid.Divider())

        self.view_focus = [1]

        super().set(contents)

        focus_path = self.window.frame.get_focus_path()

        result = stage.StageResult(stage.StageResult.RESULT_PASS_NONFINAL)
        self.controller.report(result, self.stage_id)

        self.window.frame.set_focus_path(focus_path)

    def _generate_multi_outcome(self, outcome_id, outcome, performance):
        existing_score = None

        # generate UI elements
        inputs = []
        
        for mark_id, value in enumerate(outcome.all_values):
            the_value = value[1]
            # replace value if in model
            model_value = self.marks[self.stage_id][outcome_id]\
                    [str(mark_id)]
            if model_value is not None:
                mark = model_value
            else:
                self.set_mark(outcome_id,
                              mark_id,
                              float(mark))
            
            ws = []
            w = urwid.Edit('',
                           str(mark),
                           align = 'center')
            urwid.connect_signal(w,
                                'postchange',
                                self._on_edit_change,
                                (outcome_id, mark_id))
            w = urwid.AttrMap(w, 'edit', 'edit selected')
            ws.append(w)

            num_scores = performance[outcome_id]
            num_submissions = num_scores[value[0]]
            total_submissions = sum(num_scores.values())
            percent_submissions = num_submissions/total_submissions*100
        
            w = urwid.Text(f'{num_submissions}/{total_submissions} '
                           f'{percent_submissions:.2f}%')
            w = urwid.Padding(w, 'center', 'pack')
            w = urwid.AttrMap(w, 'faded')
            ws.append(w)

            inputs.append(urwid.Pile(ws))

        return inputs

    def _generate_single_outcome(self, outcome_id, outcome, performance):
        existing_score = None
        ws = []

        num_submissions = performance[outcome_id]
        total_submissions = 0
        percent_submissions = 0
        try:
            try:
                total_submissions += performance[outcome_id]
            except:
                total_submissions += sum(performance.values())
            percent_submissions = num_submissions/total_submissions*100
        except:
            pass
        
        # if the value is None, this is an input field without a preset value
        # therefore scores can be scaled only
        if outcome.value is None:
            mark = str(1.0)
        else:
            mark = str(outcome.value)

        # replace value if in model
        model_value = self.marks[self.stage_id][outcome_id]
        if model_value is not None:
            mark = str(model_value)
        else:
            self.set_mark(outcome_id,
                          None,
                          float(mark))

        # generate UI elements
        w = urwid.Edit('',
                       mark,
                       align = 'center')
        urwid.connect_signal(w,
                            'postchange',
                            self._on_edit_change,
                            (outcome_id, None))
        w = urwid.AttrMap(w, 'edit', 'edit selected')
        ws.append(w)

        
        w = urwid.Text(f'{num_submissions}/{total_submissions} '
                       f'{percent_submissions:.2f}%')
        w = urwid.Padding(w, 'center', 'pack')
        w = urwid.AttrMap(w, 'faded')
        ws.append(w)
        
        return [urwid.Pile(ws)]

    def _on_edit_change(self, w, old_value, outcome_ids):
        """
        Callback for when any edit text box is updated.
        """
        if self._skip_on_edit_change == w:
            self._skip_on_edit_change = None
            return

        self._last_selected_widget = w

        value = w.get_edit_text()

        outcome_id = outcome_ids[0]

        mark_id = None
        if outcome_ids[1] is not None:
            mark_id = outcome_ids[1]

        try:
            value = float(value) if value is not None else 0.0
            self.set_mark(outcome_id, mark_id, value)
        except ValueError:
            self.set_mark(outcome_id, mark_id, 0.0)