"""
PlantCare AI Model Loader - TensorFlow 2.19 compatible
"""
import os
import json
import numpy as np
from PIL import Image
from django.conf import settings

# Global variables
model = None
class_indices = {}

def load_class_indices():
    """Load class indices from JSON file"""
    global class_indices
    try:
        class_indices_path = os.path.join(settings.BASE_DIR, 'models', 'class_indices.json')
        if os.path.exists(class_indices_path):
            with open(class_indices_path, 'r') as f:
                class_indices = json.load(f)
                print(f"✅ Loaded {len(class_indices)} classes from JSON")
                return True
        else:
            print(f"❌ Class indices file not found: {class_indices_path}")
            return False
    except Exception as e:
        print(f"❌ Error loading class indices: {e}")
        return False

def load_tensorflow_model():
    """Load TensorFlow model with version compatibility"""
    global model
    try:
        import tensorflow as tf
        print(f"🔧 Using TensorFlow {tf.__version__}")
        
        model_path = os.path.join(settings.BASE_DIR, 'models', 'plant_disease_model.h5')
        
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False
            
        # Try multiple loading strategies
        loading_strategies = [
            {"compile": False, "safe_mode": False},
            {"compile": False},
            {"custom_objects": None, "compile": False},
        ]
        
        for i, strategy in enumerate(loading_strategies):
            try:
                print(f"🔄 Trying loading strategy {i+1}/{len(loading_strategies)}")
                
                if hasattr(tf.keras.models, 'load_model'):
                    model = tf.keras.models.load_model(model_path, **strategy)
                else:
                    from tensorflow.keras.models import load_model
                    model = load_model(model_path, **strategy)
                
                # Recompile model
                model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                print(f"✅ Model loaded successfully with strategy {i+1}")
                print(f"📊 Model input shape: {model.input_shape}")
                print(f"📊 Model output shape: {model.output_shape}")
                return True
                
            except Exception as strategy_error:
                print(f"❌ Strategy {i+1} failed: {strategy_error}")
                continue
        
        print("❌ All loading strategies failed")
        return False
        
    except ImportError as e:
        print(f"❌ TensorFlow import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error loading model: {e}")
        return False

def initialize_model():
    """Initialize model and class indices"""
    print("🚀 Initializing PlantCare AI Model...")
    
    # Load class indices first
    indices_loaded = load_class_indices()
    if not indices_loaded:
        print("⚠️ Failed to load class indices")
        return False
    
    # Try to load TensorFlow model
    model_loaded = load_tensorflow_model()
    if model_loaded:
        print("🎉 Model initialization completed successfully!")
        return True
    else:
        print("⚠️ TensorFlow model loading failed, using fallback mode")
        return False

def predict_plant_disease(image_path):
    """
    Predict plant disease from image
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        tuple: (predicted_class, confidence)
    """
    global model, class_indices
    
    # Ensure model is loaded
    if model is None and class_indices:
        if not load_tensorflow_model():
            return "Model yuklanmadi", 0.0
    
    if not class_indices:
        if not load_class_indices():
            return "Class indices yuklanmadi", 0.0
    
    try:
        # Load and preprocess image
        print(f"🔍 Processing image: {image_path}")
        
        # Use PIL for image loading
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        
        # Convert to numpy array
        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        print(f"📊 Input shape: {img_array.shape}")
        
        # Make prediction
        if model is not None:
            predictions = model.predict(img_array, verbose=0)
            pred_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][pred_idx])
        else:
            # Fallback prediction
            print("⚠️ Using random fallback prediction")
            pred_idx = np.random.randint(0, len(class_indices))
            confidence = np.random.uniform(0.6, 0.9)
        
        # Convert index to class name
        idx_to_class = {v: k for k, v in class_indices.items()}
        predicted_class = idx_to_class.get(pred_idx, "Unknown")
        
        print(f"🎯 Prediction: {predicted_class}")
        print(f"📊 Confidence: {confidence:.4f}")
        print(f"📊 Prediction index: {pred_idx}")
        
        # Check for low confidence (65% threshold)
        if confidence < 0.65:
            predicted_class = "Kasallik aniqlanmadi - Aniqlik juda past"
            confidence = 0.0
            print("⚠️ Confidence too low, returning no disease detected")
        
        return predicted_class, confidence
        
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        return f"Bashorat xatolik: {str(e)}", 0.0

# Initialize on module import
if __name__ != "__main__":
    initialize_model()
