from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired





class GenresForm(FlaskForm):
    chosen_genres = SelectMultipleField('Select Genres',
                                        option_widget=CheckboxInput(),
                                        widget=ListWidget(prefix_label=False))
    submit = SubmitField('Submit')




