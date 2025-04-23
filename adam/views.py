from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.db.models import F
from .models import Answer, Question, Artist, ProjectManager, Form, Report, Task, ConversationSession, ConversationMessage, CheckinResponse
from django.http import JsonResponse
import openai
import json
from django.conf import settings
import logging
from adam.models import Artist, Question, Answer
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
# Create your views here.

CHECKIN_QUESTIONS = [
    "What did you work on today?",
    "Did you face any challenges?",
    "How much progress did you make (%) on your current task?",
    "Do you think you'll meet your next deadline?",
    "Anything blocking your work?",
]

def team_report(request, team_id):
    artists = get_list_or_404(Artist, team_id = team_id)
    return render(request, "adam/team_report.html", {"artists": artists})

def home(request):
    return render(request, "adam/index.html")

def chat_view(request):
    return render(request, "adam/index.html")

def teams(request):
    return render(request, "adam/teams.html")

def profile(request):
    return render(request, "adam/profile.html")

def about(request):
    return render(request, "adam/about.html")

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def chatbot_api(request):
    user = User.objects.get(username="artist1")  # Temporary for testing purposes
    
    tasks = Task.objects.filter(artist__user=user)
    task_summary = "\n".join([f"- {t.description} ({t.progress}%)" for t in tasks])

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "")

            if hasattr(user, 'artist'):
                # Artist check-in logic
                step = request.session.get('checkin_step', 0)

                if step < len(CHECKIN_QUESTIONS):
                    # Record answer if not the first question
                    if step > 0:
                        CheckinResponse.objects.create(
                            user=user,
                            question=CHECKIN_QUESTIONS[step - 1],
                            answer=user_input
                        )

                    # Ask next question
                    next_question = CHECKIN_QUESTIONS[step]
                    request.session['checkin_step'] = step + 1
                    request.session.modified = True
                    return JsonResponse({"reply": next_question})

                else:
                    # Record final response
                    CheckinResponse.objects.create(
                        user=user,
                        question=CHECKIN_QUESTIONS[-1],
                        answer=user_input
                    )

                    # Reset for next check-in
                    request.session['checkin_step'] = 0
                    request.session.modified = True
                    return JsonResponse({"reply": "Thank you! Your check-in is complete and responses recorded."})

            else:
                # Project Manager (or other roles): Regular GPT response
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are A.D.A.M. (Automated Digital Assistant for Management). Here are the team's current tasks:\n{task_summary}"
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                )
                reply = response.choices[0].message.content
                return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"reply": f"Server error: {str(e)}"})

    return JsonResponse({"reply": "Please send a message to begin."})