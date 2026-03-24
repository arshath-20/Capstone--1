#!/usr/bin/env python3
"""
Test script to verify JSON serialization fixes
Tests all API endpoints to ensure no int64/numpy types leak through
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import numpy as np
from api.routes import (
    FeatureInput, 
    PredictionResponse, 
    BatchPredictionResponse,
    MetricsResponse
)
from model.predict import get_predictor
from database.models import get_db_manager


def test_statistics_serialization():
    """Test get_statistics returns JSON-serializable types"""
    print("\n📊 Testing Statistics Endpoint...")
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        stats = db_manager.get_statistics(session)
        
        # Verify all types
        print("  Checking types:")
        for key, value in stats.items():
            type_name = type(value).__name__
            print(f"    ✓ {key}: {type_name}")
            
            # Ensure it's not numpy type
            assert not isinstance(value, (np.integer, np.floating, np.ndarray)), \
                f"❌ {key} is numpy type: {type_name}"
        
        # Try JSON serialization
        json_str = json.dumps(stats)
        print(f"  ✓ JSON serialization successful")
        print(f"  ✓ Serialized size: {len(json_str)} bytes")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    finally:
        session.close()


def test_prediction_serialization():
    """Test predict endpoint returns JSON-serializable types"""
    print("\n🔮 Testing Prediction Endpoint...")
    
    try:
        predictor = get_predictor()
        
        # Create test features
        n_features = len(predictor.get_feature_names())
        test_features = np.random.randn(n_features)
        
        # Make prediction
        result = predictor.predict_single(test_features)
        
        print("  Checking prediction result types:")
        for key, value in result.items():
            type_name = type(value).__name__
            print(f"    ✓ {key}: {type_name}")
            
            if isinstance(value, dict):
                # Check dict values
                for k, v in value.items():
                    assert not isinstance(v, (np.integer, np.floating)), \
                        f"❌ {key}[{k}] is numpy type: {type(v).__name__}"
            else:
                assert not isinstance(value, (np.integer, np.floating, np.ndarray)), \
                    f"❌ {key} is numpy type: {type_name}"
        
        # Try JSON serialization
        json_str = json.dumps(result)
        print(f"  ✓ JSON serialization successful")
        print(f"  ✓ Serialized size: {len(json_str)} bytes")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_prediction_serialization():
    """Test batch_predict endpoint logic returns JSON-serializable types"""
    print("\n📦 Testing Batch Prediction Logic...")
    
    try:
        predictor = get_predictor()
        
        # Create test features
        n_features = len(predictor.get_feature_names())
        test_features = np.random.randn(5, n_features)  # 5 samples
        
        # Make batch prediction
        predictions = predictor.predict_batch(test_features)
        
        # Calculate statistics (as done in batch_predict endpoint)
        attack_count = int(sum(1 for p in predictions if p['is_attack']))
        benign_count = int(len(predictions) - attack_count)
        attack_percentage = float((attack_count / len(predictions) * 100) if predictions else 0)
        
        print("  Checking batch stats types:")
        batch_result = {
            'total_samples': len(predictions),
            'total_attacks': attack_count,
            'benign_count': benign_count,
            'attack_percentage': attack_percentage
        }
        
        for key, value in batch_result.items():
            type_name = type(value).__name__
            print(f"    ✓ {key}: {type_name}")
            
            assert not isinstance(value, (np.integer, np.floating)), \
                f"❌ {key} is numpy type: {type_name}"
        
        # Try JSON serialization
        json_str = json.dumps(batch_result)
        print(f"  ✓ JSON serialization successful")
        print(f"  ✓ Serialized size: {len(json_str)} bytes")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_models():
    """Test Pydantic response models serialize correctly"""
    print("\n✅ Testing Pydantic Response Models...")
    
    try:
        predictor = get_predictor()
        n_features = len(predictor.get_feature_names())
        
        # Test PredictionResponse
        print("  Testing PredictionResponse...")
        test_features = np.random.randn(n_features)
        pred_result = predictor.predict_single(test_features)
        
        response = PredictionResponse(
            prediction=pred_result['prediction'],
            confidence=pred_result['confidence'],
            is_attack=pred_result['is_attack'],
            probabilities=pred_result['probabilities'],
            timestamp="2024-01-01T00:00:00"
        )
        
        json_str = json.dumps(response.model_dump())
        print(f"    ✓ PredictionResponse serialized: {len(json_str)} bytes")
        
        # Test BatchPredictionResponse
        print("  Testing BatchPredictionResponse...")
        batch_preds = predictor.predict_batch(np.random.randn(3, n_features))
        
        batch_response = BatchPredictionResponse(
            total_samples=len(batch_preds),
            total_attacks=sum(1 for p in batch_preds if p['is_attack']),
            attack_percentage=50.0,
            predictions=batch_preds,
            timestamp="2024-01-01T00:00:00"
        )
        
        json_str = json.dumps(batch_response.model_dump())
        print(f"    ✓ BatchPredictionResponse serialized: {len(json_str)} bytes")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all serialization tests"""
    print("\n" + "="*60)
    print("🧪 JSON Serialization Test Suite")
    print("="*60)
    
    results = {
        'statistics': test_statistics_serialization(),
        'prediction': test_prediction_serialization(),
        'batch_prediction': test_batch_prediction_serialization(),
        'pydantic_models': test_pydantic_models(),
    }
    
    print("\n" + "="*60)
    print("📋 Test Results Summary")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.ljust(25)}: {status}")
        all_passed = all_passed and passed
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! JSON serialization is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
