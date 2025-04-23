from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.db.models import F
from .models import Artist, ProjectManager, Summary, Task, CheckinResponse
from django.http import JsonResponse
import openai
import json
from django.conf import settings
import logging
from adam.models import Artist
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

def view_summary(request):
    return render(request, "adam/team_report.html", {"summaries": Summary.objects.all()})

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def refresh_session(request):
    request.session.flush()
    return JsonResponse({"reply": "Session refreshed."})


def do_check_in(request):
    artist = Artist.objects.get(user__username="joe")  # Temporary for testing purposes

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "")

            # Artist check-in logic
            step = request.session.get('checkin_step', 0)

            if step < len(CHECKIN_QUESTIONS):
                # Record answer if not the first question
                if step > 0:
                    CheckinResponse.objects.create(
                        artist=artist,
                        question=CHECKIN_QUESTIONS[step - 1],
                        answer=user_input,
                        session_key=request.session.session_key
                    )

                # Ask next question
                next_question = CHECKIN_QUESTIONS[step]
                request.session['checkin_step'] = step + 1
                request.session.modified = True
                return JsonResponse({"reply": next_question})

            else:
                # Record final response
                CheckinResponse.objects.create(
                    artist=artist,
                    question=CHECKIN_QUESTIONS[-1],
                    answer=user_input,
                    session_key=request.session.session_key
                )

                conversation = [
                { "role": "system", 
                         "content": "You are A.D.A.M. (Automated Digital Assistant for Management), an AI project manager specializing in 3D animation and game dev pipelines.\
                                    You help teams track progress, assign tasks, answer scheduling questions, and summarize project status. Be concise, organized, and friendly."
                        },
                ]

                for cr in CheckinResponse.objects.filter(session_key=request.session.session_key):
                    conversation.append({
                        "role": "assistant",
                        "content":cr.question
                    })
                    conversation.append({
                        "role": "user",
                        "content":cr.answer
                    })

                conversation.append({
                        "role": "assistant",
                        "content":"Is there any other information you would like to share?"
                    })
                conversation.append({
                        "role": "user",
                        "content":"No, please summarize my responses in the third person."
                    })
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=conversation,
                )

                # response = client.chat.completions.create(
                #     model="gpt-3.5-turbo",
                #     messages=[
                #         {
                #             "role": "system",
                #             "content": f"You are A.D.A.M. (Automated Digital Assistant for Management). Here are the team's current tasks:\n{task_summary}"
                #         },
                #         {
                #             "role": "user",
                #             "content": user_input
                #         }
                #     ]
                # )
                reply = response.choices[0].message.content
                print(reply)
                Summary.objects.create(
                    artist=artist,
                    summary=reply,
                )

                # Reset for next check-in
                request.session.flush()
                request.session['checkin_step'] = 0
                request.session.modified = True
                return JsonResponse({"reply": "Thank you! Your check-in is complete and responses recorded."})

        except Exception as e:
            return JsonResponse({"reply": f"Server error: {str(e)}"})

    return JsonResponse({"reply": "Please send a message to begin."})