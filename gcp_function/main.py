import functions_framework
import os
from pathlib import Path
from PIL import Image
import numpy as np
import io
import json

# Handle Windows vs Linux TFLite imports (Functions use Linux usually, but this is safe)
try:
    import tflite_runtime.interpreter as tflite
    Interpreter = tflite.Interpreter
except ImportError:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter

# Import the butterfly details dictionary 
try:
    from butterfly_details import BUTTERFLY_DETAILS
except ImportError:
    BUTTERFLY_DETAILS = {}

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "butterfly-model.tflite"

# Initialize Interpreter during cold start
interpreter = Interpreter(model_path=str(MODEL_PATH))
interpreter.allocate_tensors()

input_idx = interpreter.get_input_details()[0]['index']
output_idx = interpreter.get_output_details()[0]['index']

classes = [
    'ADONIS', 'AFRICAN GIANT SWALLOWTAIL', 'AMERICAN SNOOT', 'AN 88', 'APPOLLO',
    'ATALA', 'BANDED ORANGE HELICONIAN', 'BANDED PEACOCK', 'BECKERS WHITE',
    'BLACK HAIRSTREAK', 'BLUE MORPHO', 'BLUE SPOTTED CROW', 'BROWN SIPROETA',
    'CABBAGE WHITE', 'CAIRNS BIRDWING', 'CHECQUERED SKIPPER', 'CHESTNUT',
    'CLEOPATRA', 'CLODIUS PARNASSIAN', 'CLOUDED SULPHUR', 'COMMON BANDED AWL',
    'COMMON WOOD-NYMPH', 'COPPER TAIL', 'CRECENT', 'CRIMSON PATCH',
    'DANAID EGGFLY', 'EASTERN COMA', 'EASTERN DAPPLE WHITE', 'EASTERN PINE ELFIN',
    'ELBOWED PIERROT', 'GOLD BANDED', 'GREAT EGGFLY', 'GREAT JAY',
    'GREEN CELLED CATTLEHEART', 'GREY HAIRSTREAK', 'INDRA SWALLOW',
    'IPHICLUS SISTER', 'JULIA', 'LARGE MARBLE', 'MALACHITE', 'MANGROVE SKIPPER',
    'MESTRA', 'METALMARK', 'MILBERTS TORTOISESHELL', 'MONARCH', 'MOURNING CLOAK',
    'ORANGE OAKLEAF', 'ORANGE TIP', 'ORCHARD SWALLOW', 'PAINTED LADY',
    'PAPER KITE', 'PEACOCK', 'PINE WHITE', 'PIPEVINE SWALLOW', 'POPINJAY',
    'PURPLE HAIRSTREAK', 'PURPLISH COPPER', 'QUESTION MARK', 'RED ADMIRAL',
    'RED CRACKER', 'RED POSTMAN', 'RED SPOTTED PURPLE', 'SCARCE SWALLOW',
    'SILVER SPOT SKIPPER', 'SLEEPY ORANGE', 'SOOTYWING', 'SOUTHERN DOGFACE',
    'STRAITED QUEEN', 'TROPICAL LEAFWING', 'TWO BARRED FLASHER', 'ULYSES',
    'VICEROY', 'WOOD SATYR', 'YELLOW SWALLOW TAIL', 'ZEBRA LONG WING'
]

def preprocess_image(img):
    # Resize to target size
    img = img.resize((224, 224), Image.NEAREST)
    # Convert to numpy array
    x = np.array(img, dtype='float32')
    # RGB -> BGR (reverse channels)
    x = x[..., ::-1]
    # Subtract Mean (ImageNet weights)
    mean = [103.939, 116.779, 123.68]
    x[..., 0] -= mean[0]
    x[..., 1] -= mean[1]
    x[..., 2] -= mean[2]
    # Add Batch Dimension (1, 224, 224, 3)
    x = np.expand_dims(x, axis=0)
    return x

def predict_from_memory(img_obj) -> str:
    img = img_obj.convert('RGB')
    X = preprocess_image(img)
    
    interpreter.set_tensor(input_idx, X)
    interpreter.invoke()
    output = interpreter.get_tensor(output_idx)
    
    preds = output.flatten()
    exp_preds = np.exp(preds - np.max(preds))
    preds = exp_preds / exp_preds.sum()
    
    idx = preds.argmax()
    return classes[int(idx)], float(preds[idx])


@functions_framework.http
def predict(request):
    """HTTP Cloud Function to classify butterfly image."""
    
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        if 'image' not in request.files:
            return (json.dumps({'error': 'No image provided'}), 400, headers)
        
        file = request.files.get('image')
        image_bytes = file.read()
        
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Predict
        predicted_class, confidence_val = predict_from_memory(img)
        
        # Get metadata
        details = BUTTERFLY_DETAILS.get(predicted_class, {})
        
        response_data = {
            'prediction': predicted_class.title(),
            'confidence': f"{confidence_val * 100:.1f}%",
            'scientific_name': details.get('scientific', 'Unknown'),
            'description': details.get('desc', 'No description available.'),
            'habitat': details.get('habitat', 'Unknown'),
            'common_in': details.get('common', 'Unknown')
        }
        
        return (json.dumps(response_data), 200, headers)
        
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, headers)
