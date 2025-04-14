from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.db.models import F
from .models import Answer, Question, Artist, ProjectManager, Form, Report
# Create your views here.

def team_report(request, team_id):
    artists = get_list_or_404(Artist, team_id = team_id)
    return render(request, "adam/team_report.html", {"artists": artists})

def home(request):
    return render(request, "adam/index.html")

def teams(request):
    return render(request, "adam/teams.html")

def profile(request):
    return render(request, "adam/profile.html")

def about(request):
    return render(request, "adam/about.html")