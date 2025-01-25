from django.conf import settings
BASE_DIR = settings.BASE_DIR
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Sum, F
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Max
from django.contrib import messages
import shutil
from django.shortcuts import render
from django.db.models import Prefetch
from django.db import transaction
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


def applications(request):
    """
       Отображает заказы текущего пользователя или всех пользователей (для суперпользователя).
       """
    formatted_orders = []

    if request.user.is_superuser:
        order_items = OrderItem.objects.exclude(status='approved').exclude(status='rejected').exclude(status='get_from_admin')
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
        user_items = OrderItem.objects.filter(
            voting__user_orders__user=request.user
        ).exclude(status='approved').exclude(status='rejected').exclude(status='get_from_admin')
        for item in user_items:
            formatted_orders.append({
                'url_to_header': item.image_url if item.image_url else '/static/images/default_header.jpg',
                'category': {
                    'name': item.name,
                    'description': f"Количество: {item.quantity}",
                    'status': item.get_status_display(),
                },
                'id': item.id,
            })

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
        "user_inventory": [],
    }

    if request.user.is_superuser:
        context["is_admin"] = True
    if request.user.is_authenticated:
        context["is_auth"] = True
        directory = f"main/uploads/users/{request.user.id}" if not request.user.is_superuser else  f"main/uploads/users/admin"
        context["url_to_avatar"] = ""
        if os.path.exists(directory) and len(os.listdir(directory)) != 0:
            context["url_to_avatar"] = f"/uploads/users/{request.user.id}/{os.listdir(directory)[0]}" if not request.user.is_superuser else  f"/uploads/users/admin/{os.listdir(directory)[0]}"

        context["form"] = UploadImageForm()

        if request.method == "POST":
            form = UploadImageForm(request.POST, request.FILES)
            if form.is_valid():
                if os.path.exists(directory):
                    shutil.rmtree(directory)
                os.makedirs(directory, exist_ok=True)
                f = request.FILES["image"]
                extension = os.path.splitext(str(f))[1]
                with open(os.path.join(directory, f"avatar{extension}"), "wb+") as sv:
                    sv.write(f.read())
                return redirect("/profile")

        if not request.user.is_superuser:
            user_inventory = OrderItem.objects.filter(
                voting__user_orders__user=request.user,
                status__in=['approved', 'get_from_admin']
            ).values('name', 'status','image_url').annotate(total_quantity=Sum('quantity'))

            inventory_list = []
            for item in user_inventory:
                 inventory_list.append({
                  'name': item['name'],
                  'quantity': item['total_quantity'],
                 'image_url': item['image_url'] if item['image_url'] else '/static/images/default_header.jpg',
                   'status': dict(OrderItem.STATUS_CHOICES).get(item['status'])
                   })
            context["user_inventory"] = inventory_list

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
                    with open(new_file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
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

    context['BASE_DIR'] = settings.BASE_DIR

    if request.method == 'POST':

        if 'voting_id' not in request.POST:
            return HttpResponseForbidden("Invalid request: Missing voting ID")

        voting_id = request.POST.get('voting_id')
        try:
            questions_count = int(request.POST.get('questions_count', 1))
            if questions_count <= 0:
                messages.error(request, "Количество должно быть больше 0.")
                return render(request, 'add_voting.html', context)
            if questions_count > _voting.questions_number:
                messages.error(request, "Количество не должно превышать имеющееся.")
                return render(request, 'add_voting.html', context)
        except ValueError:
            messages.error(request, "Указано некорректное количество.")
            return render(request, 'add_voting.html', context)

        inventory_name = context["about_label"]

        directory = f"main/uploads/votings/admin/{_voting.id}"
        url_to_header = ""
        if os.path.exists(directory) and os.listdir(directory):
            url_to_header = f"/uploads/votings/admin/{_voting.id}/{os.listdir(directory)[0]}"

        try:
            with transaction.atomic():
                # Проверяем, существует ли уже такой UserOrder
                existing_order = UserOrder.objects.filter(
                    user=request.user,
                    voting=_voting
                ).first()

                if not existing_order:
                    # Если UserOrder не существует, создаем новый
                    new_order = UserOrder.objects.create(user=request.user, voting=_voting)
                else:
                    new_order = existing_order  # используем существующий

                # Проверяем, существует ли уже такой OrderItem с тем же статусом
                existing_item = OrderItem.objects.filter(
                    name=inventory_name,
                    voting=_voting,
                    status='pending',  # Проверяем только на pending
                    orders__user=request.user
                ).first()

                if existing_item:
                    # Если OrderItem существует и статус pending - увеличиваем количество
                    existing_item.quantity += questions_count
                    existing_item.save()
                    new_order.items.add(existing_item)
                else:
                    # Если OrderItem не существует или статус не pending - создаем новый
                    new_item = OrderItem.objects.create(
                        name=inventory_name,
                        quantity=questions_count,
                        image_url=url_to_header,
                        status='pending',
                        voting=_voting,
                    )
                    new_order.items.add(new_item)

                _voting.questions_number -= questions_count
                _voting.save()
                messages.success(request, "Заказ успешно создан.")
                return redirect('/applications')

        except Exception as e:
            messages.error(request, f"Ошибка при создании заказа: {e}")
            return render(request, 'add_voting.html', context)

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

                # Проверка на превышение максимального количества (добавлено при создании или добавлении)
                if questions_count > voting.questions_number:
                    messages.error(request,
                                   f"Запрошенное количество ({questions_count}) превышает доступное ({voting.questions_number}).")
                    return redirect('/applications')

                # Получаем или создаем UserOrder для этого голосования
                order, created = UserOrder.objects.get_or_create(user=request.user, voting=voting)

                # Ищем существующий OrderItem в этом UserOrder
                existing_item = order.items.filter(name=inventory_name, voting=voting).first()

                if existing_item:
                    # Проверка при изменении (увеличении или уменьшении)
                    total_requested_items = sum(item.quantity for item in order.items.all() if item.voting == voting)

                    # Calculate available questions before update
                    available_quantity = voting.questions_number - (total_requested_items - existing_item.quantity)

                    if questions_count > available_quantity:
                        messages.error(request,
                                       f"Нельзя запросить больше чем {available_quantity}, так как уже запрошено {existing_item.quantity}.")
                        return redirect('/applications')

                    existing_item.quantity += questions_count

                    # Добавленная проверка для вычитания
                    if existing_item.quantity < 0:
                        messages.error(request, "Нельзя уменьшить количество ниже 0.")
                        return redirect('/applications')

                    existing_item.save()  # Сохраняем изменения
                else:
                    # Создаем новый OrderItem, если его нет
                    item = OrderItem.objects.create(
                        name=inventory_name,
                        voting=voting,
                        quantity=questions_count,
                        image_url=url_to_header,
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
            if item.voting:
                if item.voting.questions_number >= item.quantity:
                    item.status = 'approved'
                    item.voting.questions_number -= item.quantity
                    item.voting.save()
                    item.save()

                    messages.success(request, f"Статус '{item.name}' успешно изменен на 'Одобрено'. Количество инвентаря уменьшено.")
                else:
                    messages.error(request, f"Недостаточно инвентаря для выполнения действия.")
            else:
                item.status = 'approved'
                item.save()

        except Exception as e:
            pass
    else:
        pass
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


User = get_user_model()

def secure_inventory(request):
    """Отображает список всех пользователей, кроме суперпользователей, с кнопками."""
    users = User.objects.filter(is_superuser=False)
    context = {'users': users}
    return render(request, 'secure_inventory.html', context)


def user_detail(request, user_id):
    """Обработка кнопки "Выдать инвентарь" для пользователя."""
    user = get_object_or_404(User, id=user_id)
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
    context['user'] = user

    return render(request, 'user_detail.html', context)


@login_required
def issue_inventory(request, user_id, voting_id, item_name):
    """Выдает инвентарь выбранному пользователю."""
    user = get_object_or_404(User, id=user_id)
    voting = get_object_or_404(Votings, id=voting_id)

    directory = f"main/uploads/votings/admin/{voting.id}"
    url_to_header = ""
    if os.path.exists(directory) and os.listdir(directory):
        url_to_header = f"/uploads/votings/admin/{voting.id}/{os.listdir(directory)[0]}"

    if request.method == 'POST':
        quantity_str = request.POST.get('quantity')
        if not quantity_str:
            messages.error(request, "Необходимо указать количество.")
            return render(request, 'issue_inventory.html',
                          {'user': user, 'voting': voting, 'url_to_header': url_to_header})
        try:
            quantity = int(quantity_str)
        except ValueError:
            messages.error(request, "Указано некорректное количество.")
            return render(request, 'issue_inventory.html',
                          {'user': user, 'voting': voting, 'url_to_header': url_to_header})

        if quantity <= 0:
            messages.error(request, "Количество должно быть больше 0.")
            return render(request, 'issue_inventory.html',
                          {'user': user, 'voting': voting, 'url_to_header': url_to_header})

        with transaction.atomic():
            try:
                # Проверяем, есть ли у пользователя заказ для этого голосования
                user_order = UserOrder.objects.filter(user=user, voting=voting).first()

                if not user_order:
                    # Если нет, создаем новый
                     user_order = UserOrder.objects.create(user=user, voting=voting)

                 # Проверяем, существует ли уже такой же OrderItem с соответствующим статусом
                existing_item = OrderItem.objects.filter(
                    name=item_name,
                    voting=voting,
                     status='get_from_admin',
                    orders__user=user
                ).first()

                if existing_item:
                 # Если OrderItem существует, увеличиваем количество
                    existing_item.quantity += quantity
                    existing_item.save()
                else:
                # Если такого OrderItem нет, создаем новый с get_from_admin
                   new_item = OrderItem.objects.create(
                       name=item_name,
                       quantity=quantity,
                       image_url=url_to_header,
                       status='get_from_admin',
                       voting=voting,
                   )
                   user_order.items.add(new_item)



                voting.questions_number -= quantity
                voting.save()

                messages.success(request, f"Заказ '{item_name}' для пользователя {user.username} успешно создан.")
                return redirect('/applications')

            except Exception as e:
                messages.error(request, f"Ошибка при создании заказа: {e}")

    context = {'user': user, 'voting': voting, 'url_to_header': url_to_header}
    return render(request, 'issue_inventory.html', context)

def plan(request):
    context = {}
    """Отображает список планов закупок."""
    #purchase_plans = PurchasePlan.objects.all().order_by('-creation_date') # Извлекаем все планы, сортировка по дате
    #context = {
    #    'purchase_plans': purchase_plans,
    #    'is_admin': request.user.is_superuser,  # Проверяем, является ли пользователь администратором
    #    'is_auth': request.user.is_authenticated,  # Проверяем, авторизован ли пользователь
    #}
    return render(request, 'plan.html', context)

def view_inventory(request):
    """Отображает информацию о текущем инвентаре, суммируя по пользователю, названию и статусу."""

    order_items = OrderItem.objects.filter(status__in=['get_from_admin', 'approved']).select_related('voting').order_by('name')

    grouped_items = defaultdict(lambda: {'total_quantity': 0, 'user': set(), 'status': None})

    for item in order_items:
      orders = UserOrder.objects.filter(items=item).select_related('user')
      for order in orders:
        key = (order.user.username, item.name, item.status)
        grouped_items[key]['total_quantity'] += item.quantity
        grouped_items[key]['user'].add(order.user.username)
        grouped_items[key]['status'] = item.status
    inventory = []
    for (user, name, status), data in grouped_items.items():
        inventory.append({
            'user': ', '.join(data['user']),
            'name': name,
            'total_quantity': data['total_quantity'],
            'status_display': dict(OrderItem.STATUS_CHOICES).get(data['status']),
            'status_prep': 'Невозможно отслеживать'
            })

    votings = Votings.objects.all()

    for item in votings:
        inventory.append({
            'user': 'admin',
            'name': item.name,
            'total_quantity': item.questions_number,
            'status_display': 'Находится в собственности админа',
            'status_prep': item.type_of_voting
        })

    context = {
        'inventory': inventory
    }
    return render(request, 'view_inventory.html', context)
