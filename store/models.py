from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name="Kategoriya nomi")
    image = models.ImageField(upload_to='categories/', null=True, blank=True,
                              verbose_name="Rasmi")
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Kategoriya",
                               related_name='subcategories')

    def get_absolut_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return 'https://sam.banketprofi.ru/i/7519-raskolbas/fotka-oformleniya-Restorany-Raskolbas--Krasnodara.jpg'

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Kategoriya pk={self.pk} title={self.title}"

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    price = models.FloatField(verbose_name="Narxi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Saytga qo'yilgan vaqti")
    quantity = models.IntegerField(default=0, verbose_name="Ombordagi soni")
    description = models.TextField(default="Bu yerda tez orada ma'lumot bo'ladi",
                                   verbose_name="Mahsulot haqida ma'lumot")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya",
                                 related_name="products")
    slug = models.SlugField(unique=True, null=True)
    size = models.IntegerField(default=30, verbose_name="mm dagi o'lchami")
    color = models.CharField(max_length=30, default="Kumush", verbose_name="Rangi/Material")

    def get_absolut_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Mahsulot: pk={self.pk} title={self.title}"

    def get_first_photo(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return 'https://stilsoft.ru/images/catalog/noup.png'
        else:
            return 'https://stilsoft.ru/images/catalog/noup.png'

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'


class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name="Rasm")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Rasm'
        verbose_name_plural = 'Rasmlar'



class Review(models.Model):
    text = models.TextField(verbose_name="Sharh matni")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = 'Sharh'
        verbose_name_plural = 'Sharhlar'



class FavouriteProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name="Tanlangan mahsulot")

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Tanlangan mahsulot'
        verbose_name_plural = 'Tanlangan mahsulotlar'


class Mail(models.Model):
    mail = models.EmailField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.mail

    class Meta:
        verbose_name = 'Pochta'
        verbose_name_plural = 'Pochtalar addressi'





class Customer(models.Model):
    user = models.OneToOneField(User, models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=255, default='', verbose_name="Foydalanuvchi ismi")
    last_name = models.CharField(max_length=255, default='', verbose_name="Foydalanuvchi familiyasi")

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Xaridor'
        verbose_name_plural = 'Xaridorlar'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL,
                                 blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    shipping = models.BooleanField(default=True)

    def __str__(self):
        return str(self.pk) + ' '

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'


    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum(product.quantity for product in order_products)
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Buyurtma qilingan mahsulot'
        verbose_name_plural = 'Buyurtma qilingan mahsulotlar'


    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=255)
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name="Shaharlar")
    state = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Yetkazib berish manzili'
        verbose_name_plural = 'Yetkazib berish manzillari'



class City(models.Model):
    city_name = models.CharField(max_length=255, verbose_name="Shaharlar nomi")

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name = 'Shahar'
        verbose_name_plural = 'Shaharlar'