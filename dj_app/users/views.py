import json
from asyncio import gather

from django.http import HttpResponse, HttpRequest

from users.asgi_methods import check_mail, check_pwd, player_login, player_logout, player_register, check_log


def check_method(method: str, expected: list) -> HttpResponse:
    if method not in expected:
        return HttpResponse(status=405)


async def user_login(request: HttpRequest) -> HttpResponse:
    check_method(request.method, ['POST'])
    data = json.loads(request.body)
    info = await gather(check_mail(data['email']), check_pwd(data['password'], data['email']),
                        player_login(request, data['email']))
    if not info[0]:
        return HttpResponse(json.dumps({"detail": "Wrong email address"}), status=400, content_type='application/json')
    if not info[1]:
        return HttpResponse(json.dumps({"detail": "Wrong password"}), status=400, content_type='application/json')
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
