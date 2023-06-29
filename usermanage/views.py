from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import JsonResponse
from rest_framework import permissions, viewsets

from common import local
from common.utils.django import get_params_from_request
from usermanage.serializers import GroupSerializer, UserSerializer


def list_users(request):
    params = get_params_from_request(request)
    params.update({"username": local.get_param(local.LocalVariable.USERNAME)})
    params.update({"request_id": request.request_id})
    return JsonResponse(params)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
