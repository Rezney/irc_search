from django import forms
from core.models import IRCMessage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field


class SearchForm(forms.Form):
    search_str = forms.CharField(label=False, min_length=2, max_length=30,
                                 required=True)
    author = forms.CharField(label=False, min_length=2, max_length=30, required=False)
    contains = forms.CharField(label=False, min_length=2, max_length=30, required=False)
    not_contain = forms.CharField(label=False, min_length=2, max_length=30,
                                  required=False)
    not_older_then = forms.DateField(label=False, required=False)
    irc_channels = forms.MultipleChoiceField(label=False, choices=lambda: IRCMessage.objects.distinct().values_list('irc_channel', 'irc_channel'))

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.authorhelper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_action = 'results'
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-6 col-md-offset-3'
        self.helper.layout = Layout(
            Field('search_str', placeholder='Search string...'),
            Field('author', placeholder='Author...'),
            Field('contains', placeholder='Also contains...'),
            Field('not_contain', placeholder='Does not contain...'),
            Field('not_older_then', placeholder='Not older then... e.g "2017-05-05"'),
            'irc_channels',
            Submit('search', 'Search', css_class='btn-warning col-md-offset-6'),
        )
