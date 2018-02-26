from django.conf.urls import url

from . import views

app_name = "deck"

urlpatterns = [
    url(r'^test/$', views.test, name='test'),
    url(r'^test_visual/$', views.test_visual, name='test_visual'),
    url(r'^generate_deck/$', views.generate_deck, name='generate_deck'),
    url(r'^make_move/$', views.make_move, name='make_move'),
    url(r'^show/$', views.show, name='show'),
]
