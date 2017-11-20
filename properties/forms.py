from django import forms

from .models import Property

VIEW_TYPE = (
    ('Local Map', 'Local Map'),
)
YEAR_OPTIONS = ((str(x), str(x)) for x in range(2012, 2017))
RESULT_TYPES = (
    ('Deeded', 'DEED'),
    ('Not Deeded', 'R'),
    ('All Types', 'All')
)
class SimpleForm(forms.Form):

    view_type = forms.ChoiceField(
        required=True,
        choices=VIEW_TYPE,
    )
    year_options = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=YEAR_OPTIONS,
    )
    result_types = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=RESULT_TYPES,
    )