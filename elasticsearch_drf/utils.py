from itertools import islice
from typing import List

from elasticsearch_dsl import Search

from elasticsearch_drf.settings import api_settings


def get_search_data(search: Search) -> List[dict]:
    """
    执行ES search，返回查询结果
    :param search:
    :return:
    """
    d = search.to_dict()
    from_, size = d.get("from"), d.get("size")
    # scan用法参考：https://elasticsearch-py.readthedocs.io/en/master/helpers.html#scan
    scan_params = {"preserve_order": bool(d.get("sort")), "scroll": "1m", "size": 500}
    total = search.count()
    # 未指定任何分页参数
    if from_ is None and size is None:
        if total > api_settings.ES_MAX_OFFSET:
            resp = search.params(**scan_params).scan()
        else:
            resp = search[:total].execute()
    # 只指定分页size
    elif from_ is None:
        if size > api_settings.ES_MAX_OFFSET:
            resp = islice(search.params(**scan_params).scan(), size)
        else:
            resp = search.execute()
    # 只指定分页from
    elif size is None:
        if total > api_settings.ES_MAX_OFFSET:
            resp = islice(search.extra(from_=None).params(**scan_params).scan(), from_, total)
        else:
            resp = search[from_:total].execute()
    # 指定分页from和size
    else:
        if from_ + size > api_settings.ES_MAX_OFFSET:
            resp = islice(search.extra(from_=None).params(**scan_params).scan(), from_, from_ + size)
        else:
            resp = search.execute()

    data = [i.to_dict() for i in resp]
    return data
