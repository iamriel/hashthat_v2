import redis
import tweepy

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic.base import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from instagram.client import InstagramAPI

from hashthat.mixins import LoginRequiredMixin

from .forms import CreateHashtagForm, CreateCommentForm
from .models import Comment, Hashtag


class CreateHashtagView(CreateView):
	model = Hashtag
	template_name = 'hashtags/parts/create_hashtag.html'
	form_class = CreateHashtagForm

	def get(self, request, *args, **kwargs):
		self.object = None
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		context = self.get_context_data(form=form)
		if request.is_ajax():
			return super(CreateHashtagView, self).render_to_response(context)
		else:
			return HttpResponse()

	def form_valid(self, form):
		"""
		If the request is ajax, save the form and return a json response.
		Otherwise return super as expected.
		"""
		user = self.request.user
		if self.request.is_ajax():
			self.template_name = 'hashtags/parts/hashtag-feed.html'
			self.object = form.save(commit=False)
			self.object.author = user
			self.object.save()
			context = self.get_context_data(hashtag=self.object)
			return super(CreateHashtagView, self).render_to_response(context)
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


class HashtagDetailView(DetailView):
	model = Hashtag
	template_name = 'hashtags/details.html'


class HashtagVoteView(View):
	def get(self, request, *args, **kwargs):
		context = {
			'success': False,
		}
		if not request.user.is_authenticated():
			context.update({'unauthenticated': True})
			return HttpResponse(json.dumps(context), mimetype="application/json")
		
		if 'id' in request.GET and 'mode' in request.GET:
			user = request.user
			hashtag_id = request.GET.get('id')
			mode = request.GET.get('mode')
			hashtag = Hashtag.objects.get(id=hashtag_id)
			if mode == 'up-vote':
				hashtag.up_vote.add(user)
				hashtag.down_vote.remove(user)
			else:
				hashtag.down_vote.add(user)
				hashtag.up_vote.remove(user)
			hashtag.save()
			context.update({
				'success': True,
				'votes': hashtag.votes,
			})

		if self.request.is_ajax():
			return HttpResponse(json.dumps(context), mimetype="application/json")


class InstagramRelatedListView(ListView):
	client_id = settings.INSTAGRAM_CLIENT_ID
	client_secret = settings.INSTAGRAM_CLIENT_SECRET
	api = InstagramAPI(client_id=client_id, client_secret=client_secret)

	context_object_name = 'insta_media'
	template_name = 'hashtags/instagram/instagram_list.html'

	def get_queryset(self):
		hashtag = self.kwargs['hashtag']
		queryset = self.api.tag_recent_media(tag_name=hashtag)[0]
		return queryset


class TwitterRelatedListView(ListView):
	consumer_key = settings.TWITTER_CONSUMER_KEY
	consumer_secret = settings.TWITTER_CONSUMER_SECRET
	access_token = settings.TWITTER_ACCESS_TOKEN
	access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	context_object_name = 'tweets'
	template_name = 'hashtags/twitter/tweet_list.html'

	def get_queryset(self):
		hashtag = '#%s' % self.kwargs['hashtag']
		if 'max_id' in self.request.GET:
			max_id = int(self.request.GET.get('max_id'))
			queryset = self.api.search(q=hashtag, count=10, max_id=max_id)
		else:
			queryset = self.api.search(q=hashtag, count=10)
		return queryset


class YoutubeRelatedListView(ListView):
	developer_key = settings.YOUTUBE_DEVELOPER_KEY
	youtube_api_service_name = 'youtube'
	youtube_api_version = 'v3'

	def get_queryset(self):
		hashtag = self.kwargs['hashtag']
		youtube = build(youtube_api_service_name, youtube_api_version,
			developerKey=developer_key)

		# Call the search.list method to retrieve results matching the specified
		# query term
		search_response = youtube.search().list(
			q=hashtag,
			maxResults=15
		).execute()


@csrf_exempt
def create_comment(request, template_name = 'hashtags/parts/create_comment.html'):
	try:
		#Get User from sessionid
		session = Session.objects.get(session_key=request.POST.get('sessionid'))
		user_id = session.get_decoded().get('_auth_user_id')
		user = User.objects.get(id=user_id)

		#Create comment
		comment = Comment.objects.create(author=user, comment=request.POST.get('comment'))

		hashtag_id = request.POST.get('hashtag_id')
		hashtag = Hashtag.objects.get(id=hashtag_id)
		hashtag.comments.add(comment)
		hashtag.save()
		context = {
			'comment': comment,
		}

		rendered = render_to_string(template_name, context)

		response = {
			'div_id': '#comment-%s' % hashtag_id,
			'data': rendered,
		}
		#Once comment has been created post it to the chat channel
		r = redis.StrictRedis(host='localhost', port=6379, db=0)
		r.publish('comment', json.dumps(response))

		return HttpResponse("Everything worked :)")
	except Exception, e:
		return HttpResponseServerError(str(e))
	