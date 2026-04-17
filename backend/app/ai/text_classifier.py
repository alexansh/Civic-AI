"""
AI Text Classification Service
Uses NLP for auto-classifying complaint text and sentiment analysis
"""

import re
from typing import Dict, List


# Keywords mapping for complaint categories
CATEGORY_KEYWORDS = {
    'pothole': [
        'pothole', 'potholes', 'road damage', 'road crack', 'crater',
        'road broken', 'street damage', 'pavement hole'
    ],
    'street_light': [
        'street light', 'streetlight', 'light pole', 'lamp post',
        'street lamp', 'public lighting', 'light not working',
        'light broken', 'street dark'
    ],
    'garbage': [
        'garbage', 'trash', 'waste', 'litter', 'dumpster',
        'sanitation', 'cleanliness', 'rubbish', 'refuse',
        'waste collection', 'overflowing'
    ],
    'water': [
        'water', 'leak', 'leakage', 'pipe burst', 'water supply',
        'sewage', 'drainage', 'flooding', 'water main',
        'no water', 'water shortage'
    ],
    'electrical': [
        'electrical', 'electric', 'wire', 'power', 'circuit',
        'outlet', 'switch', 'short circuit', 'spark',
        'electrical hazard', 'exposed wire'
    ],
    'plumbing': [
        'plumbing', 'plumber', 'pipe', 'leak', 'leakage',
        'drain', 'clog', 'toilet', 'faucet', 'water heater'
    ],
    'carpentry': [
        'carpentry', 'carpenter', 'wood', 'door', 'window',
        'furniture', 'cabinet', 'shelf', 'wooden'
    ],
    'painting': [
        'painting', 'paint', 'repaint', 'wall paint', 'graffiti removal',
        'touch up', 'coat', 'primer'
    ],
    'cleaning': [
        'cleaning', 'clean', 'sweep', 'wash', 'sanitation',
        'deep clean', 'maintenance cleaning'
    ],
    'gardening': [
        'gardening', 'garden', 'lawn', 'tree', 'plant',
        'landscaping', 'grass', 'hedge', 'park maintenance'
    ]
}

# Priority keywords
PRIORITY_KEYWORDS = {
    'critical': [
        'emergency', 'urgent', 'dangerous', 'hazard', 'danger',
        'immediate', 'critical', 'severe', 'life-threatening',
        'accident', 'injury', 'fire', 'collapse'
    ],
    'high': [
        'high priority', 'serious', 'major', 'significant',
        'affecting many', 'widespread', 'blocking', 'unsafe'
    ],
    'medium': [
        'medium', 'moderate', 'some impact', 'inconvenient',
        'needs attention', 'deteriorating'
    ],
    'low': [
        'low', 'minor', 'cosmetic', 'small', 'slight',
        'not urgent', 'when possible'
    ]
}

# Sentiment indicators
SENTIMENT_KEYWORDS = {
    'negative': [
        'terrible', 'awful', 'worst', 'horrible', 'unacceptable',
        'disgusting', 'dangerous', 'scary', 'frustrated', 'angry'
    ],
    'neutral': [
        'issue', 'problem', 'need', 'request', 'report'
    ],
    'positive': [
        'good', 'great', 'excellent', 'thanks', 'appreciate'
    ]
}


