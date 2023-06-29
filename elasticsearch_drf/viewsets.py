from rest_framework.viewsets import ViewSetMixin

from elasticsearch_drf import mixins
from elasticsearch_drf.generics import ESGenericAPIView


class ESGenericViewSet(ViewSetMixin, ESGenericAPIView):
    """
    自定义基于ES模型的通用API视图, 不实现任何请求处理视图函数,
    但提供 get_object、get_search、filter_search、paginate_search 等方法
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
    自定义ES模型视图集,
    默认实现 create、retrieve、update、partial_update、destroy、list 请求处理视图函数
    """

    pass
