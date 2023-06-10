from django.http import Http404
from rest_framework.views import APIView

from elasticsearch_drf.settings import api_settings


class ESGenericAPIView(APIView):
    form_class = None
    model_class = None

    # If you want to use object lookups other than _id, set 'lookup_field'.
    # For more complex lookup requirements override `get_object()`.
    lookup_field = "_id"
    lookup_url_kwarg = None

    permission_classes = []

    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS

    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_form(self, *args, **kwargs):
        assert self.form_class is not None, (
            "'%s' should either include a `form_class` attribute, "
            "or override the `get_form()` method." % self.__class__.__name__
        )
        partial = kwargs.pop("partial", False)
        form = self.form_class(*args, **kwargs)
        if partial:
            for field in form.fields.values():
                field.required = False
        return form

    def get_search(self):
        assert self.model_class is not None, (
            "'%s' should either include a `model_class` attribute, "
            "or override the `get_search()` method." % self.__class__.__name__
        )
        return self.model_class().search()

    def get_object(self):
        search = self.filter_search(self.get_search())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj = search.query("term", **filter_kwargs).execute()[0]
        except IndexError:
            raise Http404

        return obj

    def filter_search(self, search):
        for backend in list(self.filter_backends):
            search = backend().filter_search(self.request, search, self)
        return search

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_search(self, search):
        if self.paginator is None:
            return None
        return self.paginator.paginate_search(search, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
