from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('prediction:dashboard')
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('prediction:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def dashboard_view(request):
    return render(request, "dashboard.html")


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username and password:
            User.objects.create_user(username=username, password=password)
            return Response({"msg": "User created"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

def home(request):
    return render(request, "base.html")

import stripe
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    YOUR_DOMAIN = "http://localhost:8000"
    session = stripe.checkout.Session.create(
        customer_email=request.user.email,
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': 19900,
                'product_data': {
                    'name': 'Pro Membership',
                },
                'recurring': {
                    'interval': 'month',
                },
            },
            'quantity': 1,
        }],
        mode='subscription',
        success_url=YOUR_DOMAIN + '/success/',
        cancel_url=YOUR_DOMAIN + '/cancel/',
    )
    return Response({'url': session.url})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        email = event['data']['object']['customer_email']
        user = User.objects.filter(email=email).first()
        if user:
            user.userprofile.is_pro = True
            user.userprofile.save()

    elif event['type'] == 'customer.subscription.deleted':
        customer_email = event['data']['object']['customer_email']
        user = User.objects.filter(email=customer_email).first()
        if user:
            user.userprofile.is_pro = False
            user.userprofile.save()

    return HttpResponse(status=200)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_pro_status(request):
    profile = getattr(request.user, "userprofile", None)
    if profile is None:
        return Response({
            'error': 'UserProfile does not exist for this user.'
        }, status=500)

    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'is_pro': profile.is_pro
    })

def success_page(request):
    return render(request, 'templates/success.html')

def cancel_page(request):
    return render(request, 'templates/cancel.html')