from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from common import local
from common.utils import get_params_from_request


def list_users(request):
    params = get_params_from_request(request)
    params.update({"username": local.get_thread_var(local.LocalVariable.USERNAME)})
    return JsonResponse(params)
