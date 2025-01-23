from django.conf import settings
BASE_DIR = settings.BASE_DIR
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import  get_object_or_404
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import shutil
from django.db import transaction
from .models import OrderItem, UserOrder, Votings
import os
import logging
from django.http import *
from main.forms import *
from main.models import *
# Create your views here.

def index1(request):
    context = {}
    return render(request, 'index1.html', context)

def about_us(request):
    context = {}
    return render(request, 'about_us.html', context)


from django.shortcuts import render
from .models import UserOrder, OrderItem
from django.db.models import Prefetch


def applications(request):
    """
       Отображает заказы текущего пользователя или всех пользователей (для суперпользователя).
       """
    formatted_orders = []

    if request.user.is_superuser:
        order_items = OrderItem.objects.exclude(status='approved').exclude(status='rejected')
        for item in order_items:
            order_data = {
                'url_to_header': item.image_url if item.image_url else '/static/images/default_header.jpg',
                'category': {
                    'name': item.name,
                    'description': f"Количество: {item.quantity}",
                     'status': item.get_status_display(),
                },
                'id': item.id,
            }
            formatted_orders.append(order_data)
    else:
        user_orders = UserOrder.objects.filter(user=request.user).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.all())
        )
        for order in user_orders:
            # Get image_url from the first item in the order, if there are any items
            first_item = order.items.first()
            if first_item and first_item.image_url:
                image_url = first_item.image_url
            else:
                image_url = '/static/images/default_header.jpg'

            order_data = {
                'url_to_header': image_url,
                'category': {
                    'name': f"Заявка от {order.order_date.strftime('%Y-%m-%d %H:%M')} (Пользователь: {order.user.username})",
                    'description': ', '.join([f"{item.name} ({item.quantity})" for item in
                                              order.items.all()]) if order.items.exists() else "Нет предметов",
                    'status': first_item.get_status_display() if first_item else "Нет статуса",
                },
                 'id': order.id,
            }
            formatted_orders.append(order_data)



    context = {
        'data': formatted_orders,
    }

    return render(request, 'applications.html', context)


def catalog(request):
    categories = Votings.objects.all()

    context = {
        "categories": categories,
        "is_admin": False,
        "is_auth": False,
    }
    if request.user.is_superuser:
        context["is_admin"] = True
    if request.user.is_authenticated:
        context["is_auth"] = True
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
                    questions_number=data.get("questions_count"),
                    type_of_voting=data.get("type_question0")
                )
                voting.save()
                # for i in range(int(data.get("questions_count"))):
                #     question = Questions(
                #         voting=voting,
                #         question=data.get(f"question{i}"),
                #         type_of_voting=data.get(f"type_question{i}"),
                #         user_vote_amount=0
                #     )
                #     question.save()
                #     for j in range(int(data.get(f"options_count{i}"))):
                #         answer = Answers(
                #             question=question,
                #             answer=data.get(f"option{i}_{j}")
                #         )
                #         answer.save()
                directory = f"main/uploads/votings/admin/{voting.id}"
                os.makedirs(directory)
                f = request.FILES["image"]
                extension = os.path.splitext(str(f))[1]
                with open(f"{directory}/header{extension}", "wb+") as sv:
                    sv.write(f.read())
                return redirect(f"/catalog")
            else:
                print("INVALID")
        else:
            context["form"] = NewVotingForm()

    return render(request, "new_voting.html", context)


