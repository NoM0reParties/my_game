import json

from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpRequest

from users.asgi_methods import check_mail, check_pwd, player_login, player_logout, player_register, check_log
from users.models import CustomUser


def check_method(method: str, expected: list) -> HttpResponse:
    if method not in expected:
        return HttpResponse(status=405)


async def user_login(request: HttpRequest) -> HttpResponse:
    check_method(request.method, ['POST'])
    data = json.loads(request.body)
    if not await check_mail(data['email']):
        return HttpResponse(json.dumps({"detail": "Wrong email address"}), status=400, content_type='application/json')
    if not await check_pwd(data['password'], data['email']):
        return HttpResponse(json.dumps({"detail": "Wrong password"}), status=400, content_type='application/json')
    await player_login(request, data['email'])
    return HttpResponse(json.dumps({"detail": "Successfully logged in"}), status=200, content_type='application/json')


async def user_logout(request: HttpRequest) -> HttpResponse:
    check_method(request.method, ['POST'])
    await player_logout(request)
    return HttpResponse(json.dumps({"detail": "Successfully logged out"}), status=200, content_type='application/json')


async def user_register(request: HttpRequest) -> HttpResponse:
    check_method(request.method, ['POST'])
    await  player_register(request)
    return HttpResponse(json.dumps({"detail": "Successfully created"}), status=201, content_type='application/json')


async def check_logged(request: HttpRequest) -> HttpResponse:
    check_method(request.method, ['GET'])
    return HttpResponse(json.dumps(await check_log(request)), status=200, content_type='application/json')