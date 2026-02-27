import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
    idx_to_class = {v: k for k, v in class_indices.items()}

# Load the trained model
model = load_model('plant_disease_model.h5')

def predict_plant_disease(img_path):
    """
    Predicts the class of a plant disease from an image file.
    """
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0
    preds = model.predict(x)
    pred_idx = np.argmax(preds[0])
    pred_class = idx_to_class[pred_idx]
    confidence = float(preds[0][pred_idx])
    return pred_class, confidence

# Example usage
print(predict_plant_disease(r"D:\My PC Folder\Downloads\images (1).jpg"))
print(predict_plant_disease("D:\My PC Folder\Downloads\download (2).jpg"))

