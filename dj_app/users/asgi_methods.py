import json
from typing import Coroutine

from asgiref.sync import sync_to_async
from django.contrib.auth import login, logout
from django.http import HttpRequest

from users.models import CustomUser


def _check_mail(email: str) -> bool:
    return CustomUser.objects.filter(email=email).exists()


async def check_mail(email: str) -> Coroutine:
    return await sync_to_async(_check_mail)(email)


def _check_pwd(password: str, email: str) -> bool:
    user = CustomUser.objects.get(email=email)
    return user.check_password(password)


async def check_pwd(password: str, email: str) -> Coroutine:
    return await sync_to_async(_check_pwd)(password, email)


def _player_login(request: HttpRequest, email: str) -> dict:
    user = CustomUser.objects.get(email=email)
    login(request=request, user=user)


async def player_login(request: HttpRequest, email: str) -> Coroutine:
    return await sync_to_async(_player_login)(request, email)


def _player_logout(request: HttpRequest) -> None:
    logout(request)


async def player_logout(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_player_logout)(request)


def _player_register(request: HttpRequest) -> None:
    data = json.loads(request.body)
    user = CustomUser.objects.create_user(email=data['email'], password=data['password'], username=data['username'])
    login(request=request, user=user)


async def player_register(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_player_register)(request)


def _check_log(request: HttpRequest) -> dict:
    return {"logged": request.user.is_authenticated,
                                    "username": request.user.username if request.user.is_authenticated else None}


async def check_log(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_check_log)(request)