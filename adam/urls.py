from django.urls import path

from . import views

app_name = "adam"

urlpatterns = [
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
    
]

