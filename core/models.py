from django.db import models

class OrderStatus(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(unique=True, help_text='Порядковый номер для сортировки статусов')

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'
        ordering = ['order_index']

    def __str__(self):
        return self.name



class SiteSettings(models.Model):
    promo_text = models.CharField(
        max_length=255,
        default="АКЦИЯ: Скидки до 30% на все товары!",
        verbose_name="Текст акции в шапке сайта"
    )
    instagram_link = models.URLField(
        max_length=255,
        default="https://www.instagram.com/baizhigit_mebel",
        verbose_name="Ссылка на инстаграм"
    )
    whatsapp_link = models.URLField(
        max_length=255,
        default="https://wa.me/77783244835",
        verbose_name="Ссылка на WhatsApp"
    )
    main_index_text = models.CharField(
        max_length=150,
        default='Творим Дома <br> Из Мечты',
        verbose_name="Текст на главной странице",
    )
    second_index_text = models.CharField(
        max_length=150,
        default='Ваш идеальный интерьер начинается с мебели, созданной специально для вас.',
        verbose_name="Вторичный текст на странице",
    )
    business_age = models.IntegerField(
        default=15,
        help_text="15",
        verbose_name="Возраст бизнеса"
    )
    telephone_number = models.CharField(
        max_length=150,
        default="+7 (778) 324-48-35",
        verbose_name="Номер телефона"
    )
    address = models.CharField(
        max_length=255,
        default="Проспект Акжол, 20",
        verbose_name="Адрес"
    )
    twogis_link = models.URLField(
        max_length=255,
        default='https://go.2gis.com/9fZTM',
        verbose_name="Ссылка на 2GIS"
    )


    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'


class FAQ(models.Model):
    question = models.CharField(max_length=255, blank=False, null=False, verbose_name='Вопрос')
    answer = models.TextField(max_length=500, blank=False, null=False, verbose_name='Ответ')
    order = models.IntegerField(default=0, verbose_name='Порядковый номер')

    class Meta:
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Вопрос-ответ'
        ordering = ['order', 'question']

    def __str__(self):
        return self.question