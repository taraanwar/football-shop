import datetime
import requests
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404
from main.forms import ProductForm
from main.models import Product
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
import json
from main.models import Product

@login_required(login_url='/login')
def show_main(request):
    filter_type = request.GET.get("filter", "all")

    if filter_type == "all":
        products = Product.objects.all()
    else:
        products = Product.objects.filter(user=request.user)

    category = request.GET.get("category")
    if category:
        products = products.filter(category__iexact=category.strip())

    context = {
        "app_name": "Football Shop",
        "name": request.user.username,
        "class": "KKI",
        "npm": "2406365276",
        "products": products,
        "last_login": request.COOKIES.get("last_login", "Never"),
        "current_category": category or "all",
        "current_filter": filter_type,
    }
    return render(request, "main.html", context)


@login_required(login_url='/login')
def create_product(request):
    form = ProductForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_product.html", context)

@login_required(login_url='/login')
def show_product(request, id):
    product = get_object_or_404(Product, pk=id)
    context = {'product': product}
    return render(request, "product_detail.html", context)

def show_xml(request):
    products = Product.objects.all()
    xml_data = serializers.serialize("xml", products)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    products = Product.objects.select_related('user').all()
    data = [
        {
            'id': str(p.id),                # UUID -> string
            'name': p.name,
            'description': p.description,
            'category': p.category,         # "shoes" / "jersey"
            'thumbnail': p.thumbnail,       # URL
            'price': p.price,
            'is_featured': p.is_featured,
            'user_id': p.user_id,           # may be None if user is null
        }
        for p in products
    ]
    return JsonResponse(data, safe=False)

def show_xml_by_id(request, id):
    try:
        obj = Product.objects.filter(pk=id)
        xml_data = serializers.serialize("xml", obj)
        return HttpResponse(xml_data, content_type="application/xml")
    except Product.DoesNotExist:
        return HttpResponse(status=404)
    
def show_json_by_id(request, id):
    try:
        p = Product.objects.select_related('user').get(pk=id)
        data = {
            'id': str(p.id),
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'thumbnail': p.thumbnail,
            'price': p.price,
            'is_featured': p.is_featured,
            'user_id': p.user_id,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
    
def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
        user = form.get_user()
        login(request, user)
        response = HttpResponseRedirect(reverse("main:show_main"))
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

def edit_product(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(request.POST or None, instance=product)

    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "edit_product.html", context)

def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

@csrf_exempt
@require_POST
def add_product_entry_ajax(request):
    name = request.POST.get("name")
    price = request.POST.get("price")
    description = request.POST.get("description")
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'  # checkbox handling
    user = request.user

    new_product = Product(
        name=name,
        price=price or 0,
        description=description,
        category=category,
        thumbnail=thumbnail,
        is_featured=is_featured,
        user=user,
    )
    new_product.save()

    return HttpResponse(b"CREATED", status=201)

@csrf_exempt
@require_POST
def update_product_entry_ajax(request, id):
    try:
        p = Product.objects.get(pk=id, user=request.user)
    except Product.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)

    # get fields from form-data (like tutorial)
    p.name = request.POST.get("name", p.name)
    p.price = request.POST.get("price", p.price)
    p.description = request.POST.get("description", p.description)
    p.category = request.POST.get("category", p.category)
    p.thumbnail = request.POST.get("thumbnail", p.thumbnail)
    p.is_featured = request.POST.get("is_featured") == 'on'
    p.save()

    return JsonResponse({'detail': 'UPDATED'}, status=200)

@csrf_exempt
@require_POST
def delete_product_entry_ajax(request, id):
    try:
        p = Product.objects.get(pk=id, user=request.user)
    except Product.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)

    p.delete()
    return JsonResponse({'detail': 'DELETED'}, status=200)

@csrf_exempt
@require_POST
def login_ajax(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        response = JsonResponse({'detail': 'LOGGED_IN'})
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response
    return JsonResponse({'detail': 'Invalid credentials'}, status=400)


@csrf_exempt
@require_POST
def register_ajax(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'detail': 'REGISTERED'})
    error_text = '; '.join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
    return JsonResponse({'detail': error_text or 'Invalid data'}, status=400)


@csrf_exempt
@require_POST
def logout_ajax(request):
    logout(request)
    response = JsonResponse({'detail': 'LOGGED_OUT'})
    response.delete_cookie('last_login')
    return response

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def create_product_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON."},
                status=400,
            )

        name = strip_tags(data.get("name", ""))
        description = strip_tags(data.get("description", ""))
        category = data.get("category", "")
        thumbnail = data.get("thumbnail", "")
        is_featured = data.get("is_featured", False)
        price = data.get("price", 0)
        user = request.user if request.user.is_authenticated else None

        # Basic validation (optional but nice)
        if not name or not description:
            return JsonResponse(
                {"status": "error", "message": "Name and description are required."},
                status=400,
            )

        try:
            price = int(price)
        except (TypeError, ValueError):
            return JsonResponse(
                {"status": "error", "message": "Price must be an integer."},
                status=400,
            )

        # Create the product
        new_product = Product(
            name=name,
            description=description,
            category=category,
            thumbnail=thumbnail,
            price=price,
            is_featured=is_featured,
            user=user,
        )
        new_product.save()

        return JsonResponse({"status": "success"}, status=200)

    # If not POST:
    return JsonResponse({"status": "error", "message": "Invalid method."}, status=401)
