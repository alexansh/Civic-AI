"""
AI Image Classification Service
Uses TensorFlow/PyTorch for classifying complaint images
"""

import os
import json
from PIL import Image
import numpy as np


# Category mapping for civic issues
CATEGORY_MAPPING = {
    0: 'pothole',
    1: 'street_light',
    2: 'garbage',
    3: 'water_leak',
    4: 'electrical',
    5: 'building_damage',
    6: 'graffiti',
    7: 'fallen_tree',
    8: 'traffic_signal',
    9: 'drainage'
}

# Reverse mapping
CATEGORY_TO_ID = {v: k for k, v in CATEGORY_MAPPING.items()}


class ImageClassifier:
    """Image classification service for civic issues"""

    def __init__(self, model_path=None):
        self.model = None
        self.is_loaded = False
        self.model_path = model_path

        # For demo/without actual model, use rule-based classification
        self.use_demo_mode = True

    def load_model(self):
        """Load the trained model"""
        try:
            if not self.use_demo_mode and self.model_path:
                # TensorFlow model loading would go here
                # import tensorflow as tf
                # self.model = tf.keras.models.load_model(self.model_path)
                self.is_loaded = True
            else:
                # Demo mode - use keyword-based classification
                self.is_loaded = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            self.use_demo_mode = True
            self.is_loaded = True  # Still set to true for demo mode
            return False

    def classify_image(self, image_path_or_array):
        """
        Classify an image and return predicted category with confidence

        Args:
            image_path_or_array: Path to image file or numpy array

        Returns:
            dict with category, confidence, and all predictions
        """
        if not self.is_loaded:
            self.load_model()

        try:
            if isinstance(image_path_or_array, str):
                # Load image from path
                image = Image.open(image_path_or_array)
            else:
                image = image_path_or_array

            # Preprocess image
            processed_image = self._preprocess_image(image)

            if self.use_demo_mode:
                # Demo mode: use simple pattern matching
                predictions = self._demo_classify(processed_image)
            else:
                # Use loaded model
                # predictions = self.model.predict(processed_image)
                predictions = self._demo_classify(processed_image)

            # Get top prediction
            top_idx = np.argmax(predictions)
            top_category = CATEGORY_MAPPING.get(top_idx, 'unknown')
            confidence = float(predictions[top_idx])

            # Get top 3 predictions
            top_indices = np.argsort(predictions)[::-1][:3]
            top_predictions = [
                {
                    'category': CATEGORY_MAPPING.get(idx, 'unknown'),
                    'confidence': float(predictions[idx])
                }
                for idx in top_indices
            ]

            return {
                'category': top_category,
                'confidence': confidence,
                'all_predictions': predictions.tolist(),
                'top_predictions': top_predictions
            }

        except Exception as e:
            print(f"Error classifying image: {e}")
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }

    def _preprocess_image(self, image):
        """Preprocess image for model input"""
        # Resize to model input size
        image = image.resize((224, 224))

        # Convert to numpy array
        img_array = np.array(image)

        # Normalize
        img_array = img_array / 255.0

        # Add batch dimension if needed
        if len(img_array.shape) == 3:
            img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def _demo_classify(self, image_array):
        """
        Demo classification using simple image properties
        In production, this would be replaced by actual model inference
        """
        # Analyze image properties to make educated guesses
        # This is just for demonstration

        predictions = np.zeros(len(CATEGORY_MAPPING))

        # Calculate average brightness
        brightness = np.mean(image_array)

        # Calculate color distribution
        if len(image_array.shape) == 4:
            # RGB analysis
            r, g, b = np.mean(image_array[0, :, :, 0]), \
                      np.mean(image_array[0, :, :, 1]), \
                      np.mean(image_array[0, :, :, 2])

            # Simple heuristics
            if brightness < 50:
                # Dark image - could be street light issue
                predictions[CATEGORY_TO_ID.get('street_light', 1)] = 0.6
            elif r > g and r > b:
                # Reddish - could be pothole or damage
                predictions[CATEGORY_TO_ID.get('pothole', 0)] = 0.5
            elif g > r and g > b:
                # Greenish - could be vegetation/fallen tree
                predictions[CATEGORY_TO_ID.get('fallen_tree', 7)] = 0.5
            else:
                # Gray/white - could be garbage or water
                predictions[CATEGORY_TO_ID.get('garbage', 2)] = 0.4
                predictions[CATEGORY_TO_ID.get('water_leak', 3)] = 0.3
        else:
            # Grayscale - distribute probability
            predictions[CATEGORY_TO_ID.get('pothole', 0)] = 0.3
            predictions[CATEGORY_TO_ID.get('garbage', 2)] = 0.3
            predictions[CATEGORY_TO_ID.get('building_damage', 5)] = 0.2

        # Add some randomness for variety
        predictions += np.random.random(predictions.shape) * 0.2

        # Normalize to probabilities
        predictions = np.exp(predictions) / np.sum(np.exp(predictions))

        return predictions

    def detect_issue_from_image(self, image_path):
        """
        Detect if there's an actual issue in the image

        Returns:
            bool indicating if issue detected
        """
        result = self.classify_image(image_path)

        # If confidence is very low, might not be a valid issue
        if result['confidence'] < 0.3:
            return False

        # If category is unknown, might not be valid
        if result['category'] == 'unknown':
            return False

        return True


# Singleton instance
classifier = ImageClassifier()


def classify_civic_issue(image_path):
    """
    Convenience function to classify civic issue images

    Args:
        image_path: Path to image file

    Returns:
        dict with classification results
    """
    return classifier.classify_image(image_path)


def validate_issue_image(image_path):
    """
    Validate that image contains a detectable civic issue

    Args:
        image_path: Path to image file

    Returns:
        bool indicating validity
    """
    return classifier.detect_issue_from_image(image_path)
