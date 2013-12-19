from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.views.generic import CreateView, FormView, UpdateView
from django.views.decorators.csrf import ensure_csrf_cookie

from hashthat.mixins import LoginRequiredMixin

from .forms import LoginForm, SignupForm, UpdateProfileForm
from accounts.models import UserProfile


class LoginView(FormView):
	template_name = 'modals/modal-sign-in.html'
	form_class = LoginForm
	success_url = '/'

	def get(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		context = self.get_context_data(form=form)
		if request.is_ajax():
			return super(LoginView, self).render_to_response(context)
		else:
			return HttpResponse

	def form_valid(self, form):
		"""
		If the request is ajax, save the form and return a json response.
		Otherwise return super as expected.
		"""
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		try:
			user = User.objects.get(email__iexact=username)
			username = user.username
		except User.DoesNotExist:
			pass
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(self.request, user)
				return HttpResponse(json.dumps('success'), mimetype='application/json')
			else:
				if self.request.is_ajax():
					return HttpResponse(json.dumps({'error': 'Inactive User'}), mimetype='application/json')
		else:
			if self.request.is_ajax():
				return HttpResponse(json.dumps({'error': 'Ivalid username and password'}), mimetype='application/json')
		return super(LoginView, self).form_valid(form)

	def form_invalid(self, form):
		"""
		We haz errors in the form. If ajax, return them as json.
		Otherwise, proceed as normal.
		"""
		if self.request.is_ajax():
			return HttpResponse(json.dumps(form.errors), mimetype="application/json")
		return super(LoginView, self).form_invalid(form)

	def render_to_response(self, context, **response_kwargs):
		rendered = render_to_string(self.template_name, context_instance=context)
		return HttpResponse(rendered)


class SignupView(CreateView):
	model = User
	template_name = 'modals/modal-sign-up.html'
	form_class = SignupForm

	def get(self, request, *args, **kwargs):
		self.object = None
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		context = self.get_context_data(form=form)
		if request.is_ajax():
			return super(SignupView, self).render_to_response(context)
		else:
			return HttpResponse()

	def form_valid(self, form):
		"""
		If the request is ajax, save the form and return a json response.
		Otherwise return super as expected.
		"""
		password = form.cleaned_data['password']
		if self.request.is_ajax():
			self.object = form.save()
			self.object.set_password(password)
			self.object.save()
			return HttpResponse(json.dumps("success"), mimetype="application/json")
		return super(SignupView, self).form_valid(form)

	def form_invalid(self, form):
		"""
		We haz errors in the form. If ajax, return them as json.
		Otherwise, proceed as normal.
		"""
		if self.request.is_ajax():
			return HttpResponse(json.dumps(form.errors), mimetype="application/json")
		return super(SignupView, self).form_invalid(form)

	def render_to_response(self, context, **response_kwargs):
		rendered = render_to_string(self.template_name, context_instance=context)
		return HttpResponse(rendered)


class ProfileUpdateView(LoginRequiredMixin, CreateView):
	model = UserProfile
	form_class = UpdateProfileForm
	template_name = 'accounts/settings.html'
	user = None

	def get(self, request, *args, **kwargs):
		self.object = None
		form_class = self.get_form_class()
		user_form = self.get_form(form_class)
		context = self.get_context_data(user_form=user_form)
		return render(request, self.template_name, context)

	def form_valid(self, form):
		"""
		If the request is ajax, save the form and return a json response.
		Otherwise return super as expected.
		"""
		if self.request.is_ajax():
			self.object = form.save()
			print self.object.middle_name
			return HttpResponse(json.dumps("success"), mimetype="application/json")
		return super(SignupView, self).form_valid(form)

	def form_invalid(self, form):
		"""
		We haz errors in the form. If ajax, return them as json.
		Otherwise, proceed as normal.
		"""
		if self.request.is_ajax():
			return HttpResponse(json.dumps(form.errors), mimetype="application/json")
		return super(SignupView, self).form_invalid(form)

	def get_initial(self):
		self.user = self.request.user
		data = {
			'username': self.user.username,
			'email': self.user.email,
			'first_name': self.user.first_name,
			'last_name': self.user.last_name,
		}
		return data

	def get_form_kwargs(self):
		kwargs = super(ProfileUpdateView, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs