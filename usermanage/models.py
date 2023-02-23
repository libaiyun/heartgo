from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    nickname = models.CharField(
        _("nick name"),
        max_length=64,
        blank=True,
        help_text="Required. 64 characters or fewer.",
    )
    phone = models.CharField(_("phone number"), max_length=64, blank=True)

    REQUIRED_FIELDS = ["nickname"]

    def get_full_name(self):
        full_name = "{}({})".format(self.nickname, self.username)
        return full_name

    def get_short_name(self):
        return self.nickname
