from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.models import F
from .models import Answer, Question, Artist, ProjectManager, Form, Report, Task, ConversationSession, ConversationMessage
from django.http import JsonResponse
import openai
import json
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required
from .utils.decorators import login_or_admin_required

logger = logging.getLogger(__name__)
# Create your views here.

def team_report(request, team_id):
    artists = get_list_or_404(Artist, team_id = team_id)
    return render(request, "adam/team_report.html", {"artists": artists})

def home(request):
	sessions = ConversationSession.objects.filter(user=request.user).order_by('-started_at')
	return render(request, "adam/index.html", {
		"conversation_sessions": sessions
	})
@login_required
def home(request):
    sessions = ConversationSession.objects.filter(user=request.user).order_by('-started_at')
    return render(request, "adam/index.html", {"conversation_sessions": sessions})

def chat_view(request):
    return render(request, "adam/index.html")

def teams(request):
    return render(request, "adam/teams.html")

def profile(request):
    return render(request, "adam/profile.html")

def about(request):
    return render(request, "adam/about.html")

def view_conversation(request, session_id):
	session = get_object_or_404(ConversationSession, id=session_id, user=request.user)
	messages = session.messages.order_by('timestamp')  # oldest first
	sessions = ConversationSession.objects.filter(user=request.user).order_by('-started_at')

	return render(request, "adam/index.html", {
		"conversation_sessions": sessions,
		"messages": messages,
		"active_session": session
	})

def new_chat_session(request):
    if not request.user.is_authenticated:
        return redirect("login")  # Or your login route

    # Create a new session
    session = ConversationSession.objects.create(user=request.user)

    # Optional: add a welcome message
    # from .models import ConversationMessage
    # ConversationMessage.objects.create(
    #     session=session, role="assistant", content="Hi! What would you like help with today?"
    # )

    return redirect("view_conversation", session_id=session.id)

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def chatbot_api(request):
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			message = data.get("message", "")
			user = request.user

			# Get/create session
			session, created = ConversationSession.objects.get_or_create(
				user=user,
				started_at__date=timezone.now().date()
			)

			# Save user message
			ConversationMessage.objects.create(session=session, role="user", content=message)

			# Fetch last 10 messages (reversed)
			_msgs = session.messages.order_by('-timestamp')[:10][::-1]

			messages = [{"role": m.role, "content": m.content} for m in _msgs]

			messages.insert(0, {
				"role": "system",
				"content": "You are A.D.A.M., a helpful AI assistant..."
			})

			response = client.chat.completions.create(
				model="gpt-3.5-turbo",
				messages=messages
			)

			reply = response.choices[0].message.content

			# Save assistant reply
			ConversationMessage.objects.create(session=session, role="assistant", content=reply)

			return JsonResponse({ "reply": reply })

		except Exception as e:
			return JsonResponse({ "reply": f"Server error: {str(e)}" })