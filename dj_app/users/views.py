import json

from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse

from users.models import CustomUser


def check_method(method: str, expected: list) -> HttpResponse:
    if method not in expected:
        return HttpResponse(status=405)


def user_login(request):
    check_method(request.method, ['POST'])
    data = json.loads(request.body)
    if not CustomUser.objects.filter(email=data['email']).exists():
        return HttpResponse(json.dumps({"detail": "Wrong email address"}), status=400, content_type='application/json')
    user = CustomUser.objects.get(email=data['email'])
    if not user.check_password(data['password']):
        return HttpResponse(json.dumps({"detail": "Wrong password"}), status=400, content_type='application/json')
    login(request=request, user=user)
    return HttpResponse(json.dumps({"detail": "Successfully logged in"}), status=200, content_type='application/json')


def user_logout(request):
    check_method(request.method, ['POST'])
    logout(request)
    return HttpResponse(json.dumps({"detail": "Successfully logged out"}), status=200, content_type='application/json')


def user_register(request):
    check_method(request.method, ['POST'])
    data = json.loads(request.body)
    user = CustomUser.objects.create_user(email=data['email'], password=data['password'], username=data['username'])
    login(request=request, user=user)
    return HttpResponse(json.dumps({"detail": "Successfully created"}), status=201, content_type='application/json')


def check_logged(request):
    check_method(request.method, ['GET'])
    return HttpResponse(json.dumps({"logged": request.user.is_authenticated,
                                    "username": request.user.username if request.user.is_authenticated else None}),
                                    status=200, content_type='application/json')