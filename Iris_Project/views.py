import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from PIL import Image
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage, default_storage
from django.views.decorators.csrf import csrf_exempt
from tensorflow.keras.models import load_model
from django.utils import timezone

# Import models for image upload
from app.models import ImageUpload


# Admin check
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
@login_required
def custom_admin(request):
    users = User.objects.all()
    uploads = ImageUpload.objects.select_related('user').order_by('-timestamp')
    return render(request, 'admin/custom_admin.html', {
        'users': users,
        'uploads': uploads
    })

@user_passes_test(is_admin)
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            messages.error(request, "Cannot delete superuser.")
        else:
            user.delete()
            messages.success(request, "User deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
    return redirect('custom_admin')

@login_required
def home(request):
    return render(request, "home.html")

def predict(request):
    return render(request, 'predict.html')

@csrf_exempt
def result(request):
    result = None
    image_path = None

    # Case 1: Flower Dimension-based prediction (GET method)
    if request.method == "GET" and all(request.GET.get(f"n{i}") for i in range(1, 5)):
        try:
            # Load the dataset
            data = pd.read_csv("D:/END_SEM_PROJECT/Iris_Flower_Project/Iris_Project/iris.csv")
            X = data.drop("species", axis=1)
            Y = data["species"]

            # Train the model
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
            model = LogisticRegression(max_iter=200)
            model.fit(X_train, Y_train)

            # Get input values
            val1 = float(request.GET.get("n1"))
            val2 = float(request.GET.get("n2"))
            val3 = float(request.GET.get("n3"))
            val4 = float(request.GET.get("n4"))

            pred = model.predict([[val1, val2, val3, val4]])
            result = pred[0]
        except Exception as e:
            result = f"Error in prediction: {str(e)}"

    # Case 2: Image-based prediction (POST method)
    elif request.method == "POST" and 'flower_image' in request.FILES:
        try:
            uploaded_file = request.FILES['flower_image']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            filepath = fs.path(filename)
            image_path = fs.url(filename)

            # Load and preprocess image
            img = Image.open(filepath).convert('RGB')
            img = img.resize((150, 150))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Load pre-trained CNN model
            model = load_model("D:/END_SEM_PROJECT/Iris_Flower_Project/Iris_Project/model/iris_image_model.h5")
            predictions = model.predict(img_array)
            predicted_class_index = np.argmax(predictions)

            class_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
            result = class_names[predicted_class_index]

            # Save to DB
            if request.user.is_authenticated:
                ImageUpload.objects.create(
                    user=request.user,
                    image=uploaded_file,
                    predicted_class=result
                )

        except Exception as e:
            result = f"Error in image prediction: {str(e)}"

    return render(request, 'result.html', {
        'prediction': result,
        'image_path': image_path
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'auth/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already used.")
            return render(request, 'auth/register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect('home')

    return render(request, 'auth/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('register')
