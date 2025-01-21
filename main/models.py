from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Votings(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField()
    name = models.TextField()
    questions_number = models.IntegerField()
    type_of_voting = models.TextField()

class Questions(models.Model):
    voting = models.ForeignKey(Votings, on_delete=models.CASCADE)
    image = models.ImageField()
    question = models.TextField()
    type_of_voting = models.TextField()
    user_vote_amount = models.IntegerField()

class Answers(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer = models.TextField()

class User_answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE)
