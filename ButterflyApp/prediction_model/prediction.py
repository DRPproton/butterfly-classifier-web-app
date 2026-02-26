from pathlib import Path
from PIL import Image
import numpy as np
import gc

# Handle Windows vs Linux TFLite imports
try:
    import tflite_runtime.interpreter as tflite
    Interpreter = tflite.Interpreter
except ImportError:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "butterfly-model.tflite"

# Initialize Interpreter
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
    """
    Manual ResNet50 preprocessing (Caffe style).
    1. Resize to 224x224
    2. Convert to float32 numpy array
    3. RGB -> BGR
    4. Subtract Mean
    """
    # 1. Resize to target size
    img = img.resize((224, 224), Image.NEAREST)
    
    # 2. Convert to numpy array
    x = np.array(img, dtype='float32')
    
    # 3. RGB -> BGR (reverse channels)
    x = x[..., ::-1]
    
    # 4. Subtract Mean (ImageNet weights)
    # [103.939, 116.779, 123.68]
    mean = [103.939, 116.779, 123.68]
    x[..., 0] -= mean[0]
    x[..., 1] -= mean[1]
    x[..., 2] -= mean[2]
    
    # 5. Add Batch Dimension (1, 224, 224, 3)
    x = np.expand_dims(x, axis=0)
    return x

def _predict_array(X):
    interpreter.set_tensor(input_idx, X)
    interpreter.invoke()
    output = interpreter.get_tensor(output_idx)
    
    # Flatten to ensure we have a 1D array of probabilities
    preds = output.flatten()

    exp_preds = np.exp(preds - np.max(preds))
    preds = exp_preds / exp_preds.sum()
    
    # Find index of max probability
    idx = preds.argmax()
    
    # Return class name
    return classes[int(idx)], float(preds[idx])

def predict_from_memory(img_obj) -> str:
    """
    Predict butterfly species directly from a PIL Image object.
    """
    try:
        img = img_obj.convert('RGB')
        X = preprocess_image(img)
        return _predict_array(X)
    except Exception:
        raise

# --- Predict from local file ---
def predict_from_file(path: str) -> str:
    """
    Predict butterfly species from a local image file.
    Opens with PIL to ensure file is closed after reading.
    """
    img_path = Path(path)
    if not img_path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    # Open with PIL and force load to memory so we can close the file handle
    # This prevents Windows [WinError 32] file locking issues
    try:
        with Image.open(img_path) as img:
            return predict_from_memory(img)
    finally:
        # Force garbage collection to ensure file handles are released
        gc.collect()

if __name__ == "__main__":
    print("🦋 Butterfly Classifier Model")
    print(f"Model Path: {MODEL_PATH}")
    
    # Simple Health Check
    try:
        details = interpreter.get_input_details()
        print(f"✅ Model loaded successfully!")
        print(f"   Input Shape: {details[0]['shape']}")
        print(f"   Ready for Django integration.")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
    
    test_image_path = r"media/Adonis-Blue-James-Gould-2017-crop.webp"
    try:
        if Path(test_image_path).exists():
            print(f"Testing with file: {test_image_path}")
            result = predict_from_file(test_image_path)
            print(f"✅ Prediction: {result}")
        else:
            print(f"ℹ️  Test image not found (skipped local test): {test_image_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
