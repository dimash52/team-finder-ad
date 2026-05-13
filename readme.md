# TeamFinder — вариант 1

Реализован Django-бэкенд для веб-приложения TeamFinder: регистрация и вход по email, пользовательские профили, проекты, участие в проектах, избранное, фильтрация пользователей, пагинация, формы редактирования профиля/проекта и смены пароля.

## Что реализовано

- Кастомная модель `User` с авторизацией по `email`.
- Автоматическая генерация аватара с первой буквой имени при создании пользователя.
- Модель `Project` с владельцем, участниками, статусом, датой создания и ссылкой на GitHub.
- Вариант 1:
  - добавление/удаление проекта из избранного;
  - страница `/projects/favorites/` с избранными проектами владельца списка;
  - фильтры на `/users/list/`:
    - авторы избранных проектов;
    - авторы проектов, в которых я участвую;
    - пользователи, которым нравятся мои проекты;
    - участники моих проектов.
- Доступы:
  - гости видят проекты, страницы проектов и пользователей;
  - авторизованные пользователи создают проекты, редактируют свои проекты, завершают их, участвуют в чужих проектах и используют избранное;
  - администратор управляет пользователями и проектами через Django admin.
- Валидация телефона и GitHub URL в формах.
- Пагинация по 12 проектов/пользователей.
- Набор тестов и команда для генерации демо-данных.

## Быстрый запуск локально

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env_example .env
```

В `.env` укажите `TASK_VERSION=1`. Для быстрой локальной проверки можно временно оставить PostgreSQL-переменные пустыми — тогда проект использует SQLite. Но полноценный функционал реализован с PostgreSQL.

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Демо-пользователи после `seed_demo`:

- `anna@example.com`
- `pavel@example.com`
- `maria@example.com`

Пароль у всех: `demo12345`.

## Запуск с PostgreSQL

1. Скопируйте `.env_example` в `.env`.
2. Проверьте параметры PostgreSQL и выставьте:

```env
TASK_VERSION=1
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5436
```

3. Запустите БД:

```bash
docker compose up -d
```

4. Примените миграции и сгенерируйте данные:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

## Основные URL

- `/` → редирект на `/projects/list/`
- `/projects/list/` — список проектов
- `/projects/create-project/` — создание проекта
- `/projects/<id>/` — страница проекта
- `/projects/<id>/edit/` — редактирование проекта
- `/projects/favorites/` — избранное текущего пользователя
- `/users/register/` — регистрация
- `/users/login/` — вход
- `/users/logout/` — выход
- `/users/list/` — участники платформы и фильтры варианта 1
- `/users/<id>/` — профиль пользователя
- `/users/edit-profile/` — редактирование своего профиля
- `/users/change-password/` — смена пароля
- `/admin/` — админ-панель

## Проверка

Также в проекте был добавлен базовый набор тестов для проверки функциональности.

```bash
python manage.py test
```

Тесты покрывают базовый список проектов, регистрацию, избранное, участие, завершение проекта и один из фильтров пользователей.
