from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions
from .models import Disease, PlantImage, Recommendation
from .serializers import DiseaseSerializer, PlantImageSerializer, RecommendationSerializer
from .forms import PlantImageForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import numpy as np
from PIL import Image
import json
import os
from django.conf import settings
import sys

# Add models directory to path
models_path = os.path.join(settings.BASE_DIR, 'models')
if models_path not in sys.path:
    sys.path.insert(0, models_path)

# Try to import AI utils, fallback to simple version
try:
    from .ai_utils import get_ai_recommendation
except ImportError:
    from .ai_utils_simple import get_ai_recommendation

# Import the new model manager
try:
    from models.model_manager import model_manager, predict_with_manager
    MODEL_MANAGER_AVAILABLE = True
    print("✅ Model manager imported successfully")
except ImportError as e:
    MODEL_MANAGER_AVAILABLE = False
    print(f"❌ Model manager import failed: {e}")

# Import the new model loader
try:
    from .model_loader import predict_plant_disease
    MODEL_LOADER_AVAILABLE = True
    print("✅ Model loader imported successfully - ready for TensorFlow 2.19")
except ImportError as e:
    MODEL_LOADER_AVAILABLE = False
    print(f"❌ Model loader import failed: {e}")

# Legacy model loading code (kept as fallback)
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging

# Initialize model and class indices
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'plant_disease_model.h5')
CLASS_INDICES_PATH = os.path.join(settings.BASE_DIR, 'models', 'class_indices.json')

model = None
class_indices = {}

def load_model_and_indices():
    """Load TensorFlow model and class indices"""
    global model, class_indices
    print("🚀 Starting model and indices loading...")
    try:
        # Import TensorFlow 2.19
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        print(f"✅ TensorFlow {tf.__version__} imported successfully")
        
        # Load class indices first
        if os.path.exists(CLASS_INDICES_PATH):
            with open(CLASS_INDICES_PATH, 'r') as f:
                class_indices = json.load(f)
                print(f"✅ Loaded {len(class_indices)} classes from JSON")
        else:
            print(f"❌ Class indices file not found: {CLASS_INDICES_PATH}")
            return False
            
        # Load model with TensorFlow 2.19 compatibility
        if os.path.exists(MODEL_PATH):
            print(f"Loading model from: {MODEL_PATH}")
            try:
                # Load model with safe mode disabled for compatibility
                model = load_model(MODEL_PATH, compile=False, safe_mode=False)
                
                # Compile the model for TensorFlow 2.19
                model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                print(f"✅ Model loaded successfully with TensorFlow {tf.__version__}")
                print(f"📊 Model input shape: {model.input_shape}")
                print(f"📊 Model output shape: {model.output_shape}")
                return True
                
            except Exception as model_error:
                print(f"❌ Failed to load model: {model_error}")
                print("🔄 Trying alternative loading method...")
                
                try:
                    # Alternative method - load without safe_mode restrictions
                    import tensorflow.keras.utils as utils
                    model = tf.keras.models.load_model(
                        MODEL_PATH, 
                        custom_objects=None,
                        compile=False
                    )
                    model.compile(
                        optimizer='adam',
                        loss='sparse_categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    print(f"✅ Model loaded with alternative method")
                    return True
                except Exception as alt_error:
                    print(f"❌ Alternative loading also failed: {alt_error}")
                    return False
        else:
            print(f"❌ Model file not found: {MODEL_PATH}")
            return False
            
    except ImportError as e:
        print(f"❌ TensorFlow import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading model and indices: {e}")
        return False

# Load model on startup - TensorFlow 2.19 compatible
print("🚀 Initializing PlantCare AI Model with TensorFlow 2.19...")
load_success = load_model_and_indices()
if load_success:
    print("🎉 TensorFlow 2.19 Model initialization completed successfully!")
else:
    print("⚠️ Model initialization failed. Using fallback mode.")

def predict_image(image_path, detection_type='disease', plant_type='all'):
    """Predict plant disease from image using model manager or fallback methods"""
    
    # First try the new model manager if available
    if MODEL_MANAGER_AVAILABLE:
        try:
            predicted_class, confidence = predict_with_manager(
                image_path,
                detection_type=detection_type,
                plant_type=plant_type
            )
            print(f"🎯 Model Manager Prediction: {predicted_class} with confidence: {confidence:.4f}")
            return predicted_class, confidence
        except Exception as manager_error:
            print(f"❌ Model manager failed: {manager_error}")
            # Fall through to other methods
    
    # Use the new model loader if available
    if MODEL_LOADER_AVAILABLE:
        try:
            predicted_class, confidence = predict_plant_disease(image_path)
            print(f"🎯 New Model Loader Prediction: {predicted_class} with confidence: {confidence:.4f}")
            return predicted_class, confidence
        except Exception as loader_error:
            print(f"❌ New model loader failed: {loader_error}")
            # Fall through to legacy methods
    
    # Legacy fallback methods
    global model, class_indices
    
    # Try to load model if not already loaded
    if model is None:
        if not load_model_and_indices():
            # Fallback to using models/predic.py directly
            try:
                import sys
                import os
                models_path = os.path.join(settings.BASE_DIR, 'models')
                sys.path.append(models_path)
                
                # Change to models directory for relative paths
                original_cwd = os.getcwd()
                os.chdir(models_path)
                
                # Import the prediction function
                from predic import predict_plant_disease as legacy_predict
                
                # Make prediction
                predicted_class, confidence = legacy_predict(image_path)
                
                # Restore original directory
                os.chdir(original_cwd)
                
                print(f"🎯 Legacy fallback prediction: {predicted_class} with confidence: {confidence:.4f}")
                return predicted_class, confidence
                
            except Exception as fallback_error:
                print(f"❌ Legacy fallback prediction failed: {fallback_error}")
                return "Model yuklanmadi", 0.0
    
    if not class_indices:
        return "Class indices yuklanmadi", 0.0
    
    try:
        # Import required libraries for TensorFlow 2.19
        import tensorflow as tf
        from PIL import Image
        import numpy as np
        
        print(f"🔍 Processing image: {image_path}")
        
        # Load and preprocess image for TensorFlow 2.19
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        
        # Convert to numpy array and normalize
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        print(f"📊 Input shape: {img_array.shape}")
        
        # Make prediction using TensorFlow 2.19
        predictions = model.predict(img_array, verbose=0)
        pred_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][pred_idx])
        
        # Convert index to class name
        idx_to_class = {v: k for k, v in class_indices.items()}
        predicted_class = idx_to_class.get(pred_idx, "Unknown")
        
        print(f"🎯 TensorFlow 2.19 Prediction: {predicted_class} with confidence: {confidence:.4f}")
        print(f"📊 Prediction index: {pred_idx}")
        
        return predicted_class, confidence
        
    except Exception as e:
        print(f"❌ Error in TensorFlow 2.19 prediction: {e}")
        import traceback
        traceback.print_exc()
        return f"Bashorat xatolik: {str(e)}", 0.0

