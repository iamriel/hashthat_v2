from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import (
	CreateHashtagView,
	create_comment,
	HashtagDetailView,
	HashtagVoteView,
	InstagramRelatedListView,
	TwitterRelatedListView,
)

urlpatterns = patterns('',
    url(r'^create', CreateHashtagView.as_view(), name='create-hashtag'),
    url(r'^comments/create', create_comment, name='create-comment'),
    url(r'^vote/', HashtagVoteView.as_view(), name='hashtag-vote'),
    url(r'^instagram/(?P<hashtag>[-_\w]+)/$', InstagramRelatedListView.as_view(), name='hashtag-instagram'),
    url(r'^twitter/(?P<hashtag>[-_\w]+)/', TwitterRelatedListView.as_view(), name='hashtag-twitter'),
    url(r'^(?P<slug>[-_\w]+)/$', HashtagDetailView.as_view(), name='hashtag-detail'),
)
