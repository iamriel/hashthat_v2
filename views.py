from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.views.generic import ListView, TemplateView

from hashtags.models import Hashtag

class HomeView(TemplateView):
	template_name = 'index.html'

	def get(self, request, *args, **kwargs):
		popular = sorted(Hashtag.objects.all(),
			key=lambda m: m.comment_count, reverse=True)[0]
		hashtags = Hashtag.objects.all().exclude(id=popular.id).order_by('-modified')[:4]
		context = {
			'hashtags': hashtags,
			'popular': popular,
		}
		return render(request, self.template_name, context)


class TimelineView(ListView):
	template_name = 'accounts/timeline.html'
	context_object_name = 'hashtags'

	def get_queryset(self):
		username = self.kwargs['username']
		user = User.objects.get(username=username)
		hashtags = Hashtag.objects.filter(author=user).order_by('-modified')
		return hashtags

