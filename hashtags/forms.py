from django import forms
from django.contrib.auth.models import User

from .models import Comment, Hashtag


class CreateHashtagForm(forms.ModelForm):
	tag = forms.CharField(required=True, widget=forms.TextInput(
		attrs={'placeholder': 'myhashtag'}
	))
	description = forms.CharField(required=True, widget=forms.TextInput(
		attrs={'placeholder': 'This is my awesome hashtag!'}
	))

	class Meta:
		model = Hashtag
		fields = ['tag', 'description']

	def __init__(self, *args, **kwargs):
	    super(CreateHashtagForm, self).__init__(*args, **kwargs)
	    self.fields['tag'].widget.attrs['class'] = 'span2'
	    self.fields['description'].widget.attrs['class'] = 'span5 hash-desc'


class CreateCommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['comment']

