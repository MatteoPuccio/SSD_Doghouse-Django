import json
import re

from django.core.validators import MinLengthValidator, RegexValidator, URLValidator
from django.db import models
from doghouse.settings import BASE_DIR
from dogs.validators import validate_date


def get_breeds():
    dog_breeds = json.load(open(f"{BASE_DIR}/resources/dog_breeds.json"))['dogs']
    return [(value, value) for value in dog_breeds]


breeds = get_breeds()
sexes = [('M', "Male"), ('F', "Female")]
sizes = [('XS', 'Extra Small'), ('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large')]


class Dog(models.Model):
    name = models.CharField(max_length=20,
                            validators=[RegexValidator(regex=r'^[A-Z][a-z]*$'), MinLengthValidator(2)],
                            default='Unnamed')
    breed = models.CharField(choices=breeds, max_length=50)
    sex = models.CharField(choices=sexes, max_length=1)
    birth_date = models.DateField(validators=[validate_date])
    entry_date = models.DateField(validators=[validate_date])
    neutered = models.BooleanField()
    description = models.CharField(max_length=400, validators=[RegexValidator(regex=r'^[a-zA-Z0-9,;. \-\t?!]*$')])
    estimated_size = models.CharField(choices=sizes, max_length=2)
    picture = models.CharField(validators=[URLValidator()], max_length=500, null=True)

    def __str__(self):
        return self.name
