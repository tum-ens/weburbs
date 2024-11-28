import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST


def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


@require_POST
def loginUser(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return JsonResponse({'detail': 'Please provide username and password.'}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=400)

    login(request, user)
    return JsonResponse({'detail': 'Successfully logged in.'})


def logoutUser(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=400)

    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})


@ensure_csrf_cookie
def session(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True})

@require_POST
def register(request):
    data = json.loads(request.body)

    if len(data['username']) <= 3:
        return JsonResponse({'detail': 'Username is too short'}, status=400)
    try:
        validate_email(data['email'])
    except ValidationError:
        return JsonResponse({'detail': 'Invalid E-Mail'}, status=400)
    if len(data['password']) < 5:
        return JsonResponse({'detail': 'Password is too short'}, status=400)

    try:
        User.objects.create_user(**data).save()
    except IntegrityError:
        return JsonResponse({'detail': 'User with this name already exists'}, status=409)

    return JsonResponse({'detail': "User was created"})


