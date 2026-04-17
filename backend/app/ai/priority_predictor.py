"""
Priority Prediction Service
Combines multiple factors to predict complaint priority
"""

from app.ai.text_classifier import TextClassifier
from app.ai.image_classifier import ImageClassifier
from datetime import datetime
import math


class PriorityPredictor:
    """Advanced priority prediction combining multiple signals"""

    def __init__(self):
        self.text_classifier = TextClassifier()
        self.image_classifier = ImageClassifier()

        # Weights for different factors
        self.weights = {
            'text_analysis': 0.35,
            'image_analysis': 0.25,
            'severity': 0.20,
            'affected_count': 0.10,
            'time_factor': 0.05,
            'location_factor': 0.05
        }

    def predict_priority(self, complaint_data: dict) -> dict:
        """
        Predict priority for a complaint

        Args:
            complaint_data: dict with complaint fields including:
                - description: text description
                - category: complaint category
                - severity_level: 1-5
                - affected_people_count: number of people affected
                - images: list of image paths (optional)
                - location: location data (optional)
                - created_at: when complaint was created

        Returns:
            dict with priority prediction and breakdown
        """
        scores = {}
        details = {}

        # 1. Text Analysis
        text_score, text_details = self._analyze_text(
            complaint_data.get('description', ''),
            complaint_data.get('category', '')
        )
        scores['text'] = text_score
        details['text_analysis'] = text_details

        # 2. Image Analysis (if available)
        images = complaint_data.get('images', [])
        if images:
            img_score, img_details = self._analyze_images(images)
            scores['image'] = img_score
            details['image_analysis'] = img_details
        else:
            scores['image'] = 0.5
            details['image_analysis'] = {'message': 'No images provided'}

        # 3. Severity Level
        severity = complaint_data.get('severity_level', 3)
        severity_score = severity / 5.0
        scores['severity'] = severity_score
        details['severity'] = {
            'level': severity,
            'score': severity_score
        }

        # 4. Affected People Count
        affected_count = complaint_data.get('affected_people_count', 1)
        affected_score = self._calculate_affected_score(affected_count)
        scores['affected'] = affected_score
        details['affected_people'] = {
            'count': affected_count,
            'score': affected_score
        }

        # 5. Time Factor (older complaints get priority boost)
        created_at = complaint_data.get('created_at')
        if created_at:
            time_score = self._calculate_time_score(created_at)
            scores['time'] = time_score
            details['time_factor'] = {
                'days_old': (datetime.utcnow() - created_at).days if isinstance(created_at, datetime) else 0,
                'score': time_score
            }
        else:
            scores['time'] = 0.5

        # 6. Location Factor (urban areas might get higher priority)
        location = complaint_data.get('location', {})
        if location:
            location_score = self._calculate_location_score(location)
            scores['location'] = location_score
            details['location_factor'] = {
                'score': location_score
            }
        else:
            scores['location'] = 0.5

        # Calculate weighted final score
        final_score = 0
        for factor, weight in self.weights.items():
            final_score += scores.get(factor, 0.5) * weight

        # Determine priority level
        priority = self._score_to_priority(final_score)

        return {
            'priority': priority,
            'score': round(final_score * 100, 2),  # Convert to 0-100 scale
            'breakdown': {
                'individual_scores': {k: round(v, 3) for k, v in scores.items()},
                'weights': self.weights,
                'details': details
            }
        }

    def _analyze_text(self, text: str, category: str) -> tuple:
        """Analyze text for priority signals"""
        if not text:
            return 0.5, {'message': 'No text provided'}

        analysis = self.text_classifier.full_analysis(text)

        # Priority from text
        text_priority = analysis['priority']['priority']
        confidence = analysis['priority']['confidence']

        # Convert priority label to score
        priority_scores = {
            'critical': 1.0,
            'high': 0.75,
            'medium': 0.5,
            'low': 0.25
        }

        base_score = priority_scores.get(text_priority, 0.5)
        final_score = base_score * confidence

        return final_score, {
            'predicted_priority': text_priority,
            'confidence': confidence,
            'sentiment': analysis['sentiment']['sentiment']
        }

    def _analyze_images(self, images: list) -> tuple:
        """Analyze images for priority signals"""
        if not images:
            return 0.5, {'message': 'No images to analyze'}

        # For now, just analyze first image
        # In production, would analyze all and aggregate
        try:
            result = self.image_classifier.classify_image(images[0])

            # Higher confidence = more urgent
            confidence = result.get('confidence', 0.5)

            # Certain categories are higher priority
            high_priority_categories = [
                'electrical', 'building_damage', 'water_leak'
            ]
            category = result.get('category', '')
            category_multiplier = 1.3 if category in high_priority_categories else 1.0

            score = min(confidence * category_multiplier, 1.0)

            return score, {
                'detected_category': category,
                'confidence': confidence,
                'multiplier': category_multiplier
            }
        except Exception as e:
            return 0.5, {'error': str(e)}

    def _calculate_affected_score(self, count: int) -> float:
        """Calculate score based on number of people affected"""
        if count <= 1:
            return 0.3
        elif count <= 10:
            return 0.5
        elif count <= 50:
            return 0.7
        elif count <= 100:
            return 0.85
        else:
            return 1.0

    def _calculate_time_score(self, created_at: datetime) -> float:
        """Calculate time-based priority boost"""
        if not isinstance(created_at, datetime):
            return 0.5

        days_old = (datetime.utcnow() - created_at).days

        # Older complaints get priority boost
        if days_old > 14:
            return 1.0
        elif days_old > 7:
            return 0.8
        elif days_old > 3:
            return 0.65
        elif days_old > 1:
            return 0.5
        else:
            return 0.4

    def _calculate_location_score(self, location: dict) -> float:
        """Calculate location-based priority"""
        # In production, would check if location is:
        # - Urban vs rural
        # - High traffic area
        # - Near schools/hospitals
        # For now, return neutral
        return 0.5

    def _score_to_priority(self, score: float) -> str:
        """Convert numeric score to priority label"""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'


# Singleton instance
priority_predictor = PriorityPredictor()


def predict_complaint_priority(complaint_data: dict) -> dict:
    """
    Convenience function to predict complaint priority

    Args:
        complaint_data: dict with complaint information

    Returns:
        dict with priority prediction
    """
    return priority_predictor.predict_priority(complaint_data)
