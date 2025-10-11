# Library Management API

Django REST Framework API для управления библиотекой с JWT аутентификацией и ролевой системой.

## 🚀 Функциональность

- **Управление книгами**: CRUD операции, поиск, фильтрация
- **Управление пользователями**: Регистрация, аутентификация, роли
- **Система выдачи книг**: Бронирование, возврат, история
- **Ролевая система**: Читатель, Библиотекарь, Администратор
- **JWT аутентификация**: Безопасный доступ к API
- **Документация API**: Swagger/ReDoc автогенерация

## 🛠 Технологии

- **Backend**: Django 4.2 + Django REST Framework
- **База данных**: PostgreSQL
- **Аутентификация**: JWT tokens
- **Контейнеризация**: Docker + Docker-compose
- **Документация**: drf-yasg (Swagger)
- **Code quality**: flake8, black

## 📋 Требования

- Docker 20.10+
- Docker-compose 1.29+

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/Kenny-nik/Diplome
cd library-management-api