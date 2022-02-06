from django.db import models
from django.contrib.auth.models import User


class AdministratorRestaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True)
    surname = models.CharField(max_length=50, null=True)
    adress = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=10, null=True)
    employment_date = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.first_name + self.surname


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name or ''


class Menu(models.Model):
    name = models.CharField(max_length=50)
    menu_type = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    menu = models.OneToOneField(
        Menu,
        on_delete=models.CASCADE,
    )
    administrator = models.OneToOneField(
        AdministratorRestaurant,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    restaurant_name = models.CharField(max_length=1000, null=True)
    restaurant_image = models.ImageField(null=True, blank=True)
    restaurant_owner = models.CharField(max_length=1000, null=True, blank=True)
    restaurant_phone = models.CharField(max_length=10, null=True)
    restaurant_addres = models.CharField(max_length=10000, null=True, blank=True)
    restaurant_opentime = models.TimeField(null=True, blank=True)
    restaurant_closetime = models.TimeField(null=True, blank=True)


    @property
    def imageURL(self):
        try:
            url = self.restaurant_image.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.restaurant_name


# MenuItem
class Product(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=3000)
    product_image = models.ImageField(null=True, blank=True)
    product_description = models.TextField(max_length=10000, null=True, blank=True)
    product_price = models.PositiveIntegerField()
    vegan = models.BooleanField(null=True, blank=True)
    vegetarian = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.product_name

    @property
    def imageURL(self):
        try:
            url = self.product_image.url
        except:
            url = ''
        return url


class DeliveryGuy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    phoneNumber = models.CharField(max_length=10, null=True, blank=True)

    #pentru Observer
    def __init__(self,name):
            self.name=name
    def update(self, orderAvailable):
        print (' {}, there is a new order available: "{}" !'.format(self.name, orderAvailable))

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    #aici incerc sa implementez design pattern-ul observer pentru ca atunci cand o comanda este afcuta sa se afiseze in pagina livratorului
    def __init__(self, newOrders):
        self.observers={order: dict()
                        for order in newOrders}
    def get_observers(self, newOrder):
        return self.observers[newOrder]
    #register/unregister allows the observer to register itself with the observable
    def register(self, newOrderEvent, deliveryGuy, callback=None):
        if callback is None:
                callback=getattr(deliveryGuy, 'update')
        self.get_observers(newOrderEvent)[deliveryGuy] = callback
    def unregister(self, event, who):
            del self.get_subscribers(event)[who]
    #when this method is invocked, every observer has its update methos invocked
    def dispatch(self, event, message):
        for subscriber, callback in self.get_observers(event).items():
            callback(message)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.product)

    @property
    def get_total(self):
        total = self.product.product_price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.address

#implementing Singleton Design Pattern for working with db
class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj