from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from .forms import RestaurantEditDetailsForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import *
from django.http import JsonResponse
from abc import ABCMeta, abstractmethod


import json

def home(request):
    restaurants = Restaurant.objects.all()
    context = {'restaurants': restaurants}
    return render(request, 'users/home.html', context)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hi {username}, your account was created successfully')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if "admin_" in username:
                login(request, user)
                return redirect(f'http://127.0.0.1:8000/adminRestaurant/{AdministratorRestaurant.objects.filter(user=user).values_list("id", flat=True).first()}/')
            elif "delivery_" in username:
                login(request, user)
                if request.user.is_authenticated:
                    try:
                        deli = request.user.deliveryguy
                    except DeliveryGuy.DoesNotExist:
                        deli = DeliveryGuy(
                            user=request.user,
                            name=request.user,
                        )
                        deli.save()
                return redirect('deliveryguy')
            else:
                login(request, user)
                return redirect('home')
    form = AuthenticationForm()
    return render(request, "users/login.html", {'form': form})


@login_required()
def profile(request):
    return render(request, 'users/profile.html')


def cart(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer(
                user=request.user,
                name=request.user,
                email=request.user.email,
            )
            customer.save()
        finally:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            order.save()
            items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}

    context = {'items': items, 'order': order}
    return render(request, 'users/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}

    context = {'items': items, 'order': order}
    return render(request, 'users/checkout.html', context)


class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/about.html')


class Contact(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/contact.html')


def adminSeeProducts(request, menu):
    products = Product.objects.filter(menu_id=menu)
    context = {'products': products}
    return render(request, 'users/adminSeeMenu.html', context)



class RestaurantEdit:
    def adminSeeRestaurant(request, idMenu):
        print("See Restaurant....")

    def editRestaurant(request, id):
        print("Editing restaurant details....")


class RestaurantEditProxy:

    def adminSeeRestaurant(request, idMenu):
        r = Restaurant.objects.filter(menu_id=idMenu)
        print("Proxy in action. Checking the admin's id...")
        context = {'restaurants': r}
        return render(request, 'users/adminViewRestaurant.html', context)


    def editRestaurant(request,id):
        restaurant = Restaurant.objects.get(administrator_id=id)
        print(restaurant)
        print("Proxy in action. Checking to see if the data is valid or not...")
        if request.POST.get('phoneNumber') and request.POST.get('address') and request.POST.get('opentime') and request.POST.get('closetime'):
            restaurant.restaurant_phone = request.POST.get('phoneNumber')
            restaurant.restaurant_addres = request.POST.get('address')
            restaurant.restaurant_opentime = request.POST.get('opentime')
            restaurant.restaurant_closetime = request.POST.get('closetime')
            restaurant.save()
            return redirect("/adminMenu/{}/".format(id))
        return render(request, 'users/adminRestaurantEdit.html', {'restaurant': restaurant})


def clientSeeRestaurant(request, restid):
    productss = Product.objects.filter(menu_id=restid)
    context = {'productss': productss}
    return render(request, 'users/clientRestaurant.html', context)


def productDetails(request, productId):
    p = Product.objects.filter(id=productId)
    context = {'product': p}
    return render(request, 'users/details.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('action:',action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

  
def adminEditAProduct(request, productId):
    prod = Product.objects.filter(id=productId)
    context = {'product': prod}
    return render(request, 'users/adminProductEdit.html', context)




# Observer

class IObservable(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def subscribe(observer):
        """the subscribe method"""

    @staticmethod
    @abstractmethod
    def unsubscribe(observer):
        """the unsubscribe method"""

    @staticmethod
    @abstractmethod
    def notify(observer):
        """the notify method"""


class Subject(IObservable):
    def __init__(self):
        self._observers = set()

    def subscribe(self, observer):
        self._observers.add(observer)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def notify(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)

    @property
    def observers(self):
        return self._observers


class IObserver(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def notify(observable, *args, **kwargs):
        """Receive notifications"""


class Observer(IObserver):
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, observable, *args, **kwargs):
        print("You received a new order!")


def deliveryguy(request):
    orders = Order.objects.all()
    items = set()
    for order in orders:
        item = order.orderitem_set.all()
        items.add(item)

    subj = Subject()

    for deliveryGuy in DeliveryGuy.objects.all():
        if deliveryGuy not in subj._observers:
            subj.subscribe(deliveryGuy)

    initialCnt = Order.objects.count()
    cnt = Order.objects.count()
    if cnt > initialCnt:
        for sub in subj._observers:
            subj.notify(sub)

    context = {'items': items, 'orders': orders}
    return render(request, 'users/deliveryguy.html', context)

