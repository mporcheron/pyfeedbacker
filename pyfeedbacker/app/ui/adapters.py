# -*- coding: utf-8 -*-

from .. import config, stage
from . import widgets as uw

import urwid


class AdapterNone:
    def __init__(self, stage_id, controller, model, window):
        self.output    = [urwid.Text('This stage has no output.')]

        self.stage_id   = stage_id
        self.controller = controller
        self.model      = model
        self.window     = window

        # where the UI should focus
        self.ui_focus   = None
        
        # initial score
        score_init = config.ini[f'stage_{stage_id}'].getfloat(
            'score_init', None)
        if score_init:
            self.add_score('__init', score_init)

    def set(self, output):
        self.output = [urwid.Text('This stage has no output adapter.')]

    def add_score(self, model_id, score):
        self.controller.add_score(self.stage_id,
                                  model_id,
                                  score)

    def add_feedback(self, model_id, feedback):
        self.controller.add_feedback(self.stage_id,
                                     model_id,
                                     feedback)
        


class AdapterBase(AdapterNone):
    def set(self, output):
        """
        Sets an output as a pile of contents
        """
        if isinstance(output, list):
            self.output = output
        else:
            self.output = [output]



class AdapterText(AdapterBase):
    def set(self, text):
        """
        Set a stage as a series of urwid Text objects
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

        super(AdapterText, self).set(contents)



class AdapterEditText(AdapterBase):
    def set(self, texts):
        """
        Set a stage as a series of editable text fields
        """
        contents = []
        if isinstance(texts, stage.OutputNone):
            contents = [urwid.Text('An error has occured that has presented '
                                   'this stage fron mexecuting.')]
        else:
            self.outputedittext = texts

            for stage_id, stage_texts in texts.texts.items():
                for model_id, text in stage_texts.items():
                    w = urwid.Edit('', text, multiline=True)
                    urwid.connect_signal(w,
                                        'change',
                                        self._on_edit_change,
                                        (stage_id, model_id))
                    w = urwid.AttrMap(w, 'edit', 'edit selected')
                    contents.append(w)
                contents.append(urwid.Divider())


        super(AdapterEditText, self).set(contents)

    def _on_edit_change(self, w, old_value, user_data):
        value = w.get_edit_text()
        value = value if value is not None else ''
        self.outputedittext.callback(user_data[0], user_data[1], value)





class AdapterChecklist(AdapterText):
    def set(self, output):
        """
        Updates the output for a stage that is a checklist.
        """
        contents = []
        for state, item in output.progress:
            line = ' ✅ ' if state \
                           else (' ❎ ' if state is None else ' ❌ ')
            line += item
            contents.append(line)

        super(AdapterChecklist, self).set(contents)



class AdapterForm(AdapterBase):
    def set(self, output):
        """
        Create an interactive form
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

        self.scores   = [0] * len(output.questions)
        self.feedback = [''] * len(output.questions)

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
                self.required_not_completed.add(question_id)


            # existing value in the model?
            try:
                existing_score_f = \
                    self.model.raw_scores[self.stage_id][question_id]
                existing_score_s = str(existing_score_f)
                if existing_score_s == 'None':
                    existing_score_s = ''
            except KeyError:
                existing_score_f = None
                existing_score_s = ''

                self.add_score(question_id, None)

            try:
                existing_feedback = \
                    self.model.raw_feedback[self.stage_id][question_id]
            except KeyError:
                existing_feedback = ''
                self.add_feedback(question_id, '')

            # show question per row
            question_text = [urwid.AttrWrap(urwid.Text(text),
                                           'table row')]

            inputs = []
            if question.type == stage.OutputForm.Question.TYPE_SCALE:
                max_score = '/' + str(max(question.scores))
                radio_group = []
                for score_id, score in enumerate(question.scores):
                    checked = False
                    if existing_score_f == float(score):
                        checked = True

                    button = urwid.RadioButton(radio_group,
                                               str(score) + max_score,
                                               checked,
                                               self._on_radio_check,
                                               (question_id, score_id))
                    button = urwid.Padding(button, 'center', 'pack')
                    inputs.append(button)
            elif question.type == stage.OutputForm.Question.TYPE_INPUT_SCORE:
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

        self.ui_focus = [1]

        super(AdapterForm, self).set(contents)

    def status_check(self):
        if len(self.required_not_completed) == 0:
            focus_path = self.window.frame.get_focus_path()

            result = stage.StageResult(stage.StageResult.RESULT_PASS)
            result.set_output(self.outputform)
            self.controller.report(result, self.stage_id)

            self.window.frame.set_focus_path(focus_path)

    def _on_radio_check(self, w, state, user_data):
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
