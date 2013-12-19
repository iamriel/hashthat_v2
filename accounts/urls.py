from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import LoginView, SignupView, ProfileUpdateView

urlpatterns = patterns('',
    url(r'^login', LoginView.as_view(), name='login'),
    url(r'^signup', SignupView.as_view(), name='signup'),
    url(r'^settings', ProfileUpdateView.as_view(), name='account-settings'),
)
