from django.db import models
from django.contrib.auth.models import AbstractUser

REGIONS = [
    ('toshkent', 'Toshkent'),
    ('samarqand', 'Samarqand'),
    ('buxoro', 'Buxoro'),
    ('fargona', 'Farg\'ona'),
    ('andijon', 'Andijon'),
    ('namangan', 'Namangan'),
    ('qashqadaryo', 'Qashqadaryo'),
    ('surxondaryo', 'Surxondaryo'),
    ('xorazm', 'Xorazm'),
    ('jizzax', 'Jizzax'),
    ('navoiy', 'Navoiy'),
    ('sirdaryo', 'Sirdaryo'),
    ('qoraqalpog\'iston', 'Qoraqalpog\'iston'),
]

class User(AbstractUser):
    # Add extra fields if needed (e.g., phone, region)
    region = models.CharField(max_length=255, blank=True, choices=REGIONS, default='toshkent')
    phone = models.CharField(max_length=20, blank=True)

    # For export history, etc. in the future
    def __str__(self):
        return self.username
        
    @property
    def region_choices(self):
        return dict(REGIONS)  # Template uchun qulay
