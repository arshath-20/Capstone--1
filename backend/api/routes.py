"""
FastAPI Routes
API endpoints for predictions and analysis
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import io
from datetime import datetime
from pathlib import Path
import sys

# Add backend parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from model.predict import get_predictor
from database.models import get_db_manager
from utils.preprocessing import CSVProcessor

router = APIRouter(prefix="/api", tags=["predictions"])

# Pydantic models for request/response
class FeatureInput(BaseModel):
    """Model for single prediction input"""
    features: List[float] = Field(..., description="List of feature values")

class PredictionResponse(BaseModel):
    """Model for prediction response"""
    prediction: str
    confidence: float
    is_attack: bool
    probabilities: Dict[str, float]
    timestamp: str

class BatchPredictionResponse(BaseModel):
    """Model for batch prediction response"""
    total_samples: int
    total_attacks: int
    attack_percentage: float
    predictions: List[Dict[str, Any]]
    timestamp: str

class MetricsResponse(BaseModel):
    """Model for metrics response"""
    best_model: str
    dataset: str
    features_count: int
    classes: List[str]
    test_accuracy: float

@router.post("/predict", response_model=PredictionResponse)
async def predict(data: FeatureInput):
    """
    Make a single prediction
    
    Example:
    ```
    {
        "features": [3306, 15050.607, 47, 10, 4272, ...]
    }
    ```
    """
    try:
        predictor = get_predictor()
        
        # Validate input
        if len(data.features) != len(predictor.get_feature_names()):
            raise HTTPException(
                status_code=400,
                detail=f"Expected {len(predictor.get_feature_names())} features, got {len(data.features)}"
            )
        
        # Make prediction
        features_array = np.array(data.features)
        result = predictor.predict_single(features_array)
        
        # Log prediction
        db_manager = get_db_manager()
        session = db_manager.get_session()
        try:
            log_data = {
                'features': data.features,
                'prediction': result['prediction'],
                'confidence': result['confidence'],
                'is_attack': result['is_attack'],
                'model_used': 'Random Forest',
                'probabilities': result['probabilities']
            }
            db_manager.add_prediction_log(session, log_data)
        finally:
            session.close()
        
        return PredictionResponse(
            prediction=result['prediction'],
            confidence=result['confidence'],
            is_attack=result['is_attack'],
            probabilities=result['probabilities'],
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch_predict", response_model=BatchPredictionResponse)
async def batch_predict(file: UploadFile = File(...)):
    """
    Make batch predictions from CSV file
    
    Expected CSV format: All features in order, with or without 'Label' column
    """
    try:
        # Read uploaded file
        contents = await file.read()
        df, read_report = CSVProcessor.read_csv(io.StringIO(contents.decode()))
        
        if not read_report['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read CSV: {read_report['errors']}"
            )
        
        predictor = get_predictor()
        feature_names = predictor.get_feature_names()
        
        # Remove Label column if present
        if 'Label' in df.columns:
            df = df.drop('Label', axis=1)
        
        # Prepare features
        features_array, prep_report = CSVProcessor.prepare_for_prediction(df, feature_names)
        
        if not prep_report['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to prepare data: {prep_report['warnings']}"
            )
        
        # Make predictions
        predictions = predictor.predict_batch(features_array)
        
        # Calculate statistics (convert to native Python int for JSON serialization)
        attack_count = int(sum(1 for p in predictions if p['is_attack']))
        benign_count = int(len(predictions) - attack_count)
        attack_percentage = float((attack_count / len(predictions) * 100) if predictions else 0)
        
        # Log batch analysis
        db_manager = get_db_manager()
        session = db_manager.get_session()
        try:
            batch_log = {
                'filename': file.filename,
                'total_samples': len(predictions),
                'attack_count': attack_count,
                'benign_count': benign_count,
                'results_summary': {
                    'attack_percentage': attack_percentage,
                    'benign_percentage': 100 - attack_percentage
                }
            }
            db_manager.add_batch_analysis(session, batch_log)
        finally:
            session.close()
        
        return BatchPredictionResponse(
            total_samples=int(len(predictions)),
            total_attacks=attack_count,
            attack_percentage=attack_percentage,
            predictions=predictions,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get model performance metrics"""
    try:
        predictor = get_predictor()
        model_info = predictor.get_model_info()
        
        return MetricsResponse(
            best_model=model_info['best_model'],
            dataset=model_info['dataset'],
            features_count=model_info['features_count'],
            classes=model_info['classes'],
            test_accuracy=0.95  # Would load from saved metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent prediction logs"""
    try:
        db_manager = get_db_manager()
        session = db_manager.get_session()
        try:
            logs = db_manager.get_prediction_logs(session, limit)
            return {
                'count': len(logs),
                'logs': [log.to_dict() for log in logs]
            }
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_statistics():
    """Get overall statistics"""
    try:
        db_manager = get_db_manager()
        session = db_manager.get_session()
        try:
            stats = db_manager.get_statistics(session)
            return stats
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }
