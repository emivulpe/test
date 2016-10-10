from django.conf.urls import patterns, url
from mercurytide_app import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^report/$', views.create_report, name='report'),
        )