import json
import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator, URLValidator, MaxLengthValidator
from django.db import models
from doghouse.settings import BASE_DIR
from dogs.validators import validate_date

picture_source_prefix = 'https://i.imgur.com/'


def get_breeds():
    dog_breeds = json.load(open(f"{BASE_DIR}/resources/dog_breeds.json"))['dogs']
    return [(value, value) for value in dog_breeds]


breeds = get_breeds()
sexes = [('M', "Male"), ('F', "Female")]
sizes = [('XS', 'Extra Small'), ('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large')]


class Dog(models.Model):
    name = models.CharField(max_length=20,
                            validators=[RegexValidator(regex=r'^[A-Z][a-z]+$',
                                                       message='Dog name cannot contain invalid characters\
                                                        and must only have an uppercase character at the start.'),
                                        MinLengthValidator(2)],
                            default='Unnamed', help_text='Dog name')
    breed = models.CharField(choices=breeds, max_length=50)
    sex = models.CharField(choices=sexes, max_length=1)
    birth_date = models.DateField(validators=[validate_date])
    entry_date = models.DateField(validators=[validate_date])
    neutered = models.BooleanField()
    description = models.TextField(
        validators=[RegexValidator(regex=r'^[a-zA-Z0-9,;. \-\t?!]*$',
                                   message='Dog description cannot contain invalid characters.'),
                    MaxLengthValidator(400)],
        blank=True, default='', help_text='Dog description')
    estimated_adult_size = models.CharField(choices=sizes, max_length=2)
    picture = models.CharField(validators=[RegexValidator(rf'^{picture_source_prefix}.*$',
                                                          message=f"Image must have prefix {picture_source_prefix}")],
                               max_length=200, help_text='Dog picture url',
                               blank=True, default='')
    interested_users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.entry_date is None:
            raise ValidationError('Entry date must be specified')
        if self.birth_date is None:
            raise ValidationError('Birth date must be specified')
        if self.entry_date < self.birth_date:
            raise ValidationError("Entry date must be after birth date")
        return super().clean()
