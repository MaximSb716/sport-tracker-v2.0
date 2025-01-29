# Sport Tracker v2.0

![Sport Tracker](https://raw.githubusercontent.com/MaximSb716/sport-tracker-v2.0/70e2be3853984eae9c49cba3b83295333e27e4c3/main/static/img/icon.svg)

Sport Tracker v2.0 - это современное веб-приложение на Django для отслеживания, управления и планировки запупок спортивного инвентаря.

## 🚀 Функциональность

- 👁️ Отслеживание спортивного инвентаря
- ➕ Добавление позиций инвентаря
- 🖋️ Редактирование позиций инвентаря
- 🗃️ Закрепление за пользователями инвентаря
- 👥 Регистрация и авторизация пользователей
- 📑 Удобная система отчетности

## 🛠️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-repo/sport-tracker-v2.0.git
cd sport-tracker-v2.0
```

### 2. Переключение на ветку `simple-votings`
```bash
git checkout simple-votings
```

### 3. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 5. Применение миграций
```bash
python manage.py migrate
```

### 6. Запуск сервера
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📂 Структура проекта

```bash
sport-tracker-v2.0/
├── main/               # Основное приложение
│   ├── migrations/     # Миграции базы данных
│   ├── models.py       # Модели данных
│   ├── views.py        # Логика представлений
│   ├── urls.py         # Маршруты
│   └── forms.py        # Формы
|   └──
├── manage.py           # Управление Django-проектом
├── requirements.txt    # Зависимости проекта
└── README.md           # Описание проекта
```

## 📸 Скриншоты

### Главная страница
![Главная](https://via.placeholder.com/800x400?text=Главная+страница)

### Страница голосования
![Голосование](https://via.placeholder.com/800x400?text=Страница+голосования)

## 🤝 Авторы
- **Сбродов Максим Александрович** - [GitHub](https://github.com/your-profile)
- **Лахтиков Дмитрий** - [GitHub](https://github.com/your-profile)
- **Баричев Артем** - [GitHub](https://github.com/your-profile)
- **Чернилевкий Александр** - [GitHub](https://github.com/your-profile)
