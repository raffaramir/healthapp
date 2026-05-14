from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Service, Order


# ================= HOME =================
def home(request):
    services = Service.objects.all()

    print("SERVICES:", services)  # اختبار

    return render(request, 'home.html', {
        'services': services
    })


# ================= REGISTER =================
def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('home')

    return render(request, 'register.html')


# ================= LOGIN =================
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')


# ================= LOGOUT =================
def logout_user(request):
    logout(request)
    return redirect('home')


# ================= DASHBOARD =================
@login_required
def dashboard(request):

    if not request.user.is_superuser:
        return redirect('home')

    users = User.objects.all()
    orders = Order.objects.all()
    services = Service.objects.all()

    context = {
        'users': users,
        'orders': orders,
        'services': services,
        'users_count': users.count(),
    }

    return render(request, 'dashboard.html', context)


# ================= ADD SERVICE =================
@login_required
def add_service(request):

    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        Service.objects.create(
            title=title,
            description=description,
            price=price,
            image=image
        )

        return redirect('home')

    return render(request, 'add_service.html')


# ================= CREATE ORDER =================
@login_required
def create_order(request, service_id):

    service = Service.objects.get(id=service_id)

    if request.method == 'POST':
        phone = request.POST['phone']
        address = request.POST['address']

        Order.objects.create(
            user=request.user,
            service=service,
            phone=phone,
            address=address,
            status='Pending'
        )

        return redirect('home')

    return render(request, 'order_form.html', {
        'service': service
    })


from django.shortcuts import render, redirect

def chat_view(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        birth_date = request.POST.get("birth_date")
        birth_place = request.POST.get("birth_place")
        age = request.POST.get("age")
        phone = request.POST.get("phone")

        # رسالة WhatsApp
        message = f"""
Hello Doctor 👨‍⚕️
Name: {first_name} {last_name}
Birth Date: {birth_date}
Birth Place: {birth_place}
Age: {age}
Phone: {phone}
"""

        # رقم الطبيب (ضع رقمك هنا)
        doctor_number = "213661822299"

        whatsapp_url = f"https://wa.me/{doctor_number}?text={message}"

        return redirect(whatsapp_url)

    return render(request, "chat.html")