from django.contrib import admin

# Register your models here.

from .models import Artist, Question, ProjectManager, Task, Answer, CheckinResponse, ConversationSession, Summary

admin.site.register(Question)
admin.site.register(Artist)
admin.site.register(ProjectManager) 
admin.site.register(Task)
admin.site.register(Answer)
admin.site.register(CheckinResponse)
admin.site.register(ConversationSession)
admin.site.register(Summary)