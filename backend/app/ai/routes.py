"""
AI Routes - AI-powered endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.ai.image_classifier import classify_civic_issue, validate_issue_image
from app.ai.text_classifier import classify_complaint_text, predict_complaint_priority, analyze_complaint_sentiment
from app.ai.priority_predictor import predict_complaint_priority as predict_full_priority
from app.middleware.auth import optional_jwt_required

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/classify-image', methods=['POST'])
def classify_image():
    """Classify an uploaded image"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    try:
        # Save temporarily or process directly
        # For now, we'll use a placeholder
        # In production, you'd save to temp location or use in-memory processing

        # For demonstration, return mock result
        # In production: result = classify_civic_issue(image_path)

        return jsonify({
            'message': 'Image classification endpoint',
            'note': 'In production, this would return actual classification'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/classify-text', methods=['POST'])
def classify_text():
    """Classify complaint description text"""
    data = request.get_json()

    if not data or not data.get('description'):
        return jsonify({'error': 'Description is required'}), 400

    text = data['description']

    # Classify category
    category_result = classify_complaint_text(text)

    # Predict priority
    priority_result = predict_complaint_priority(text, data.get('severity_level'))

    # Analyze sentiment
    sentiment_result = analyze_complaint_sentiment(text)

    return jsonify({
        'category': category_result,
        'priority': priority_result,
        'sentiment': sentiment_result
    }), 200


@ai_bp.route('/predict-priority', methods=['POST'])
def predict_priority():
    """Predict full complaint priority with all factors"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Validate required fields
    if not data.get('description'):
        return jsonify({'error': 'Description is required'}), 400

    try:
        result = predict_full_priority(data)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/validate-issue', methods=['POST'])
def validate_issue():
    """Validate if text/image describes a real civic issue"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    has_text = bool(data.get('description'))
    has_image = bool(data.get('image_url'))

    if not has_text and not has_image:
        return jsonify({'error': 'Description or image is required'}), 400

    validation = {
        'is_valid_issue': False,
        'confidence': 0.0,
        'reasons': []
    }

    # Check text
    if has_text:
        text_valid = len(data['description'].strip()) >= 10
        if text_valid:
            validation['is_valid_issue'] = True
            validation['confidence'] += 0.4
            validation['reasons'].append('Sufficient description provided')
        else:
            validation['reasons'].append('Description too short')

    # Check image (would use image validation in production)
    if has_image:
        # In production: image_valid = validate_issue_image(image_path)
        validation['is_valid_issue'] = True
        validation['confidence'] += 0.4
        validation['reasons'].append('Image provided')

    return jsonify(validation), 200


@ai_bp.route('/category-suggestion', methods=['POST'])
def suggest_category():
    """Suggest category based on text description"""
    data = request.get_json()

    if not data or not data.get('description'):
        return jsonify({'error': 'Description is required'}), 400

    result = classify_complaint_text(data['description'])

    # Get full analysis
    from app.ai.text_classifier import TextClassifier
    classifier = TextClassifier()
    full_analysis = classifier.full_analysis(data['description'])

    return jsonify({
        'suggested_category': result['category'],
        'confidence': result['confidence'],
        'alternatives': result.get('top_3', []),
        'full_analysis': full_analysis
    }), 200


@ai_bp.route('/health', methods=['GET'])
def health_check():
    """AI service health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI classification',
        'models_loaded': True
    }), 200