def voting(request):
    context = {"IsExist": False}
    id_of_page = request.GET.get("id", None)
    if id_of_page is None:
        return redirect("/catalog")
    try:
        _voting = get_object_or_404(Votings, id=id_of_page)
        context["IsExist"] = True
        context["about_label"] = _voting.name
        context["author"] = _voting.author
        context["questions_number"] = _voting.questions_number
        context["voting_id"] = _voting.id
        context["type_of_voting"] = _voting.type_of_voting
        directory = os.path.join('main', 'uploads', 'users', 'admin')
        context["url_to_avatar"] = ""
        if os.path.exists(directory):
            if os.listdir(directory):
                context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"

        directory = os.path.join('main', 'uploads', 'votings', 'admin', str(_voting.id))
        context["url_to_header"] = ""
        if os.path.exists(directory):
            if os.listdir(directory):
                context["url_to_header"] = f"/uploads/votings/admin/{_voting.id}/{os.listdir(directory)[0]}"

        # Передаем BASE_DIR в контекст, чтобы использовать его в шаблоне
        context['BASE_DIR'] = BASE_DIR

        if request.method == "POST":
            _voting.name = request.POST.get("about_label")
            _voting.questions_number = request.POST.get("questions_count")
            _voting.type_of_voting = request.POST.get("type_question0")

            if request.FILES.get('image', False):
                image_file = request.FILES['image']

                # Путь к папке для сохранения картинки (ВНУТРИ main)
                upload_dir = os.path.join(BASE_DIR, 'main', 'uploads', 'votings', 'admin', str(_voting.id))
                print(f"Upload directory: {upload_dir}")  # Для отладки пути

                # Создаем папку, если ее нет
                os.makedirs(upload_dir, exist_ok=True)

                # Полный путь к новому файлу
                new_file_path = os.path.join(upload_dir, 'header' + os.path.splitext(image_file.name)[1])
                print(f"New file path: {new_file_path}")  # Для отладки пути

                # Удаляем все файлы в папке
                if os.path.exists(upload_dir):
                    for file in os.listdir(upload_dir):
                        file_path = os.path.join(upload_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)

                try:
                    # Сохраняем новый файл
                    with open(new_file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                # Не сохраняем путь в базе данных!
                # _voting.image = ...  # Убрали запись пути в БД!
                except Exception as e:
                    print(f"Ошибка при сохранении файла: {e}")

            _voting.save()
            return redirect("/catalog")
    except Exception as e:
        print(e)
        return HttpResponse("Голосование не найдено или ошибка!")

    return render(request, 'voting.html', context)



def about_voting(request):
    context = {}
    return render(request, 'about_voting.html', context)



def survey(request):
    context = {}
    return render(request, 'survey.html', context)


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
            context["author"] = _voting[0].author
            context["voting_id"] = _voting[0].id

            directory = f"main/uploads/users/admin"
            context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"
            directory = f"main/uploads/votings/admin/{_voting[0].id}"
            context["url_to_header"] = f"/uploads/votings/admin/{_voting[0].id}/{os.listdir(directory)[0]}"
            
        else:
            print("Not Founded")
    else:
        return redirect("/catalog")
    
    return render(request, 'delete_voting.html', context)

def add_voting(request):
    context = {"IsExist": False}
    id_of_page = request.GET.get("id", None)
    if id_of_page is None:
        return redirect("/catalog")

    _voting = get_object_or_404(Votings, id=id_of_page)
    context["IsExist"] = True
    context["about_label"] = _voting.name
    context["author"] = _voting.author
    context["questions_number"] = _voting.questions_number
    context["voting_id"] = _voting.id
    context["type_of_voting"] = _voting.type_of_voting

    directory = os.path.join('main', 'uploads', 'users', 'admin')
    context["url_to_avatar"] = ""
    if os.path.exists(directory):
        if os.listdir(directory):
            context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"

    directory = os.path.join('main', 'uploads', 'votings', 'admin', str(_voting.id))
    context["url_to_header"] = ""
    if os.path.exists(directory):
        if os.listdir(directory):
            context["url_to_header"] = f"/uploads/votings/admin/{_voting.id}/{os.listdir(directory)[0]}"

    context['BASE_DIR'] = BASE_DIR


    if request.method == 'POST':
        voting_id = request.GET.get('id')
        if not voting_id:
            return HttpResponseForbidden("Invalid request: Missing voting ID")

        questions_count = int(request.POST.get('questions_count', 1))  # get with a default value of 1
            # Replace this with your logic for getting the inventory item's name by voting_id
        inventory_name = context["about_label"]

        directory = f"main/uploads/votings/admin/{_voting.id}"
        url_to_header = ""
        if len(os.listdir(directory)) != 0:
            url_to_header = f"/uploads/votings/admin/{_voting.id}/{os.listdir(directory)[0]}"

        item, created = OrderItem.objects.get_or_create(
            name=inventory_name,
            defaults={'quantity': questions_count, 'image_url': url_to_header, 'status': 'pending'}
        )
        if not created:
            item.quantity = questions_count
            item.image_url = url_to_header
            item.status = 'pending'
            item.save()

            # Create the user's order
        order = UserOrder.objects.create(user=request.user)
        order.items.add(item)

        return redirect('/applications')

    return render(request, 'add_voting.html', context)


@require_POST
@login_required
def submit_inventory(request):
    if request.method == 'POST':
        voting_id = request.POST.get('voting_id')
        if not voting_id:
            messages.error(request, "Invalid request: Missing voting ID")
            return redirect('/applications')

        try:
            with transaction.atomic():
                voting_id = int(voting_id)
                voting = Votings.objects.get(pk=voting_id)
                questions_count = int(request.POST.get('questions_count', 1))
                inventory_name = request.POST.get('inventory_name')

                if not inventory_name:
                    messages.error(request, "Invalid request: Missing inventory name")
                    return redirect('/applications')

                # Получаем url_to_header из voting
                directory = f"main/uploads/votings/admin/{voting.id}"
                url_to_header = ""
                if os.path.exists(directory) and len(os.listdir(directory)) > 0:
                    url_to_header = f"/uploads/votings/admin/{voting.id}/{os.listdir(directory)[0]}"

                # Проверка на превышение максимального количества
                if questions_count > voting.questions_number:
                    messages.error(request, f"Запрошенное количество ({questions_count}) превышает доступное ({voting.questions_number}).")
                    return redirect('/applications')
                # Получаем или создаем UserOrder для этого голосования
                order, created = UserOrder.objects.get_or_create(user=request.user, voting=voting)

                # Ищем существующий OrderItem в этом UserOrder
                existing_item = order.items.filter(name=inventory_name, voting=voting).first()

                if existing_item:
                    # Проверяем, не превысит ли добавление количества доступное
                    available_quantity = voting.questions_number - sum(item.quantity for item in order.items.all() if item.voting == voting)
                    if questions_count > available_quantity:
                        messages.error(request, f"Нельзя запросить больше, чем {available_quantity}, так как уже запрошено {existing_item.quantity}.")
                        return redirect('/applications')

                    existing_item.quantity += questions_count
                    existing_item.save()  # Сохраняем изменения
                else:
                    # Создаем новый OrderItem, если его нет
                    item = OrderItem.objects.create(
                        name=inventory_name,
                        voting=voting,
                        quantity=questions_count,
                        image_url=url_to_header,  # <- Добавлено сохранение image_url
                        status='pending'
                    )
                    order.items.add(item)

                return redirect('/applications')

        except Votings.DoesNotExist:
            messages.error(request, "Invalid request: Voting not found")
            return redirect('/applications')
        except ValueError:
            messages.error(request, "Invalid request: Invalid questions_count")
            return redirect('/applications')
        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")

    return HttpResponseForbidden("Invalid request: Not a POST request")


@require_POST
@login_required
def approve_item(request):
    item_id = request.POST.get('item_id')
    if item_id:
        item = get_object_or_404(OrderItem, id=item_id)
        try:
            item.status = 'approved'
            item.save()
            if item.voting:
                item.voting.questions_number = max(0, item.voting.questions_number - item.quantity)
                item.voting.save()
                messages.success(request, f"Статус '{item.name}' успешно изменен на 'Одобрено'. Количество вопросов в голосовании обновлено.")
            else:
                messages.warning(request, f"Статус '{item.name}' успешно изменен на 'Одобрено', но нет связи с голосованием.")
        except Exception as e:
            print(f"Error saving item status: {e}")
            messages.error(request, f"Ошибка при изменении статуса '{item.name}'. Попробуйте позже.")
    else:
        messages.error(request, f"Не удалось получить id элемента.")
    return redirect('/applications')


def reject_item(request):
     """Изменяет статус OrderItem на 'Отказано'."""
     if request.method == 'POST':
         item_id = request.POST.get('item_id')
         if not item_id:
             return HttpResponseBadRequest("Missing item_id in POST data")

         try:
             item = get_object_or_404(OrderItem, pk=item_id)
             item.status = 'rejected'  # Предполагается, что у вас есть такой статус
             item.save()
         except ValueError:
             return HttpResponseBadRequest("Invalid item_id format")
         except Exception as e:
             print(f"Error updating item status: {e}")
             return HttpResponseBadRequest("Error updating item status")

     return redirect("/applications")