from django import forms

from movie_app.models import Feedback


class MovieForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        error_messages = {
            'review': {
                'max_length': 'Ой, слишком много символов',
                'min_length': 'Ой, слишком мало символов',
                'required': 'Поле не должно быть пустым',
            }
        }