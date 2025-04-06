from django.shortcuts import render

# Create your views here.

import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse

from django.http import JsonResponse
import json
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')  

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Log the user in
        login(request, user)
        return redirect('home')

    return render(request, 'register.html')
    



def dashboard_view(request):
    location = request.GET.get('location')
    weather_data = None
    activity_suggestions = None
    email_sent = False
    email_error = None

    if not location:
        return render(request, 'dashboard.html', {
            'weather_data': None,
            'activity_suggestions': None,
            'email_sent': email_sent,
            'email_error': email_error
        })

    weather_api_url = f"https://65wb2cfcug.execute-api.eu-west-1.amazonaws.com/hproduction/get-weather?location={location}"
    activity_api_url = f"https://65wb2cfcug.execute-api.eu-west-1.amazonaws.com/hproduction/suggest-activities?location={location}"

    try:
        # Fetch weather data
        response = requests.get(weather_api_url)
        response_data = response.json()

        if response.status_code == 200:
            weather_data = {
                'location': location.capitalize(),
                'weather': response_data.get('weather', 'N/A'),
                'description': response_data.get('description', 'N/A'),
                'temperature': response_data.get('temperature', 'N/A')
            }
        else:
            weather_data = {
                'location': location.capitalize(),
                'weather': 'N/A',
                'description': 'Unable to fetch weather data.',
                'temperature': 'N/A'
            }

        # Fetch activity suggestions
        activity_response = requests.get(activity_api_url)
        activity_response_data = activity_response.json()

        if activity_response.status_code == 200:
            activity_suggestions = activity_response_data.get('suggested_activities', [])
            if not activity_suggestions:
                activity_suggestions = ["No activities found for the current weather condition."]
        else:
            activity_suggestions = ["Error occurred while fetching activity suggestions."]

        # Handle email sending
        if request.method == 'POST':
            user_email = request.POST.get('email')
            subject = f"Weather and Activity Info for {location.capitalize()}"
            content = f"""
                    Weather in {weather_data['location']}:
                    Condition: {weather_data['weather']}
                    Temperature: {weather_data['temperature']}°C
                    Description: {weather_data['description']}
                    
                    Suggested Activities:
                    {chr(10).join(activity_suggestions)}
                    """

            email_api_url = "https://574zxm1da6.execute-api.eu-west-1.amazonaws.com/default/x23271281-EmailSenderAPI"
            email_payload = {
                "email": user_email,
                "subject": subject,
                "content": content
            }

            headers = {'Content-Type': 'application/json'}
            try:
                email_response = requests.post(email_api_url, json=email_payload, headers=headers)
                if email_response.status_code == 200:
                    email_sent = True
                else:
                    email_error = "Failed to send email."
            except Exception as e:
                email_error = str(e)

    except Exception as e:
        weather_data = {
            'location': location.capitalize(),
            'weather': 'N/A',
            'description': 'Error occurred while fetching data.',
            'temperature': 'N/A'
        }
        activity_suggestions = ["Error occurred while fetching activity suggestions."]

    context = {
        'weather_data': weather_data,
        'activity_suggestions': activity_suggestions,
        'email_sent': email_sent,
        'email_error': email_error,
    }

    return render(request, 'dashboard.html', context)


# OpenWeather API Key
# OPENWEATHER_API_KEY = "61e93c3b21eadf5aac1ddab2b9979978"

# @api_view(['GET'])
# def suggest_activities(request):
#     location = request.GET.get('location')
#     date = request.GET.get('date')

#     # Call OpenWeather API to get weather data
#     weather_data = get_weather_data(location, date)
#     if not weather_data:
#         return Response({"error": "Unable to fetch weather data"}, status=500)

#     weather_condition = weather_data['weather'][0]['main'].lower()

#     # Suggest activities based on weather condition
#     activities = get_activity_suggestions(weather_condition)

#     # Return response
#     return Response({
#         "location": location,
#         "date": date,
#         "weather": weather_condition,
#         "suggested_activities": activities
#     })
    
    
# def get_weather_data(location, date):
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching weather data: {e}")
#         return None

# def get_activity_suggestions(weather_condition):
#      # Mapping OpenWeather conditions to custom conditions
#     condition_mapping = {
#         "Clear": "sunny",
#         "Clouds": "cloudy",
#         "Rain": "rainy",
#         "Snow": "snowy",
#         "Thunderstorm": "rainy",
#         "Drizzle": "rainy",
#         "Mist": "cloudy",
#         "Smoke": "cloudy",
#         "Haze": "cloudy",
#         "Fog": "cloudy",
#         "Dust": "cloudy",
#         "Tornado": "rainy",
#     }

#     # Get the custom condition (default to "cloudy" if not found)
#     custom_condition = condition_mapping.get(weather_condition, "cloudy")

#     # Suggest activities based on the custom condition
#     if custom_condition == "sunny":
#         return ["Go Hiking", "Visit a Park", "Have a Picnic"]
#     elif custom_condition == "rainy":
#         return ["Visit a Museum", "Watch a Movie", "Try a Café"]
#     elif custom_condition == "snowy":
#         return ["Go Skiing", "Build a Snowman", "Drink Hot Chocolate"]
#     elif custom_condition == "cloudy":
#         return ["Go for a Walk", "Visit an Art Gallery", "Read a Book"]
#     else:
#         return ["Check out local events"]