from django.urls import path,include
from app import views
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView
urlpatterns = [
    path('',TemplateView.as_view(template_name='signup.html')),
    path('signup_page/',TemplateView.as_view(template_name='signup.html')),
    path('login_page/',TemplateView.as_view(template_name='login.html')),
    path('chat_page/',TemplateView.as_view(template_name='chat.html')),
    path('signup/',views.UserCreate.as_view()),
    path('start_chat/',TemplateView.as_view(template_name='start_chat.html')),
    path('login/', views.CustomAuthToken.as_view()),
    path('logout/',views.Logout.as_view()),
    path('set_preferences/',views.set_preferences),
    path('set_interests/',views.set_interests),
    path('get_preferences_and_interests/',views.get_preferences_and_interests),
    path('get_profile/',views.get_profile),
]