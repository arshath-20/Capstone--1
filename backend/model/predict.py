"""
Model Prediction Module
Loads trained models and makes predictions on new data
"""

import joblib
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

class ModelPredictor:
    def __init__(self, model_dir: str = None):
        """Initialize the predictor and load saved models"""
        if model_dir is None:
            model_dir = Path(__file__).parent
        else:
            model_dir = Path(model_dir)
        
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.model_info = None
        self.all_models = None
        
        self._load_models()
    
    def _load_models(self):
        """Load all saved models and preprocessing objects"""
        try:
            # Load best model
            self.model = joblib.load(self.model_dir / 'saved_model.pkl')
            print("✓ Loaded best model")
            
            # Load scaler
            self.scaler = joblib.load(self.model_dir / 'scaler.pkl')
            print("✓ Loaded scaler")
            
            # Load label encoder
            self.label_encoder = joblib.load(self.model_dir / 'label_encoder.pkl')
            print("✓ Loaded label encoder")
            
            # Load feature names
            with open(self.model_dir / 'feature_names.pkl', 'rb') as f:
                self.feature_names = pickle.load(f)
            print(f"✓ Loaded {len(self.feature_names)} feature names")
            
            # Load model info
            with open(self.model_dir / 'model_info.json', 'r') as f:
                self.model_info = json.load(f)
            print(f"✓ Loaded model info (Best: {self.model_info['best_model']})")
            
            # Load all models
            with open(self.model_dir / 'all_models.pkl', 'rb') as f:
                self.all_models = pickle.load(f)
            print(f"✓ Loaded {len(self.all_models)} models")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Model files not found: {e}")
    
    def predict_single(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Make prediction on a single sample
        
        Args:
            features: numpy array of features
        
        Returns:
            Dictionary with prediction and confidence
        """
        if features.shape[0] != len(self.feature_names):
            raise ValueError(
                f"Feature count mismatch. Expected {len(self.feature_names)}, "
                f"got {features.shape[0]}"
            )
        
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get prediction and probability
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        # Decode prediction
        label = self.label_encoder.inverse_transform([prediction])[0]
        
        # Get probability for each class
        class_probs = {
            self.label_encoder.classes_[i]: float(probabilities[i])
            for i in range(len(self.label_encoder.classes_))
        }
        
        return {
            'prediction': label,
            'confidence': float(confidence),
            'probabilities': class_probs,
            'is_attack': label != 'BENIGN'
        }
    
    def predict_batch(self, features_array: np.ndarray) -> List[Dict[str, Any]]:
        """
        Make predictions on a batch of samples
        
        Args:
            features_array: numpy array of shape (n_samples, n_features)
        
        Returns:
            List of prediction dictionaries
        """
        if features_array.shape[1] != len(self.feature_names):
            raise ValueError(
                f"Feature count mismatch. Expected {len(self.feature_names)}, "
                f"got {features_array.shape[1]}"
            )
        
        # Scale features
        features_scaled = self.scaler.transform(features_array)
        
        # Get predictions and probabilities
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        results = []
        for i, pred in enumerate(predictions):
            label = self.label_encoder.inverse_transform([pred])[0]
            confidence = np.max(probabilities[i])
            
            class_probs = {
                self.label_encoder.classes_[j]: float(probabilities[i][j])
                for j in range(len(self.label_encoder.classes_))
            }
            
            results.append({
                'prediction': label,
                'confidence': float(confidence),
                'probabilities': class_probs,
                'is_attack': label != 'BENIGN'
            })
        
        return results
    
    def predict_with_all_models(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Get predictions from all trained models for comparison
        
        Args:
            features: numpy array of features
        
        Returns:
            Dictionary with predictions from all models
        """
        if features.shape[0] != len(self.feature_names):
            raise ValueError(
                f"Feature count mismatch. Expected {len(self.feature_names)}, "
                f"got {features.shape[0]}"
            )
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        all_predictions = {}
        for model_name, model in self.all_models.items():
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = np.max(probabilities)
            label = self.label_encoder.inverse_transform([prediction])[0]
            
            all_predictions[model_name] = {
                'prediction': label,
                'confidence': float(confidence),
                'is_attack': label != 'BENIGN'
            }
        
        return all_predictions
    
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return self.feature_names
    
    def get_classes(self) -> List[str]:
        """Get classification classes"""
        return self.label_encoder.classes_.tolist()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return self.model_info


# Global predictor instance
_predictor = None

def get_predictor(model_dir=None):
    """Get or create predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = ModelPredictor(model_dir)
    return _predictor
