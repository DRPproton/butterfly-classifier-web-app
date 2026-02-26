from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .forms import ImageUploadForm
from .prediction_model.prediction import predict_from_memory
import os
import time
from django.conf import settings
import base64
from io import BytesIO
from PIL import Image
from .butterfly_details import BUTTERFLY_DETAILS

@login_required
def index(request):
    prediction = None
    image_url = None
    error_message = None
    confidence = None 
    # Mock Data for UI to match design
    scientific_name = None
    description = None
    habitat = None
    common_in = None
    
    # Database of details (Simplified for tutorial)

    

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the file from request
                image_file = request.FILES['image']
                
                # 1. Open Image in Memory (PIL)
                img = Image.open(image_file)
                
                # 2. Create Base64 String for Display (UI)
                # We need to save the PIL image to a BytesIO buffer first
                buffered = BytesIO()
                img.save(buffered, format="JPEG") # Convert to JPEG for display consistency
                img_str = base64.b64encode(buffered.getvalue()).decode()
                image_url = f"data:image/jpeg;base64,{img_str}"
                
                # 3. Predict from Memory
                # We pass the PIL image object directly
                prediction, conf = predict_from_memory(img)
                confidence = f"{conf * 100:.1f}%"
                
                # Dynamic Details Lookup
                details = BUTTERFLY_DETAILS.get(prediction, {
                    'scientific': 'Unknown Species', 
                    'desc': 'No description available for this species yet.',
                    'habitat': 'Unknown',
                    'common': 'Unknown'
                })
                
                scientific_name = details['scientific']
                description = details['desc']
                habitat = details['habitat']
                common_in = details['common']
                
            except Exception as e:
                print(f"Prediction Error: {e}")
                prediction = None
                error_message = f"Could not identify the image. Please try another photo. (Error: {e})"
    else:
        form = ImageUploadForm()

    return render(request, 'ButterflyApp/index.html', {
        'form': form,
        'prediction': prediction,
        'image_url': image_url,
        'confidence': confidence,
        'scientific_name': scientific_name,
        'description': description,
        'habitat': habitat,
        'common_in': common_in,
        'error_message': error_message
    })

@login_required
def about(request):
    return render(request, 'ButterflyApp/about.html')
