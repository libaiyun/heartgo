import logging

from django.utils.translation import gettext_lazy as _


class CustomException(Exception):
    """
    自定义项目异常基类,
    子类需要提供 CODE、MESSAGE 这两个属性
    """

    CODE = 10000
    MESSAGE = _("系统异常, 请联系管理员")
    LOG_LEVEL = logging.ERROR

    def __init__(self, message=None, data=None, *args):
        super().__init__(*args)
        self.code = self.CODE
        self.message = self.MESSAGE if message is None else message

        # 当异常有进一步处理时，需返回data
        self.data = data

    def __str__(self):
        return "{}({})".format(self.message, self.code)


class ParamValidationError(CustomException):
    CODE = 10001
    MESSAGE = _("参数验证失败")


class ParamFormatError(CustomException):
    CODE = 10002
    MESSAGE = _("参数格式化错误")
