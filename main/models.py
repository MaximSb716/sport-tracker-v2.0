
import os
from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
from django.db.models.signals import post_save
# Create your models here.

def get_image_upload_path(instance, filename):
    """Создает путь к файлу изображения для конкретного голосования."""
    ext = filename.split('.')[-1]  # получаем расширение файла
    unique_name = f"header.png"
    return os.path.join('main', 'uploads', 'inventorys', 'admin', str(instance.id), unique_name)


class Inventory(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    name = models.TextField()
    questions_number = models.IntegerField()
    type_of_inventory = models.TextField()

    def delete(self, *args, **kwargs):
        """Удаляем файл изображения, при удалении объекта."""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Переопределяем метод save чтобы сохранять картинки в нужный путь."""
        if self.pk is None:
            super().save(*args, **kwargs)  # если объект новый
            return

        if self.image:
            old_inventory = Inventory.objects.get(pk=self.pk)
            if old_inventory.image and old_inventory.image != self.image:
                if os.path.isfile(old_inventory.image.path):  # удаляем старую картинку, если она есть
                    os.remove(old_inventory.image.path)
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Модель для представления отдельных элементов заказа (например, конкретный товар).
    """
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отказано'),
        ('get_from_admin', 'Выдано админом')
    ]
    name = models.CharField(max_length=255, verbose_name="Название предмета")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')

    def __str__(self):
        return f"{self.name} ({self.quantity}) - {self.get_status_display()}"

    class Meta:
        verbose_name = "Предмет заказа"
        verbose_name_plural = "Предметы заказа"


class UserOrder(models.Model):
    """
    Модель для представления заказа пользователя.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    items = models.ManyToManyField(OrderItem, related_name='orders', verbose_name="Предметы заказа")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_orders')

    def __str__(self):
        return f"Заказ пользователя {self.user.username} от {self.order_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Заказ пользователя"
        verbose_name_plural = "Заказы пользователей"

class Item(models.Model):
    """
    Модель для представления предмета инвентаря.
    """
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('completed', 'Выполнено'),
    ]
    name = models.CharField(max_length=255, verbose_name="Название предмета")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", blank=True, null=True)
    supplier = models.CharField(max_length=255, verbose_name="Планируемый поставщик", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус плана')

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    class Meta:
        verbose_name = "Предмет инвентаря"
        verbose_name_plural = "Предметы инвентаря"

class UsageReport(models.Model):
    """
    Модель для отчетов об использовании предметов
    """
    STATUS_CHOICES = [
        ('one', 'Новый'),
        ('multi', 'Использованный'),
        ('end', 'Сломанный'),
    ]
    item_name = models.CharField(max_length=255, verbose_name="Имя предмета")
    user_name = models.CharField(max_length=255, verbose_name="Имя пользователя")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Состояние")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отчета")

    def __str__(self):
        return f"Отчет для {self.item_name} пользователя {self.user_name} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Отчет об использовании"
        verbose_name_plural = "Отчеты об использовании"