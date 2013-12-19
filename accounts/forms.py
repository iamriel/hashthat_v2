from django import forms
from django.contrib.auth.models import User

from .models import UserProfile


class LoginForm(forms.Form):
	username = forms.CharField(max_length=50, label='Email or username')
	password = forms.CharField(widget=forms.PasswordInput)
	remember = forms.BooleanField(required=False)


class SignupForm(forms.ModelForm):
	email = forms.EmailField()
	confirm_email = forms.EmailField(label='Re-enter email')
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ['username', 'email', 'confirm_email', 'password']

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			user = User.objects.get(username__iexact=username)
		except User.DoesNotExist:
			return username
		raise forms.ValidationError(u'Username %s already exists' % username)

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			user = User.objects.get(email__iexact=email)
		except User.DoesNotExist:
			return email
		raise forms.ValidationError(u'User with email %s already exists' % email)

	def clean_confirm_email(self):
		email = self.cleaned_data['email']
		confirm_email = self.cleaned_data['confirm_email']
		if email != confirm_email:
			raise forms.ValidationError(u'Emails do not match')
		return confirm_email


class UpdateProfileForm(forms.ModelForm):
	username = forms.CharField(max_length=255)
	email = forms.EmailField()
	first_name = forms.CharField(max_length=255)
	last_name = forms.CharField(max_length=255)

	class Meta:
		model = UserProfile
		fields = ['username', 'email', 'first_name', 'middle_name', 'last_name']

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super(UpdateProfileForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		# profile = super(forms.ModelForm, self).save(commit=False)
		profile = self.request.user.profile
		profile.user.username = self.cleaned_data['username']
		profile.user.email = self.cleaned_data['email']
		profile.user.first_name = self.cleaned_data['first_name']
		profile.user.last_name = self.cleaned_data['last_name']
		if commit:
			profile.save()
			profile.user.save()
		return profile

	def clean_username(self):
		username = self.cleaned_data['username']
		user_username = self.request.user.username

		if username != user_username:
			try:
				user = User.objects.get(username__iexact=username)
				raise forms.ValidationError(u'Username %s already exists' % username)
			except User.DoesNotExist:
				pass
		return username

	def clean_email(self):
		email = self.cleaned_data['email']
		user_email = self.request.user.email

		if email != user_email:
			try:
				user = User.objects.get(email__iexact=email)
				raise forms.ValidationError(u'User with email %s already exists' % email)
			except User.DoesNotExist:
				pass
		return email
