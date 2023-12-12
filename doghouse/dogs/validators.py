import datetime
from django.core.exceptions import ValidationError


def validate_date(value: datetime.date):
    if value < datetime.date(1980, 1, 1):
        raise ValidationError("Date must be after year 1979")
    if value > datetime.date.today():
        raise ValidationError("Date must be at most today")

