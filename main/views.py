from django.conf import settings
BASE_DIR = settings.BASE_DIR
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib import messages
import shutil
from django.shortcuts import render
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
            inventory__user_orders__user=request.user
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
    categories = Inventory.objects.all()

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
        directory = f"main/uploads/inventorys/admin/{category.id}"
        url_to_header = ""
        if len(os.listdir(directory)) != 0:
            url_to_header = f"/uploads/inventorys/admin/{category.id}/{os.listdir(directory)[0]}"
        data.append({"category": category, "url_to_header": url_to_header})


    context["data"] = data
    if request.method == 'GET':
        sku = request.GET.get('sku')
        if not sku:
            return render(request, 'catalog.html', context)
    return render(request, 'catalog.html', context)

@login_required
def profile(request):
    context = {
        "is_auth": True,
        "is_admin": False,
        "user_inventory": [],
        "form": UploadImageForm(),
        "url_to_avatar": "",
    }

    if request.user.is_superuser:
        context["is_admin"] = True
        directory = f"main/uploads/users/admin/{request.user.id}"
    else:
        directory = f"main/uploads/users/{request.user.id}"

    if os.path.exists(directory) and os.listdir(directory):
        avatar_filename = os.listdir(directory)[0]
        context["url_to_avatar"] = f"/uploads/users/admin/{request.user.id}/{avatar_filename}" if request.user.is_superuser else f"/uploads/users/{request.user.id}/{avatar_filename}"

    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if os.path.exists(directory):
                     for filename in os.listdir(directory):
                         file_path = os.path.join(directory, filename)
                         if os.path.isfile(file_path):
                            os.remove(file_path)
                os.makedirs(directory, exist_ok=True)
                f = request.FILES['image']
                extension = os.path.splitext(str(f))[1]
                unique_name = f"header{extension}"
                with open(os.path.join(directory, unique_name), "wb+") as sv:
                    sv.write(f.read())
                messages.success(request, "Аватар успешно обновлен.")
                return redirect("/profile")
            except Exception as e:
                messages.error(request, f"Ошибка при загрузке аватара. Обратитесь к администратору")
        else:
            messages.error(request, "Ошибка валидации формы. Пожалуйста, проверьте данные.")

    if not request.user.is_superuser:
        user_inventory = OrderItem.objects.filter(
            inventory__user_orders__user=request.user,
            status__in=['approved', 'get_from_admin']
        ).values('name', 'status').annotate(total_quantity=Sum('quantity'))

        inventory_list = []
        for item in user_inventory:
            inventory_list.append({
                'name': item['name'],
                'quantity': item['total_quantity'],
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

def new_inventory(request):
    context = {"is_auth" : False}
    if request.user.is_authenticated and  request.user.is_authenticated:
        context["is_auth"] = True
        if request.method == "POST":
            form = NewInventoryForm(request.POST, request.FILES)
            if form.is_valid():
                print("VALID +", form.cleaned_data)
                data = form.cleaned_data
                inventory = Inventory(
                    author=request.user,
                    name=data.get("about_label"),
                    questions_number=data.get("questions_count"),
                    type_of_inventory=data.get("type_question0")
                )
                inventory.save()
                # for i in range(int(data.get("questions_count"))):
                #     question = Questions(
                #         inventory=inventory,
                #         question=data.get(f"question{i}"),
                #         type_of_inventory=data.get(f"type_question{i}"),
                #         user_vote_amount=0
                #     )
                #     question.save()
                #     for j in range(int(data.get(f"options_count{i}"))):
                #         answer = Answers(
                #             question=question,
                #             answer=data.get(f"option{i}_{j}")
                #         )
                #         answer.save()
                directory = f"main/uploads/inventorys/admin/{inventory.id}"
                os.makedirs(directory)
                f = request.FILES["image"]
                extension = os.path.splitext(str(f))[1]
                with open(f"{directory}/header{extension}", "wb+") as sv:
                    sv.write(f.read())
                return redirect(f"/catalog")
            else:
                print("INVALID")
        else:
            context["form"] = NewInventoryForm()


    return render(request, "new_inventory.html", context)


def inventory(request):
    context = {"IsExist": False}
    id_of_page = request.GET.get("id", None)
    if id_of_page is None:
        return redirect("/catalog")
    try:
        _inventory = get_object_or_404(Inventory, id=id_of_page)
        context["IsExist"] = True
        context["about_label"] = _inventory.name
        context["author"] = _inventory.author
        context["questions_number"] = _inventory.questions_number
        context["inventory_id"] = _inventory.id
        context["type_of_inventory"] = _inventory.type_of_inventory
        directory = os.path.join('main', 'uploads', 'users', 'admin')
        context["url_to_avatar"] = ""
        if os.path.exists(directory):
            if os.listdir(directory):
                context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"

        directory = os.path.join('main', 'uploads', 'inventorys', 'admin', str(_inventory.id))
        context["url_to_header"] = ""
        if os.path.exists(directory):
            if os.listdir(directory):
                context["url_to_header"] = f"/uploads/inventorys/admin/{_inventory.id}/{os.listdir(directory)[0]}"

        # Передаем BASE_DIR в контекст, чтобы использовать его в шаблоне
        context['BASE_DIR'] = BASE_DIR

        if request.method == "POST":
            _inventory.name = request.POST.get("about_label")
            _inventory.questions_number = request.POST.get("questions_count")
            _inventory.type_of_inventory = request.POST.get("type_question0")

            if request.FILES.get('image', False):
                image_file = request.FILES['image']

                # Путь к папке для сохранения картинки (ВНУТРИ main)
                upload_dir = os.path.join(BASE_DIR, 'main', 'uploads', 'inventorys', 'admin', str(_inventory.id))
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

            _inventory.save()
            return redirect("/catalog")
    except Exception as e:
        print(e)
        return HttpResponse("Голосование не найдено или ошибка!")

    return render(request, 'inventory.html', context)


def delete_inventory(request):
    context = {
        "IsExist" : False
    }
    id_of_page = request.GET.get("id", "not founded")
    if request.method == "POST" and request.user.is_authenticated:
        _id = request.POST.get("inventory_id")
        _inventory = Inventory.objects.filter(id=_id)
        if (len(_inventory) != 0):
            if request.user.is_superuser:
                shutil.rmtree(f"main/uploads/inventorys/admin/{_inventory[0].id}")
                _inventory[0].delete()
        return redirect("/catalog")

    elif (id_of_page != "not founded"):
        _inventory = Inventory.objects.filter(id=id_of_page)
        if (len(_inventory) != 0):
            if (_inventory[0].author != request.user):
                return redirect("/catalog")
            context["IsExist"] = True
            context["about_label"] = _inventory[0].name
            context["author"] = _inventory[0].author
            context['questions_number'] = _inventory[0].questions_number
            context["inventory_id"] = _inventory[0].id
            directory = f"main/uploads/users/admin"
            context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"
            directory = f"main/uploads/inventorys/admin/{_inventory[0].id}"
            context["url_to_header"] = f"/uploads/inventorys/admin/{_inventory[0].id}/{os.listdir(directory)[0]}"
            
        else:
            print("Not Founded")
    else:
        return redirect("/catalog")
    
    return render(request, 'delete_inventory.html', context)


def add_inventory(request):
    context = {"IsExist": False}
    id_of_page = request.GET.get("id", None)
    if id_of_page is None:
        return redirect("/catalog")

    _inventory = get_object_or_404(Inventory, id=id_of_page)
    context["IsExist"] = True
    context["about_label"] = _inventory.name
    context["author"] = _inventory.author
    context["questions_number"] = _inventory.questions_number
    context["inventory_id"] = _inventory.id
    context["type_of_inventory"] = _inventory.type_of_inventory

    directory = os.path.join('main', 'uploads', 'users', 'admin')
    context["url_to_avatar"] = ""
    if os.path.exists(directory):
        if os.listdir(directory):
            context["url_to_avatar"] = f"/uploads/users/admin/{os.listdir(directory)[0]}"

    directory = os.path.join('main', 'uploads', 'inventorys', 'admin', str(_inventory.id))
    context["url_to_header"] = ""
    if os.path.exists(directory):
        if os.listdir(directory):
            context["url_to_header"] = f"/uploads/inventorys/admin/{_inventory.id}/{os.listdir(directory)[0]}"

    context['BASE_DIR'] = settings.BASE_DIR

    if request.method == 'POST':

        if 'inventory_id' not in request.POST:
            return HttpResponseForbidden("Invalid request: Missing inventory ID")

        inventory_id = request.POST.get('inventory_id')
        try:
            questions_count = int(request.POST.get('questions_count', 1))
            if questions_count <= 0:
                messages.error(request, "Количество должно быть больше 0.")
                return render(request, 'add_inventory.html', context)
            if questions_count > _inventory.questions_number:
                messages.error(request, "Количество не должно превышать имеющееся.")
                return render(request, 'add_inventory.html', context)
        except ValueError:
            messages.error(request, "Указано некорректное количество.")
            return render(request, 'add_inventory.html', context)

        inventory_name = context["about_label"]

        directory = f"main/uploads/inventorys/admin/{_inventory.id}"
        url_to_header = ""
        if os.path.exists(directory) and os.listdir(directory):
            url_to_header = f"/uploads/inventorys/admin/{_inventory.id}/{os.listdir(directory)[0]}"

        try:
            with transaction.atomic():
                existing_order = UserOrder.objects.filter(
                    user=request.user,
                    inventory=_inventory
                ).first()

                if not existing_order:
                    new_order = UserOrder.objects.create(user=request.user, inventory=_inventory)
                else:
                    new_order = existing_order

                existing_item = OrderItem.objects.filter(
                    name=inventory_name,
                    inventory=_inventory,
                    status='pending',
                    orders__user=request.user
                ).first()

                if existing_item:
                    existing_item.quantity += questions_count
                    existing_item.save()
                    new_order.items.add(existing_item)
                else:
                    new_item = OrderItem.objects.create(
                        name=inventory_name,
                        quantity=questions_count,
                        image_url=url_to_header,
                        status='pending',
                        inventory=_inventory,
                    )
                    new_order.items.add(new_item)
                _inventory.save()
                messages.success(request, "Заказ успешно создан.")
                return redirect('/applications')

        except Exception as e:
            messages.error(request, f"Ошибка при создании заказа: {e}")
            return render(request, 'add_inventory.html', context)

    return render(request, 'add_inventory.html', context)


@require_POST
@login_required
def submit_inventory(request):
    if request.method == 'POST':
        inventory_id = request.POST.get('inventory_id')
        if not inventory_id:
            messages.error(request, "Invalid request: Missing inventory ID")
            return redirect('/applications')

        try:
            with transaction.atomic():
                inventory_id = int(inventory_id)
                inventory = Inventory.objects.get(pk=inventory_id)
                questions_count = int(request.POST.get('questions_count', 1))
                inventory_name = request.POST.get('inventory_name')

                if not inventory_name:
                    messages.error(request, "Invalid request: Missing inventory name")
                    return redirect('/applications')

                # Получаем url_to_header из inventory
                directory = f"main/uploads/inventorys/admin/{inventory.id}"
                url_to_header = ""
                if os.path.exists(directory) and len(os.listdir(directory)) > 0:
                    url_to_header = f"/uploads/inventorys/admin/{inventory.id}/{os.listdir(directory)[0]}"

                # Проверка на превышение максимального количества (добавлено при создании или добавлении)
                if questions_count > inventory.questions_number:
                    messages.error(request,
                                   f"Запрошенное количество ({questions_count}) превышает доступное ({inventory.questions_number}).")
                    return redirect('/applications')

                # Получаем или создаем UserOrder для этого голосования
                order, created = UserOrder.objects.get_or_create(user=request.user, inventory=inventory)

                # Ищем существующий OrderItem в этом UserOrder
                existing_item = order.items.filter(name=inventory_name, inventory=inventory).first()

                if existing_item:
                    # Проверка при изменении (увеличении или уменьшении)
                    total_requested_items = sum(item.quantity for item in order.items.all() if item.inventory == inventory)

                    # Calculate available questions before update
                    available_quantity = inventory.questions_number - (total_requested_items - existing_item.quantity)

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
                        inventory=inventory,
                        quantity=questions_count,
                        image_url=url_to_header,
                        status='pending'
                    )
                    order.items.add(item)

                return redirect('/applications')

        except Inventory.DoesNotExist:
            messages.error(request, "Invalid request: inventory not found")
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
            with transaction.atomic():
                user_name = "Unknown"
                if item.orders.first():
                    user_name = item.orders.first().user.username

                status = 'used'  # Статус по умолчанию
                if item.inventory and item.inventory.type_of_inventory:  # Если есть голосование и тип голосования
                    status = item.inventory.type_of_inventory

                if item.inventory:
                    if item.inventory.questions_number >= item.quantity:
                        item.status = 'approved'
                        item.inventory.questions_number -= item.quantity
                        item.inventory.save()
                        item.save()

                        UsageReport.objects.create(
                            item_name=item.name,
                            user_name=user_name,
                            quantity=item.quantity,
                            status=status
                        )
                        messages.success(request,
                                         f"Статус '{item.name}' успешно изменен на 'Одобрено'. Количество инвентаря уменьшено.")
                    else:
                        messages.error(request, f"Недостаточно инвентаря для выполнения действия.")
                else:
                    item.status = 'approved'
                    item.save()

                    UsageReport.objects.create(
                        item_name=item.name,
                        user_name=user_name,
                        quantity=item.quantity,
                        status=status
                    )

        except Exception as e:
            messages.error(request, f"Ошибка при изменении статуса элемента. Обратитесь к администратору")
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
    categories = Inventory.objects.all()

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
        directory = f"main/uploads/inventorys/admin/{category.id}"
        url_to_header = ""
        if len(os.listdir(directory)) != 0:
            url_to_header = f"/uploads/inventorys/admin/{category.id}/{os.listdir(directory)[0]}"
        data.append({"category": category, "url_to_header": url_to_header})

    context["data"] = data
    context['user'] = user

    return render(request, 'user_detail.html', context)


@login_required
def issue_inventory(request, user_id, inventory_id, item_name):
    """Выдает инвентарь выбранному пользователю."""
    user = get_object_or_404(User, id=user_id)
    inventory = get_object_or_404(Inventory, id=inventory_id)

    directory = f"main/uploads/inventorys/admin/{inventory.id}"
    url_to_header = ""
    if os.path.exists(directory) and os.listdir(directory):
        url_to_header = f"/uploads/inventorys/admin/{inventory.id}/{os.listdir(directory)[0]}"

    if request.method == 'POST':
        quantity_str = request.POST.get('quantity')
        if not quantity_str:
           messages.error(request, "Необходимо указать количество.")
           return render(request, 'issue_inventory.html', {'user': user, 'inventory': inventory, 'url_to_header': url_to_header})
        try:
            quantity = int(quantity_str)
        except ValueError:
            messages.error(request, "Указано некорректное количество.")
            return render(request, 'issue_inventory.html', {'user': user, 'inventory': inventory, 'url_to_header': url_to_header})

        if quantity <= 0:
            messages.error(request, "Количество должно быть больше 0.")
            return render(request, 'issue_inventory.html', {'user': user, 'inventory': inventory, 'url_to_header': url_to_header})


        try:
            with transaction.atomic():
                 # Проверяем, есть ли у пользователя заказ для этого голосования
                user_order = UserOrder.objects.filter(user=user, inventory=inventory).first()

                if not user_order:
                    # Если нет, создаем новый
                     user_order = UserOrder.objects.create(user=user, inventory=inventory)

                 # Проверяем, существует ли уже такой же OrderItem с соответствующим статусом
                existing_item = OrderItem.objects.filter(
                    name=item_name,
                    inventory=inventory,
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
                       inventory=inventory,
                   )
                   user_order.items.add(new_item)



                inventory.questions_number -= quantity
                inventory.save()

               # Добавляем запись в UsageReport
                UsageReport.objects.create(
                   item_name=item_name,
                   user_name=user.username,
                   quantity=quantity,
                    status=inventory.type_of_inventory
                  )


                messages.success(request, f"Заказ '{item_name}' для пользователя {user.username} успешно создан.")
                return redirect('/applications')

        except Exception as e:
            pass


    context = {'user': user, 'inventory': inventory, 'url_to_header': url_to_header}
    return render(request, 'issue_inventory.html', context)


def view_inventory(request):
    """Отображает информацию о текущем инвентаре, суммируя по пользователю, названию и статусу."""

    order_items = OrderItem.objects.filter(status__in=['get_from_admin', 'approved']).select_related('inventory').order_by('name')

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

    inventorys = Inventory.objects.all()

    for item in inventorys:
        inventory.append({
            'user': 'admin',
            'name': item.name,
            'total_quantity': item.questions_number,
            'status_display': 'Находится в собственности админа',
            'status_prep': item.type_of_inventory
        })

    context = {
        'inventory': inventory
    }
    return render(request, 'view_inventory.html', context)


def item_list(request):
    """Отображает список предметов."""
    items = Item.objects.all().order_by('name')
    return render(request, 'item_list.html', {'items': items})

def item_create(request):
    """Создает новый предмет."""
    if request.method == 'POST':
        item_form = ItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save()
            return redirect('item_list')
    else:
        item_form = ItemForm()
    return render(request, 'item_form.html', {'item_form': item_form, 'action': 'create'})

def item_update(request, item_id):
    """Обновляет существующий предмет."""
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        item_form = ItemForm(request.POST, instance=item)
        if item_form.is_valid():
            item = item_form.save()
            return redirect('item_list')
    else:
        item_form = ItemForm(instance=item)
    return render(request, 'item_form.html', {'item_form': item_form, 'action':'update', 'item_id': item_id})

def item_delete(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'item_delete.html', {'item': item})

def view_reports(request):
    """
    Отображает отчеты об использовании предметов
    """
    reports = UsageReport.objects.all()  # получение отчетов из базы данных

    context = {
        'reports': reports
    }
    return render(request, 'view_reports.html', context)