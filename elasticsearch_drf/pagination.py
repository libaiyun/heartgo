from collections import OrderedDict

from rest_framework.response import Response

from elasticsearch_drf.settings import api_settings


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


class ESPagination:
    page_query_param = api_settings.PAGE_QUERY_PARAM
    page_size_query_param = api_settings.PAGE_SIZE_QUERY_PARAM
    page_size = api_settings.PAGE_SIZE
    max_page_size = None
    display_page_controls = False

    def __init__(self):
        self.total = None

    def paginate_search(self, search, request, view=None):
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            return None

        self.total = search.count()
        page_number = self.get_page_number(request)
        start = (page_number - 1) * self.page_size
        return search.extra(from_=start, size=self.page_size)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param], strict=True, cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_page_number(self, request):
        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            return _positive_int(page_number, strict=True)
        except ValueError:
            return 1

    def get_paginated_response(self, data):
        return Response(OrderedDict([("count", self.total), ("results", data)]))
