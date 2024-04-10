# Проект Foodgram 

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)



Foodgram реализован для публикации рецептов. Авторизованные пользователи
могут подписываться на понравившихся авторов, добавлять рецепты в избранное,
в покупки, скачать список покупок ингредиентов для добавленных в покупки
рецептов.

## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```
git clone https://github.com/skivelll/foodgram-project-react.git
```

* Cоздайте .env файл и впишите:
    ```
    POSTGRES_DB=[db]
    POSTGRES_USER=[user]
    POSTGRES_PASSWORD=[password]
    DB_NAME=[db_name]
    
    DB_HOST=[host]
    DB_PORT=[port]
    
    
    SECRET_KEY=[secret key django]
    
    ALLOWED_HOSTS=[allowed hosts]
    ```

*   Workflow состоит из трёх шагов:
    - Проверка кода на соответствие PEP8
    - Сборка и публикация образа бекенда на DockerHub.
    - Автоматический деплой на удаленный сервер.
    - Отправка уведомления в телеграм-чат.  
  

* На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```
* После успешной сборки на сервере выполните команды (только после первого деплоя):
    - Соберите статические файлы:
    ```
    sudo docker-compose exec backend python manage.py collectstatic
    ```
    - Примените миграции:
    ```
    sudo docker-compose exec backend python manage.py migrate
    ```
    - Загрузите ингридиенты в базу данных (необязательно).:  
    ```
    python manage.py ingredients_upload_fixture path/to/file
    ```

## Проект в интернете
Проект запущен и доступен по [адресу](https://foodgramsenya.ddns.net/recipes)
