from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views

app_name = "adam"

path("login/", LoginView.as_view(), name="login")

urlpatterns = [
    
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # ← this line enables login/logout
    path("", include("capstone.urls")),  # or your app's main urls
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    # ex: /adam/
    path("", views.home, name="home"),
    path("", views.chat_view, name="home"),
    path("chatbot-api/", views.chatbot_api, name="chatbot_api"),
    path("teams", views.teams, name="teams"),
    # ex: /adam/teams/teamID
    path("teams/<int:team_id>/", views.team_report, name="team_report"),
    # ex: /adam/profile
    path("profile", views.profile, name="profile"),
    # ex: /adam/about
    path("about", views.about, name="about"),
    path("chat/<int:session_id>/", views.view_conversation, name="view_conversation"),
    path("chat/new/", views.new_chat_session, name="new_chat"),
    path('', views.home, name='home'),
]

