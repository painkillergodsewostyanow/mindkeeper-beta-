from django.db.models.fields.files import ImageFieldFile
from django.db import models
from PIL import Image


class ResizeImageOnSaveMixin:
    max_height = 800
    max_weight = 600
    resize_image_fields = []

    def init_resize_image_fields(self):
        temp = []
        if len(self.resize_image_fields) == 0:
            for field in self._meta.get_fields():
                if isinstance(field, models.ImageField):
                    str_field_repr = str(field)
                    field_name = str_field_repr[str_field_repr.rfind('.') + 1:]
                    field = getattr(self, field_name)
                    temp.append(field)

        else:
            for field_name in self.resize_image_fields:
                field = getattr(self, field_name, False)

                if field is False:
                    raise TypeError(f'Поля {field_name} несуществует')

                if not isinstance(field, ImageFieldFile):
                    raise TypeError(f'Введенное вами поле {field_name} не являеться ImageField')

                temp.append(field)

        return temp

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_fields = self.init_resize_image_fields()
        for field in resize_fields:
            if field:
                image = Image.open(field.path)
                if image.height > self.max_height or image.width > self.max_weight:
                    image.thumbnail((self.max_height, self.max_weight))
                    image.save(field.path)


class CompressImageOnSaveMixin:
    quality = 70
    compress_image_fields = []

    def init_compress_image_fields(self):
        temp = []
        if len(self.resize_image_fields) == 0:
            for field in self._meta.get_fields():
                if isinstance(field, models.ImageField):
                    str_field_repr = str(field)
                    field_name = str_field_repr[str_field_repr.rfind('.') + 1:]
                    field = getattr(self, field_name)
                    temp.append(field)

        else:
            for field_name in self.resize_image_fields:
                field = getattr(self, field_name, False)

                if field is False:
                    raise TypeError(f'Поля {field_name} несуществует')

                if not isinstance(field, ImageFieldFile):
                    raise TypeError(f'Введенное вами поле {field_name} не являеться ImageField')

                temp.append(field)

        return temp

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        compress_fields = self.init_compress_image_fields()
        for field in compress_fields:
            if field:
                image = Image.open(field.path)
                image = image.convert('RGB')
                image.save(fp=field.path, format='JPEG', quality=self.quality)
