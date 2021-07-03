# -*- coding: utf-8 -*-

from .. import config, stage
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
        self.scores     = model['scores'][controller.submission]
        self.feedbacks  = model['feedbacks'][controller.submission]
        self.window     = window
        self.result     = None

        # where the UI should focus
        self.view_focus   = None

        # initial score
        score_init = config.ini[f'stage_{stage_id}'].getfloat(
            'score_init', None)
        if score_init:
            self.add_score('__init', score_init)

    def set(self, output):
        """
        Update the output, forcing the adapter to re-adapt it to urwid
        components.
        """
        self.output = [urwid.Text('This stage has no output adapter.')]

    def add_score(self, score_id, score):
        """
        Add to the submission's score (calls through to the model).
        """
        self.controller.add_score(self.stage_id,
                                  score_id,
                                  score)

    def add_feedback(self, feedback_id, feedback):
        """
        Add to the submission's feedback (calls through to the model).
        """
        self.controller.add_feedback(self.stage_id,
                                     feedback_id,
                                     feedback)



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
        scale-based questions, score input text fields, feedback input fields
        and weight input text fields (the latter three are all simple EditText
        widgets).
        """
        self.outputform = output

        contents = []
        current_scale = None
        temp_contents = []
        min_question_width = 20

        self.questions = output.questions
        self.required_not_completed = set()
        self._last_selected_widget = None
        self._skip_on_edit_change = None

        # self._scores    = [0] * len(output.questions)
        # self._feedbacks = [''] * len(output.questions)

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

            text = question.text
            if question.min_score != False:
                text += ' (min: ' + str(question.min_score)
                if question.max_score:
                    text += ', max: ' + str(question.max_score) + ')'
                else:
                    text += ')'
            elif question.max_score != False:
                text += ' (max: ' + str(question.max_score) + ')'

            if question.required:
                text += ' *'

            # existing values in the model?
            if question_id in self.scores[self.stage_id]:
                existing_score_f = self.scores[self.stage_id][question_id]
                existing_score_s = str(existing_score_f)
            else:
                existing_score_f = None
                existing_score_s = ''

                self.add_score(question_id, 0.0)

            existing_feedback = ''
            if question_id in self.feedbacks[self.stage_id]:
                existing_feedback = self.feedbacks[self.stage_id][question_id]
            elif question.type == stage.OutputForm.Question.TYPE_SCALE and \
                        existing_score_f is not None:
                try:
                    pos = question.scores.index(existing_score_f)
                    existing_feedback = question.feedback[pos]
                except ValueError:
                    existing_score_f = None
                    existing_score_s = ''
                    self.add_score(question_id, 0.0)

                self.add_feedback(question_id, existing_feedback)

            # show question per row
            question_text = [urwid.AttrWrap(urwid.Text(text),
                                           'table row')]

            inputs = []
            if question.type == stage.OutputForm.Question.TYPE_SCALE:
                if question.required and existing_score_f is None:
                    self.required_not_completed.add(question_id)

                max_score = '/' + str(max(question.scores))
                radio_group = []
                for score_id, score in enumerate(question.scores):
                    checked = False
                    if existing_score_f == float(score):
                        checked = True

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
            elif question.type == stage.OutputForm.Question.TYPE_INPUT_SCORE:
                if question.required and len(existing_score_s) == 0:
                    self.required_not_completed.add(question_id)

                w = urwid.Edit('',
                               existing_score_s,
                               align = 'center')
                urwid.connect_signal(w,
                                    'postchange',
                                    self._on_edit_change,
                                    question_id)
                w = urwid.AttrMap(w, 'edit', 'edit selected')
                inputs.append(w)
            elif question.type == stage.OutputForm.Question.TYPE_INPUT_FEEDBACK:
                if question.required and len(existing_feedback) == 0:
                    self.required_not_completed.add(question_id)

                w = urwid.Edit('', existing_feedback, multiline=True)
                urwid.connect_signal(w,
                                    'postchange',
                                    self._on_edit_change,
                                    question_id)
                w = urwid.AttrMap(w, 'edit', 'edit selected')
                inputs.append(w)


            w_inputs = [uw.JumpableColumns(inputs, dividechars = 1)]
            w = urwid.Columns(question_text + w_inputs,
                              min_width   = min_question_width,
                              dividechars = 1)

            contents.append(urwid.Divider())
            contents.append(w)
            contents.append(urwid.Divider())

        self.view_focus = [1]

        super().set(contents)

        if len(self.required_not_completed) == 0:
            self.status_check(False)

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
        required     = self.questions[question_id].required

        if state:
            score    = self.questions[question_id].scores[score_id]
            feedback = self.questions[question_id].feedback[score_id]

            self.add_score(question_id, float(score))
            self.add_feedback(question_id, feedback)

            if question_id in self.required_not_completed:
                self.required_not_completed.remove(question_id)
        elif required:
            self.required_not_completed.add(question_id)

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

        # question = self.questions[user_data]
        value = w.get_edit_text()
        q = self.questions[question_id]
        if q.type == stage.OutputForm.Question.TYPE_INPUT_SCORE:
            try:
                value = float(value) if value is not None else 0.0

                if q.min_score != False and value < q.min_score:
                    value = q.min_score
                    strvalue = str(value)
                    if int(value) == value:
                        strvalue = str(int(value))

                    self._skip_on_edit_change = w
                    w.set_edit_text(strvalue)

                if q.max_score != False and value > q.max_score:
                    value = q.max_score
                    strvalue = str(value)
                    if int(value) == value:
                        strvalue = str(int(value))

                    self._skip_on_edit_change = w
                    w.set_edit_text(strvalue)

                self.add_score(question_id, value)
            except ValueError:
                if q.min_score != False:
                    self.add_score(question_id, q.min_score)
                else:
                    self.add_score(question_id, 0.0)
        elif q.type == stage.OutputForm.Question.TYPE_INPUT_FEEDBACK:
            value = value if value is not None else ''
            self.add_feedback(question_id, value)
