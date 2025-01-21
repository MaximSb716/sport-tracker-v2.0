from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.messages import constants as messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import random, os, shutil
from main.forms import SignInForm, SignUpForm, NewVotingForm, VotingForm, UploadImageForm
from main.models import Votings, Questions, Answers, User_answer
# Create your views here.

def index1(request):
    context = {}
    return render(request, 'index1.html', context)

def about_us(request):
    context = {}
    return render(request, 'about_us.html', context)
def applications(request):
    context = {}
    return render(request, 'applications.html', context)
def catalog(request):
    categories = Votings.objects.all()

    context = {
        "categories": categories,
    }
    data = []
    for category in categories:
        directory = f"main/uploads/votings/admin/{category.id}"
        url_to_header = ""
        if len(os.listdir(directory)) != 0:
            url_to_header = f"/uploads/votings/admin/{category.id}/{os.listdir(directory)[0]}"
        data.append({"category": category, "url_to_header": url_to_header})


    context["data"] = data
    if request.method == 'GET':
        sku = request.GET.get('sku')
        if not sku:
            return render(request, 'catalog.html', context)
    return render(request, 'catalog.html', context)

def profile(request):
    context = {
        "is_auth": False,
        "is_admin": False,
    }
    if request.user.is_superuser:
        context["is_admin"] = True
    if request.user.is_authenticated and (not request.user.is_superuser):
        context["is_auth"] = True
        directory = f"main/uploads/users/{request.user.id}"
        context["url_to_avatar"] = ""
        if len(os.listdir(directory)) != 0:
            context["url_to_avatar"] = f"/uploads/users/{request.user.id}/{os.listdir(directory)[0]}"
        context["form"] = UploadImageForm()
        if request.method == "POST":
            form = UploadImageForm(request.POST, request.FILES)
            if form.is_valid():
                shutil.rmtree(directory)
                os.mkdir(directory)
                f = request.FILES["image"]
                extension = os.path.splitext(str(f))[1]
                with open(f"main/uploads/users/{request.user.id}/avatar{extension}", "wb+") as sv:
                    sv.write(f.read())
                return redirect("/profile")

    if request.user.is_authenticated and  request.user.is_superuser:
        context["is_auth"] = True
        directory = f"main/uploads/users/admin"
        context["url_to_avatar"] = ""
        if len(os.listdir(directory)) != 0:
            context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"
        context["form"] = UploadImageForm()
        if request.method == "POST":
            form = UploadImageForm(request.POST, request.FILES)
            if form.is_valid():
                shutil.rmtree(directory)
                os.mkdir(directory)
                f = request.FILES["image"]
                extension = os.path.splitext(str(f))[1]
                with open(f"main/uploads/users/admin/avatar{extension}", "wb+") as sv:
                    sv.write(f.read())
                return redirect("/profile")
    return render(request, 'profile.html', context)

@csrf_exempt
def save_avatar(request):
    pass
    #if request.method == 'POST':
    #    data = json.loads(request.body)
    #    avatar_data = data.get('avatar')
    #    if avatar_data:
    #        # 1. Извлекаем данные base64
    #        format, imgstr = avatar_data.split(';base64,')
    #        ext = format.split('/')[-1]  # извлекаем расширение файла
    #        # 2. Декодируем base64
    #        avatar = ContentFile(base64.b64decode(imgstr), name=f'avatar.{ext}')


