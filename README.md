# Sport Tracker v2.0

Sport Tracker v2.0 - это современное веб-приложение на Django для отслеживания, управления и планировки запупок спортивного инвентаря.

## 🚀 Функциональность

- 👁️ Отслеживание спортивного инвентаря
- ➕ Добавление позиций инвентаря
- 🖋️ Редактирование позиций инвентаря
- 🗃️ Закрепление за пользователями инвентаря
- 👥 Регистрация и авторизация пользователей
- 📑 Удобная система отчетности

## 🛠️ Установка и запуск (Linux)

### 1. Клонирование репозитория
```bash
git clone https://github.com/MaximSb716/sport-tracker-v2.0.git
cd sport-tracker-v2.0
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate
```
### 2. Создание виртуального окружения(Visual Studio Code)
```
ctrl+shift+p
create environment
.venv
Выбрать python
Выбрать requirements.txt
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Применение миграций
```bash
python manage.py migrate --run-syncdb # если сайт не работает правильно
python manage.py makemigrations
python manage.py migrate
```

### 5. Создание аккаунта админа
```bash
python manage.py createsuperuser
```

### 6. Запуск сервера
```bash
python manage.py runserver
```

Сайт будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📂 Структура проекта

```bash
sport-tracker-v2.0/
├── main/               # Основное приложение для управления спортивным инвентарем
│   ├── static/         # Содержит статические файлы, такие как CSS, изображения для приложения 'main'
│   │   └── ...         #   (подкаталоги для css, img)
│   ├── templates/      # Содержит HTML-шаблоны для отображения данных и пользовательского интерфейса приложения 'main'
│   │   └── ...         #   (файлы HTML-шаблонов)
│   ├── uploads/        # Создается при загрузке изображений на сайт
│   │   └── ...         #   (здесь будут храниться загруженные изображения аватара и изображений инвентаря)
│   ├── admin.py        # Настройки панели администратора Django для моделей приложения 'main'
│   ├── apps.py         # Конфигурация приложения 'main' (название, готовность и т.д.)
│   ├── forms.py        # Определения форм Django для ввода и валидации данных приложения 'main'
│   ├── models.py       # Определение моделей базы данных приложения 'main' (таблицы БД и их поля)
│   ├── tests.py        # Файлы с тестами для тестирования функциональности приложения 'main'
│   ├── urls.py         # Маршрутизация URL-запросов к представлениям приложения 'main'
│   └── views.py        # Логика обработки запросов и рендеринга шаблонов приложения 'main' (представления)
├── sport_tracker/      # Основной каталог настроек проекта
│   ├── __init__.py     # Файл инициализации пакета Python
│   ├── asgi.py         # Настройки ASGI для асинхронных веб-серверов (для production)
│   ├── settings.py     # Основные настройки Django проекта (база данных, приложения, ключи, и т.д.)
│   ├── urls.py         # Общая маршрутизация URL-запросов для всего проекта
│   └── wsgi.py         # Настройки WSGI для синхронных веб-серверов (для production)
├── manage.py           # Скрипт для управления Django проектом (запуск сервера, миграции и т.д.)
├── requirements.txt    # Файл со списком зависимостей проекта (устанавливается pip install -r requirements.txt)
└── README.md           # Файл с описанием проекта (цель, инструкции по установке и запуску и т.д.)
```

## Видео работы программного продукта
https://vkvideo.ru/video849850570_456239017

## Схема базы данных
https://www.drawdb.app/editor?shareId=1c2c14f657dc9996833f341d61256f6b

## 🤝 Авторы
- **Сбродов Максим Александрович** - [GitHub](https://github.com/MaximSb716)
- **Барычев Артем Антонович** - [GitHub](https://github.com/Artem2062)
- **Лахтиков Дмитрий Александрович** - [GitHub](https://github.com/Lahtikov)
- **Чернилевкий Александр Сергеевич** - [GitHub](https://github.com/ALEKSANDR7899)