class TextClassifier:
    """Text classification service for complaint descriptions"""

    def __init__(self):
        self.category_keywords = CATEGORY_KEYWORDS
        self.priority_keywords = PRIORITY_KEYWORDS
        self.sentiment_keywords = SENTIMENT_KEYWORDS

    def classify_category(self, text: str) -> Dict:
        """
        Classify text into complaint category

        Args:
            text: Complaint description text

        Returns:
            dict with category predictions
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        scores = {}

        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Exact phrase match gets higher score
                    score += 3
                else:
                    # Individual word match
                    for word in keyword.split():
                        if word in words:
                            score += 1

            if score > 0:
                scores[category] = score

        if not scores:
            return {
                'category': 'other',
                'confidence': 0.0,
                'all_scores': {}
            }

        # Normalize scores to confidence
        max_score = max(scores.values())
        total_score = sum(scores.values())

        # Sort by score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        top_category = sorted_categories[0][0]
        confidence = max_score / total_score if total_score > 0 else 0.0

        return {
            'category': top_category,
            'confidence': min(confidence, 1.0),
            'all_scores': {k: v for k, v in sorted_categories},
            'top_3': [cat for cat, _ in sorted_categories[:3]]
        }

    def predict_priority(self, text: str, severity: int = None) -> Dict:
        """
        Predict complaint priority from text

        Args:
            text: Complaint description
            severity: Optional severity level (1-5)

        Returns:
            dict with priority prediction
        """
        text_lower = text.lower()

        scores = {}

        for priority, keywords in self.priority_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 2  # Phrase match
                else:
                    for word in keyword.split():
                        if word in text_lower.split():
                            score += 1

            if score > 0:
                scores[priority] = score

        # Adjust based on severity if provided
        if severity:
            severity_multiplier = 1 + (severity - 3) * 0.3
            for priority in scores:
                if priority in ['critical', 'high']:
                    scores[priority] *= severity_multiplier
                elif priority in ['medium', 'low']:
                    scores[priority] *= (2 - severity_multiplier)

        if not scores:
            # Default to medium if no keywords found
            return {
                'priority': 'medium',
                'confidence': 0.5,
                'all_scores': {'low': 1, 'medium': 2, 'high': 1, 'critical': 0}
            }

        # Get highest priority
        sorted_priorities = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_priority = sorted_priorities[0][0]
        total_score = sum(scores.values())
        confidence = sorted_priorities[0][1] / total_score if total_score > 0 else 0.5

        return {
            'priority': top_priority,
            'confidence': min(confidence, 1.0),
            'all_scores': scores
        }

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of complaint text

        Args:
            text: Complaint description

        Returns:
            dict with sentiment analysis
        """
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))

        scores = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }

        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[sentiment] += 2
                else:
                    for word in keyword.split():
                        if word in words:
                            scores[sentiment] += 1

        total = sum(scores.values())
        if total == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': scores
            }

        # Determine dominant sentiment
        dominant = max(scores, key=scores.get)
        confidence = scores[dominant] / total

        return {
            'sentiment': dominant,
            'confidence': min(confidence, 1.0),
            'scores': scores
        }

    def extract_entities(self, text: str) -> Dict:
        """
        Extract important entities from text

        Args:
            text: Complaint description

        Returns:
            dict with extracted entities
        """
        entities = {
            'locations': [],
            'dates': [],
            'contact_info': [],
            'severity_indicators': []
        }

        # Extract potential locations (capitalized words)
        location_patterns = [
            r'near\s+([A-Z][a-z]+)',
            r'at\s+([A-Z][a-z]+)',
            r'on\s+([A-Z][a-z]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd))',
            r'in\s+([A-Z][a-z]+)'
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            entities['locations'].extend(matches)

        # Extract dates/times
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'(today|yesterday|tomorrow|last week|next week)'
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)

        # Extract contact info
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities['contact_info'] = re.findall(phone_pattern, text)

        # Extract severity indicators
        severity_words = ['urgent', 'emergency', 'immediately', 'asap', 'critical']
        for word in severity_words:
            if word in text.lower():
                entities['severity_indicators'].append(word)

        return entities

    def full_analysis(self, text: str) -> Dict:
        """
        Perform full text analysis

        Args:
            text: Complaint description

        Returns:
            dict with complete analysis
        """
        category = self.classify_category(text)
        priority = self.predict_priority(text)
        sentiment = self.analyze_sentiment(text)
        entities = self.extract_entities(text)

        return {
            'category': category,
            'priority': priority,
            'sentiment': sentiment,
            'entities': entities,
            'text_length': len(text),
            'word_count': len(text.split())
        }


# Singleton instance
text_classifier = TextClassifier()


def classify_complaint_text(text: str) -> Dict:
    """
    Convenience function to classify complaint text

    Args:
        text: Complaint description

    Returns:
        dict with classification results
    """
    return text_classifier.classify_category(text)


def predict_complaint_priority(text: str, severity: int = None) -> Dict:
    """
    Convenience function to predict complaint priority

    Args:
        text: Complaint description
        severity: Optional severity level

    Returns:
        dict with priority prediction
    """
    return text_classifier.predict_priority(text, severity)


def analyze_complaint_sentiment(text: str) -> Dict:
    """
    Convenience function to analyze complaint sentiment

    Args:
        text: Complaint description

    Returns:
        dict with sentiment analysis
    """
    return text_classifier.analyze_sentiment(text)