# Create your views here.

class DiseaseViewSet(viewsets.ModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [permissions.AllowAny]

class PlantImageViewSet(viewsets.ModelViewSet):
    queryset = PlantImage.objects.all()
    serializer_class = PlantImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.AllowAny]

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import PlantImageForm  # Assuming this is your form
from .models import Disease  # Assuming this is your model
from .ai_utils import get_ai_recommendation  # Assuming these are your utility functions

@login_required
@csrf_exempt
def test_image(request):
    if request.method == 'POST':
        form = PlantImageForm(request.POST, request.FILES)
        if form.is_valid():
            plant_image = form.save(commit=False)
            plant_image.user = request.user
            plant_image.status = 'processing'
            plant_image.save()

            try:
                # Get detection and plant types from form
                detection_type = request.POST.get('detection_type', 'disease')
                plant_type = request.POST.get('plant_type', 'all')
                
                print(f"🔍 Detection Type: {detection_type}, Plant Type: {plant_type}")
                
                # Use model manager with parameters
                label, confidence = predict_image(
                    plant_image.image.path,
                    detection_type=detection_type,
                    plant_type=plant_type
                )
                
                disease, _ = Disease.objects.get_or_create(
                    name=label,
                    defaults={
                        'description': f'{label} kasalligi aniqlandi',
                        'symptoms': 'Belgilar aniqlanmoqda...',
                        'treatment': 'Davolash usullari tayyorlanmoqda...'
                    }
                )

                current_lang = request.session.get('django_language', 'uz')
                ai_tavsiya = get_ai_recommendation(label, lang=current_lang)

                plant_image.disease = disease
                plant_image.disease_name = label
                plant_image.confidence = confidence
                plant_image.accuracy = confidence * 100
                plant_image.ai_result = ai_tavsiya
                plant_image.status = 'completed'
                plant_image.save()

                return JsonResponse({
                    'success': True,
                    'disease': label,
                    'confidence': round(confidence * 100, 2),
                    'description': disease.description,
                    'recommendations': ai_tavsiya,
                    'image_url': plant_image.image.url,
                })
            except Exception as e:
                plant_image.status = 'failed'
                plant_image.ai_result = f"Xatolik yuz berdi: {str(e)}"
                plant_image.save()
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': _('Formada xatolik bor')}, status=400)
    else:
        # Handle GET requests by rendering the template with plant types
        from .models import PlantType
        
        # Barcha faol o'simlik turlarini olish
        plant_types = PlantType.objects.filter(is_active=True).order_by('name_uz')
        
        # Turlar bo'yicha guruhlash (kelajakda detection_type bo'yicha filterlash mumkin)
        context = {
            'plant_types': plant_types,
        }
        
        return render(request, 'diagnosis/test_image.html', context)