from rest_framework.viewsets import ViewSetMixin

from elasticsearch_drf import mixins
from elasticsearch_drf.generics import ESGenericAPIView


class ESGenericViewSet(ViewSetMixin, ESGenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """

    pass


class ESModelViewSet(
    mixins.ESCreateModelMixin,
    mixins.ESRetrieveModelMixin,
    mixins.ESUpdateModelMixin,
    mixins.ESDestroyModelMixin,
    mixins.ESListModelMixin,
    ESGenericViewSet,
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    pass
