"""
forms.py
---------
Defines the WTForms form used by the application.

GenresForm contains a SelectMultipleField rendered as a list of checkboxes
and a submit button. The form object is created in `app.index` and its
`chosen_genres.choices` attribute is populated at runtime from the
`GENRES` list in `app.py`.

Notes:
- The SelectMultipleField sends multiple values under the same field name
    when checkboxes are selected; on the server use `request.form.getlist`
    to read all selected values.
- The field uses `ListWidget` + `CheckboxInput` so each choice becomes a
    separate checkbox element in the rendered HTML.
"""

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired


class GenresForm(FlaskForm):
        chosen_genres = SelectMultipleField('Select Genres',
                                    option_widget=CheckboxInput(),
                                    widget=ListWidget(prefix_label=False))
        submit = SubmitField('Submit')
        """Form for selecting one or more movie genres.

        Fields:
        - chosen_genres: SelectMultipleField rendered as checkboxes. Choices are
            injected at runtime by the caller (app.index) as a list of (value,
            label) tuples. Values should be strings (WTForms requirement).
        - submit: Simple submit button.
        """

        # The label 'Select Genres' will be used by helpers that render the
        # whole field, but in the template we iterate through `chosen_genres`
        # subfields to render each checkbox individually.
        chosen_genres = SelectMultipleField('Select Genres',
                                                                                option_widget=CheckboxInput(),
                                                                                widget=ListWidget(prefix_label=False))

        # Submit button used to POST the form.
        submit = SubmitField('Submit')