def sign_up(request):
    """Регистрация пользователя."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            os.makedirs(f"main/uploads/users/{user.id}")
            return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "accounts/sign_up.html", {"form": form})


def sign_in(request):
    """Авторизация пользователя."""
    if request.method == "POST":
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_page = request.GET.get("next")
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(
                        "/"
                    )
    else:
        form = SignInForm()

    return render(request, "accounts/sign_in.html", {"form": form})


def sign_out(request):
    """Выход пользователя из системы."""
    logout(request)
    return redirect("/")

def votings(request):
    if str(request.user) == "AnonymousUser" and False:
        page = "votings_anon.html"
    else:
        page = "votings.html"

    context = {}
    return render(request, page, context)

def new_voting(request):
    context = {"is_auth" : False}
    if request.user.is_authenticated and  request.user.is_authenticated:
        context["is_auth"] = True
        if request.method == "POST":
            form = NewVotingForm(request.POST, request.FILES)
            if form.is_valid():
                print("VALID +", form.cleaned_data)
                data = form.cleaned_data
                voting = Votings(
                    author=request.user,
                    name=data.get("about_label"),
                    questions_number=data.get("questions_count")
                )
                voting.save()
                for i in range(int(data.get("questions_count"))):
                    question = Questions(
                        voting=voting,
                        question=data.get(f"question{i}"),
                        type_of_voting=data.get(f"type_question{i}"),
                        user_vote_amount=0
                    )
                    question.save()
                    for j in range(int(data.get(f"options_count{i}"))):
                        answer = Answers(
                            question=question,
                            answer=data.get(f"option{i}_{j}")
                        )
                        answer.save()
                directory = f"main/uploads/votings/admin/{voting.id}"
                os.makedirs(directory)
                f = request.FILES["image"]
                extension = os.path.splitext(str(f))[1]
                with open(f"{directory}/header{extension}", "wb+") as sv:
                    sv.write(f.read())
                return redirect(f"/voting?id={voting.id}")
            else:
                print("INVALID")
        else:
            context["form"] = NewVotingForm()

    return render(request, "new_voting.html", context)

def voting(request):
    context = {"IsExist" : False}
    id_of_page = request.GET.get("id", "not founded")
    
    if request.method == "POST" and request.user.is_authenticated:
        form = VotingForm(request)
        form.is_valid()
        print(form.cleaned_data)
        for answer in form.cleaned_data["answers"]:
            print(answer, "qqq")
            user_answer = User_answer(
                user=request.user,
                answer=answer)
            user_answer.save()
        for question in form.cleaned_data["questions"]:
            question.user_vote_amount += 1
            question.save()
        return redirect(f"/result?id={form.cleaned_data['voting_id']}")

    elif (id_of_page != "not founded"):
        _voting = Votings.objects.filter(id=id_of_page)
        if (len(_voting) != 0):
            context["IsExist"] = True
            context["about_label"] = _voting[0].name
            context["author"] = _voting[0].author
            context["voting_id"] = _voting[0].id
            _questions = Questions.objects.filter(voting=_voting[0])
            data = []
            i = 0
            for quest in _questions:
                i += 1
                data.append({"questions" : quest, "answers" : Answers.objects.filter(question=quest)})

            context["data"] = data

            directory = f"main/uploads/users/admin"
            context["url_to_avatar"] = ""
            if len(os.listdir(directory)) != 0:
                context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"
            directory = f"main/uploads/votings/admin/{_voting[0].id}"
            context["url_to_header"] = ""
            context["url_to_header"] = f"/uploads/votings/admin/{_voting[0].id}/{os.listdir(directory)[0]}"
        else:
            print("Not Founded")
    else:
        return redirect("/catalog")

    return render(request, 'voting.html', context)

def about_voting(request):
    context = {}
    return render(request, 'about_voting.html', context)



def survey(request):
    context = {}
    return render(request, 'survey.html', context)

def result(request):
    # Example hardcoded data // Thanks from D1964❤

    context = {"IsExist" : False}
    id_of_page = request.GET.get("id", "not founded")

    if id_of_page != "not founded":
        _voting = Votings.objects.filter(id=id_of_page)
        if (len(_voting) != 0):
            context["IsExist"] = True
            context["about_label"] = _voting[0].name
            context["about_description"] = _voting[0].description
            context["author"] = _voting[0].author
            context["data"] = []

            questions = Questions.objects.filter(voting=_voting[0])
            
            for question in questions:
                vote_counts = []
                answers = Answers.objects.filter(question=question)
                
                for answer in answers:
                    vote_counts.append( {"choice" : answer.answer, "count" : len(User_answer.objects.filter(answer=answer)), "id" : answer.id} )

                if question.type_of_voting == "one":
                    total_votes = sum(vote['count'] for vote in vote_counts)

                elif question.type_of_voting == "multi":
                    total_votes = question.user_vote_amount

                
                results = []
                if total_votes > 0:
                    for vote in vote_counts:
                        results.append({"percentage" : (vote['count'] / total_votes) * 100, "choice" : vote["choice"], "count" : vote["count"]})
                
                _question = {"results" : results, "question" : question}
            
                context["data"].append(_question)
                directory = f"main/uploads/users/{_voting[0].author.id}"
                context["url_to_avatar"] = ""
                if len(os.listdir(directory)) != 0:
                    context["url_to_avatar"] = f"/uploads/users/{_voting[0].author.id}/{os.listdir(directory)[0]}"
                directory = f"main/uploads/votings/{_voting[0].id}"
                context["url_to_header"] = ""
                if len(os.listdir(directory)) != 0:
                    context["url_to_header"] = f"/uploads/votings/{_voting[0].id}/{os.listdir(directory)[0]}"
        else:
            return redirect("/catalog")
    else:
        return redirect("/catalog")


    return render(request, 'result.html', context)

def delete_voting(request):
    context = {
        "IsExist" : False
    }
    id_of_page = request.GET.get("id", "not founded")
    if request.method == "POST" and request.user.is_authenticated:
        _id = request.POST.get("voting_id")
        _voting = Votings.objects.filter(id=_id)
        if (len(_voting) != 0):
            if request.user.is_superuser:
                shutil.rmtree(f"main/uploads/votings/admin/{_voting[0].id}")
                _voting[0].delete()
        return redirect("/catalog")

    elif (id_of_page != "not founded"):
        _voting = Votings.objects.filter(id=id_of_page)
        if (len(_voting) != 0):
            if (_voting[0].author != request.user):
                return redirect("/catalog")
            context["IsExist"] = True
            context["about_label"] = _voting[0].name
            context["about_description"] = _voting[0].description
            context["author"] = _voting[0].author
            context["voting_id"] = _voting[0].id
            _questions = Questions.objects.filter(voting=_voting[0])
            data = []
            i = 0
            for quest in _questions:
                i += 1
                data.append({"questions" : quest, "answers" : Answers.objects.filter(question=quest)})
            
            context["data"] = data
            directory = f"main/uploads/users/admin"
            context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"
            directory = f"main/uploads/votings/admin/{_voting[0].id}"
            context["url_to_header"] = f"/uploads/votings/admin/{_voting[0].id}/{os.listdir(directory)[0]}"
            
        else:
            print("Not Founded")
    else:
        return redirect("/catalog")
    
    return render(request, 'delete_voting.html', context)
