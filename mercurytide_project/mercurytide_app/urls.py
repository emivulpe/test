from django.conf.urls import patterns, url
from mercurytide_app import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
        url(r'^register/$', views.register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        )