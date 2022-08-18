"""Define URLS pattern for 8Trigrams  wallet"""

from django.urls import path
from . import views

app_name = 'wallet'
urlpatterns = [       
    #user dashboatd/home page
    path('', views.dashboard, name='dashboard'),
    #send page
    path('send_page', views.send_page, name='send_page'),
    #send btc
    path('send', views.send, name="send"),
]