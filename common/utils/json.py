import datetime
import decimal
import json
import uuid

from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware

from common.constants import DATE_FORMAT, DATETIME_FORMAT, TIME_FORMAT


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return o.strftime(DATETIME_FORMAT)
        elif isinstance(o, datetime.date):
            return o.strftime(DATE_FORMAT)
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            return o.strftime(TIME_FORMAT)
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o)
        elif isinstance(o, bytes):
            return o.decode()
        else:
            return super().default(o)
