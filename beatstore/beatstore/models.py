from django.conf import settings

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Genre(models.Model):
    """Жанр"""

    name = models.CharField(max_length=100, verbose_name='Жанр')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class LicenseType(models.Model):
    """Тип лицензии"""

    name = models.CharField(max_length=100, verbose_name='Название лицензии')
    description = models.TextField(verbose_name='Описание лицензии')
    file_type = models.CharField(max_length=100, verbose_name='Формат файла')
    number_of_copies = models.CharField(max_length=255, verbose_name='Количество копийй')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип лицензии'
        verbose_name_plural = 'Типы лицензий'


class Beatmaker(models.Model):
    """Битмейкер"""

    name = models.CharField(max_length=100, verbose_name='Битмейкер')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Битмейкер'
        verbose_name_plural = 'Битмейкеры'


class Beat(models.Model):
    """Бит"""

    beatmaker = models.ForeignKey(Beatmaker,
                                  on_delete=models.CASCADE,
                                  blank=False,
                                  verbose_name='Битмейкер')
    title = models.CharField(max_length=255, verbose_name='Бит')
    license = models.ManyToOneRel(LicenseType, related_name='beat')
    genre = models.ManyToOneRel(Genre, related_name='beat')
    release_date = models.DateField(verbose_name='Дата релиза')
    slug = models.SlugField
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    discount = models.BooleanField(deafult=False, verbose_name='Скидка ')

    def __str__(self):
        return f'{self.id} | {self.title} | {self.beatmaker}'

    @property
    def content_type_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = 'Бит'
        verbose_name_plural = 'Биты'


class Playlist(models.Model):
    """Плейлист"""

    name = models.CharField(max_length=255, verbose_name='Плейлист')
    beats = models.ManyToManyField(Beat,
                                   verbose_name='Бит',
                                   related_name='playlist')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'


class CartProduct(models.Model):
    """Продукт корзины"""

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_od = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Продукт: {self.content_object.name} (для корзины)'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Cart(models.Model):
    """Корзины"""

    owner = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField(
        CartProduct, blank=True, null=True, related_name='related_cart', verbose_name='Продукты для корзины'
    )
    total_products = models.IntegerField(default=0, verbose_name='Общее количество товаров')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    """Заказ пользователя"""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'is_ready'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', related_name='orders', on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    email = models.CharField(max_length=255, verbose_name='Email')
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateField(verbose_name='Дата создания заказа', auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Customer(models.Model):
    """Покупатель"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    is_active = models.BooleanField(default=True, verbose_name='Активный?')
    customer_orders = models.ManyToManyField(
        Order, blank=True, related_name='related_customer', verbose_name='Заказы покупателя'
    )
    whishlist = models.ManyToManyField(Beat, blank=True, verbose_name='Список желаемого')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    email = models.CharField(max_length=255, verbose_name='Email')

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Notification(models.Model):
    """Уведомления"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Уведомление для {self.recipient.user.username} | id={self.id}'

    class Meta:
        verbose_name = 'Уведомеление'
        verbose_name_plural = 'Уведомеления'
