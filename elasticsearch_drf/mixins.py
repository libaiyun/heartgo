from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from elasticsearch_drf.utils import get_search_data


class ESCreateModelMixin:
    def create(self, request, *args, **kwargs):
        form = self.get_form(data=request.data)
        if form.is_valid() is False:
            raise ValidationError(form.errors)
        self.perform_create(form)
        return Response(form.cleaned_data, status=status.HTTP_201_CREATED)

    def perform_create(self, form):
        assert self.model_class is not None
        self.model_class(**form.cleaned_data).save()


class ESListModelMixin:
    def list(self, request, *args, **kwargs):
        search = self.filter_search(self.get_search())

        page_search = self.paginate_search(search)
        if page_search is not None:
            data = get_search_data(page_search)
            return self.get_paginated_response(data)

        return Response(get_search_data(search))


class ESRetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.to_dict())


class ESUpdateModelMixin:
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        form = self.get_form(data=request.data, partial=partial)
        if form.is_valid() is False:
            raise ValidationError(form.errors)
        data = form.cleaned_data
        if partial:
            data = {k: v for k, v in data.items() if k in request.data}
        self.perform_update(instance, data)
        return Response({**instance.to_dict(), **data})

    def perform_update(self, instance, data):
        if not data:
            return
        instance.update(**data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class ESDestroyModelMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
