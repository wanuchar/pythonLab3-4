from io import BytesIO
from PIL import Image
from django.core import files
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from users.models import UserProfile
from django.template.loader import render_to_string


class Subject(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(UserProfile,
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(UserProfile,
                                   related_name='courses_joined',
                                   blank=True)
    image = models.ImageField(upload_to='uploads/',
                              blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/',
                                  blank=True, null=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_image(self):
        if self.image:
            return self.image.url
        return ''

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return self.thumbnail.url
            else:
                return ''

    @staticmethod
    def make_thumbnail(image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        thumbnail = files.File(thumb_io, name=image.name)
        return thumbnail


class Module(models.Model):
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)


class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={
                                         'model__in': ('text',
                                                       'picture',
                                                       'video',
                                                       'file')
                                     })
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(UserProfile,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(
            'courses/content/{}.html'.format(self._meta.model_name),
            {'item': self}
        )


class Text(ItemBase):
    content = models.TextField()

    class Meta:
        verbose_name = 'Информация'


class File(ItemBase):
    file = models.FileField(upload_to='files')

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'


class Picture(ItemBase):
    picture = models.FileField(upload_to='images')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def get_picture(self):
        if self.picture:
            return self.picture.url
        return ''


class Video(ItemBase):
    url = models.URLField()

    class Meta:
        verbose_name = 'Видео'
