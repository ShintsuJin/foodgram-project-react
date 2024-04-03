# Foodgram - социальная сеть для пользователей, которые хотят делится рецептами.
## Описание проекта
Доступен по адресу - https://bokuva.duckdns.org/. Для админки - reviewer@gmail.com \ Nelsonnik1
Проект, где пользователи могут регистрироваться, загружать фотографии рецептов с описанием, добавлением ингридиентов, тегов, добавлять в избранное, подписываться, а также скачать список покупок.

## Технологии
•	Python-3.9  
•	Django-3.2.3  
•	djangorestframework-3.12.4  
•	nginx  
•	gunicorn-20.1.0  
•   djoser-2.1.0  
•   Docker
## Автор
[@shintsujin](https://github.com/shintsujin)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ShintsuJin/foodgram-project-react 
```

Перейти в корневую директорию

```
cd foodgram-project-react
```

Создать файл .evn для хранения ключей:

```
SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать имя или IP хоста'
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
```

Запустить docker-compose.production:

```
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/

```

Создать суперпользователя, ввести почту, логин, пароль:

```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Готово, теперь можно похвастаться своим Рецептом!