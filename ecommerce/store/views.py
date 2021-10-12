from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseNotFound
import json
import datetime


from .models import *
from .models import Customer
from . utils import cookie_cart, cart_data, guest_order


def store(request):
    data = cart_data(request)
    cart_items = data['cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cart_items': cart_items}
    return render(request, 'store/store.html', context)


def login(request: HttpRequest):
    if request.method == "GET":
        error = request.session.get("error", None)
        if error is not None:
            del request.session['error']
        context = {"error": error}
        return render(request, "store/login.html", context)
    if request.method == "POST":
        try:
            login_user = User.objects.get(username=request.POST['username'])
            if login_user.verify_password(request.POST['password']):
                request.session['user'] = login_user.to_dict()
                return redirect("store")
        except:
            pass
        request.session['error'] = "Username and/or password invalid."
        return redirect("login")

def logout(request: HttpRequest):
    user = request.session.get('user', None)
    if user is not None:
        request.session['success'] = "You have successfully logged out."
        del request.session['user']
    return redirect('login')


def register(request: HttpResponse):
    if request.method == "GET":
        return render(request, "store/registration.html")
    if request.method == "POST":
        new_user = User()
        new_user.first_name = request.POST['first_name']
        new_user.last_name = request.POST['last_name']
        new_user.username = request.POST['username']
        new_user.create_hashed_password(request.POST['password'])
        try:
            new_user.save()
            #return  HttpResponse("User has been saved!")
            return redirect("login")
        except IntegrityError as iex:
            return HttpResponseNotFound(f"User with username {request.POST['username']} already exists.")
        except Exception as ex:
            return HttpResponseNotFound(f"{ex}")


def view_profile(request: HttpRequest, username: str):
    try:
        error = request.session.get('error', None)
        if error is not None:
            del request.session['error']
        selected_user = User.objects.get(username=username)
        context = {"user": selected_user}
        return render(request, "store/profile.html", context)
    except:
        request.session['error'] = f"No user with username '{username}' found."
        return redirect("store")


def cart(request):

    data = cart_data(request)
    cart_items = data['cart_items']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cart_data(request)
    cart_items = data['cart_items']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId'] #iz cart.js body fetch
    action = data['action'] #iz cart.js body fetch

    print('action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False) 

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product) #ako postoji OrderItem u orderu ili u productu
        # ne zelimo kreirati novi proizvod vec samo promeniti kolicinu

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)

#from django.views.decorators.csrf import csrf_exempt

#@csrf_exempt
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guest_order(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse("Payment complete!", safe=False)

def details(request, id):
    data = cart_data(request)
    cart_items = data['cart_items']

    products = Product.objects.filter(id=id)
    context = {'products': products, 'cart_items': cart_items}
    return render(request, 'store/single_product.html', context)
