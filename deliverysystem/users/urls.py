from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
from users.views import About, Contact
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_request, name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
    path('about/', About.as_view(), name="about"),
    path('contact/', Contact.as_view(), name="contact"),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('adminMenu/<menu>/', views.adminSeeProducts, name='restaurantProducts'),
    path('deliveryguy/', views.deliveryguy, name='deliveryguy'),
    path('adminRestaurant/<idMenu>/', views.RestaurantEditProxy.adminSeeRestaurant, name='myRestaurant'),
    path('adminRestaurantEdit/<int:id>/', views.RestaurantEditProxy.editRestaurant, name='myRestaurantEdit'),
    path('clientMenu/<int:restid>/', views.clientSeeRestaurant, name='namedUrl'),
    path('productDetails/<int:productId>', views.productDetails, name='namedProductDetailsUrl'),
    path('adminEditAProduct/<int:productId>', views.adminEditAProduct, name='editAProduct'),
    path('update_item/', views.updateItem, name="update_item"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)