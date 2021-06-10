from io import BytesIO
from PIL import Image
from django.core import files
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


class UserProfile(AbstractUser):
    age = models.PositiveIntegerField(default=18,
                                      verbose_name='Возраст')
    image = models.ImageField(upload_to='users/',
                              default='default.png',
                              max_length=100,
                              verbose_name='Фоточка')
    thumbnail = models.ImageField(upload_to='users/',
                                  blank=True, null=True)
    is_teacher = models.BooleanField(default=False,
                                     verbose_name='Преподаватель')
    # USERNAME_FIELD = 'email'
    # email = models.EmailField(_('email address'),
    #                           unique=True)
    # REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''

    def get_thumbnail(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000' + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return 'http://127.0.0.1:8000' + self.thumbnail.url
            else:
                return ''

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thumb_io = BytesIO()
        img.save(thumb_io, 'svg', quality=85)
        thumbnail = files.File(thumb_io, name=image.name)
        return thumbnail
