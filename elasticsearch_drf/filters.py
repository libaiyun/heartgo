from functools import reduce

from django.template import loader
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from elasticsearch_dsl import Q
from rest_framework.compat import coreapi, coreschema

from elasticsearch_drf.settings import api_settings


class ESBaseFilterBackend:
    """
    A base class from which all filter backend classes should inherit.
    """

    def filter_search(self, request, search, view):
        """
        Return a filtered search.
        """
        raise NotImplementedError(".filter_search() must be overridden.")

    def get_schema_fields(self, view):
        assert coreapi is not None, "coreapi must be installed to use `get_schema_fields()`"
        assert coreschema is not None, "coreschema must be installed to use `get_schema_fields()`"
        return []

    def get_schema_operation_parameters(self, view):
        return []


class ESFilter(ESBaseFilterBackend):
    def get_filter_kwargs(self, request, search, view):
        filter_fields = getattr(view, "filter_fields", [])

        filter_kwargs = {k: v for k, v in request.query_params.items() if k in filter_fields}
        return filter_kwargs

    def filter_search(self, request, search, view):
        filter_kwargs = self.get_filter_kwargs(request, search, view)
        if not filter_kwargs:
            return search

        dsl = reduce(
            lambda x, y: x & y,
            [Q("terms" if isinstance(v, list) else "term", **{k: v}) for k, v in filter_kwargs.items()],
        )
        return search.query(dsl)


class ESearchFilter(ESBaseFilterBackend):
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    template = "rest_framework/filters/search.html"
    search_title = _("Search")
    search_description = _("A search term.")

    def get_search_fields(self, view, request):
        # search_fields 须是Text类型
        return getattr(view, "search_fields", None)

    def get_search_term(self, request):
        """
        Search term is set by a ?search=... query parameter.
        """
        param = request.query_params.get(self.search_param, "")
        return param.strip()

    def filter_search(self, request, search, view):
        search_fields = self.get_search_fields(view, request)
        search_term = self.get_search_term(request)

        if not search_fields or not search_term:
            return search

        return search.query("multi_match", query=search_term, fields=search_fields)

    def to_html(self, request, search, view):
        if not getattr(view, "search_fields", None):
            return ""

        term = self.get_search_term(request)
        context = {"param": self.search_param, "term": term}
        template = loader.get_template(self.template)
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, "coreapi must be installed to use `get_schema_fields()`"
        assert coreschema is not None, "coreschema must be installed to use `get_schema_fields()`"
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location="query",
                schema=coreschema.String(
                    title=force_str(self.search_title), description=force_str(self.search_description)
                ),
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.search_param,
                "required": False,
                "in": "query",
                "description": force_str(self.search_description),
                "schema": {
                    "type": "string",
                },
            },
        ]


class ESOrderingFilter(ESBaseFilterBackend):
    ordering_param = api_settings.ORDERING_PARAM
    ordering_fields = None
    ordering_title = _("Ordering")
    ordering_description = _("Which field to use when ordering the results.")
    template = "rest_framework/filters/ordering.html"

    def get_ordering(self, request, search, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.

        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(",")]
            ordering = self.remove_invalid_fields(fields, request, view)
            if ordering:
                return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)

    def get_default_ordering(self, view):
        ordering = getattr(view, "ordering", None)
        if isinstance(ordering, str):
            return (ordering,)
        return ordering

    def get_valid_fields(self, request, view):
        valid_fields = getattr(view, "ordering_fields", self.ordering_fields)
        model_class = getattr(view, "model_class", None)
        assert model_class is not None

        if valid_fields is None or valid_fields == "__all__":
            mappings = list(model_class._index.get_mapping().values())
            properties = mappings[0]["mappings"]["properties"]
            valid_fields = list(properties)

        return valid_fields

    def remove_invalid_fields(self, fields, request, view):
        valid_fields = self.get_valid_fields(request, view)

        def term_valid(term):
            if term.startswith("-"):
                term = term[1:]
            return term in valid_fields

        return [term for term in fields if term_valid(term)]

    def filter_search(self, request, search, view):
        ordering = self.get_ordering(request, search, view)

        if ordering:
            return search.sort(*ordering)

        return search

    def get_template_context(self, request, search, view):
        current = self.get_ordering(request, search, view)
        current = None if not current else current[0]
        options = []
        context = {
            "request": request,
            "current": current,
            "param": self.ordering_param,
        }
        for field in self.get_valid_fields(request, view):
            options.append((field, "{} - {}".format(field, _("ascending"))))
            options.append(("-" + field, "{} - {}".format(field, _("descending"))))
        context["options"] = options
        return context

    def to_html(self, request, search, view):
        template = loader.get_template(self.template)
        context = self.get_template_context(request, search, view)
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, "coreapi must be installed to use `get_schema_fields()`"
        assert coreschema is not None, "coreschema must be installed to use `get_schema_fields()`"
        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location="query",
                schema=coreschema.String(
                    title=force_str(self.ordering_title), description=force_str(self.ordering_description)
                ),
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.ordering_param,
                "required": False,
                "in": "query",
                "description": force_str(self.ordering_description),
                "schema": {
                    "type": "string",
                },
            },
        ]
