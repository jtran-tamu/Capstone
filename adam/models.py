from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    due_date = models.DateField()
    progress = models.PositiveIntegerField()
    description = models.TextField()

class ProjectManager(models.Model):
    team_id = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team_id = models.IntegerField()
    tasks = models.ManyToManyField(Task, blank=True)

class Question(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    description = models.TextField()

class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    response = models.TextField()

class Form(models.Model):
    questions = models.ManyToManyField(Question)
    answers = models.ManyToManyField(Answer)
    date = models.DateField(auto_now_add=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

class Report(models.Model):
    forms = models.ManyToManyField(Form)
    summary = models.TextField()