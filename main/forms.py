from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import validate_integer, validate_slug
from django.core.exceptions import ValidationError
from main.models import *


class SignUpForm(UserCreationForm):
    """Форма регистрации пользователя."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class SignInForm(AuthenticationForm):
    """Форма входа пользователя."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "login"}
        )  # Добавляем класс
        self.fields["password"].widget.attrs.update({"class": "password"})


class NewVotingForm(forms.Form):
    """Создание нового голосования."""
    about_label = forms.CharField(label="Напиши заголовок голосования", max_length=100)
    image = forms.ImageField(label="Добавь изображение!")
    questions_count = forms.IntegerField(label="questions_count")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for i in range(1):
            cleaned_data[f"question{i}"] = "asd"
            cleaned_data[f"type_question{i}"] = self.data.get(f"type_question{i}")
            cleaned_data[f"options_count{i}"] = 1

            if not 1 <= len(str(cleaned_data[f"question{i}"])) <= 500:
                raise ValidationError(f"Недопустимое содержание вопроса {i}!")

            if validate_slug(cleaned_data.get(f"type_question{i}")) or not (cleaned_data.get(f"type_question{i}") == "end" or cleaned_data.get(f"type_question{i}") == "one" or cleaned_data.get(f"type_question{i}") == "multi"):
                raise ValidationError(f"Недопустимое содержание выбора типа вопроса {i}!")

            if validate_integer(cleaned_data.get(f"options_count{i}")) or not (1 <= int(cleaned_data.get(f"options_count{i}")) <= 20):
                raise ValidationError(f"Недопустимое значение колличества ответов на вопрос {i}!")

            for j in range(1):
                cleaned_data[f"option{i}_{j}"] = 'asd'

                if not len(cleaned_data.get(f"option{i}_{j}")) <= 70:
                    print(f"Недопустимое содержание ответа {i}_{j}!")
                    raise ValidationError(f"Недопустимое содержание ответа {i}_{j}!")


# class VotingForm(forms.Form):
#     """Форма с голосом пользователя"""
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def clean(self):
#         cleaned_data = super().clean()
#
#         voting = Votings.objects.filter(id=self.data.POST["voting_id"])
#         if len(voting) == 0:
#             print("Голосование не найдено!")
#             raise ValidationError("Голосование не найдено!")
#
#         cleaned_data["voting_id"] = voting[0].id
#         questions = Questions.objects.filter(voting=voting[0])
#         cleaned_data["questions"] = "questions"
#         data = dict(self.data.POST)
#         cleaned_data["answers"] = []

class UploadImageForm(forms.Form):
    """Форма для загрузки изображений"""
    image = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)