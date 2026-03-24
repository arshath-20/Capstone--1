"""
Machine Learning Model Training Pipeline
Trains and evaluates multiple classification models for intrusion detection
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import warnings

warnings.filterwarnings('ignore')

class ModelTrainer:
    def __init__(self, dataset_path: str):
        """Initialize the model trainer"""
        self.dataset_path = dataset_path
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.model_metrics = {}
        self.scaler = StandardScaler()
        self.label_encoder = None
        self.feature_names = None
        
    def load_data(self) -> tuple:
        """Load and explore the dataset"""
        print("📊 Loading dataset...")
        df = pd.read_csv(self.dataset_path)
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        print(f"Label distribution:\n{df['Label'].value_counts()}")
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame):
        """Preprocess the dataset"""
        print("\n🔧 Preprocessing data...")
        
        # Create a copy
        df = df.copy()
        
        # Handle missing values
        df = df.fillna(df.mean(numeric_only=True))
        
        # Handle infinity values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        # Separate features and target
        X = df.drop('Label', axis=1)
        y = df['Label']
        
        self.feature_names = X.columns.tolist()
        
        # Encode target variable
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        print(f"Classes: {self.label_encoder.classes_}")
        print(f"Features: {len(self.feature_names)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.X_train = X_train_scaled
        self.X_test = X_test_scaled
        self.y_train = y_train
        self.y_test = y_test
        
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Test set size: {X_test.shape[0]}")
        
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self):
        """Train Random Forest model"""
        print("\n🌲 Training Random Forest...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(self.X_train, self.y_train)
        self.models['Random Forest'] = model
        print("✓ Random Forest trained successfully")
        return model
    
    def train_logistic_regression(self):
        """Train Logistic Regression model"""
        print("\n📈 Training Logistic Regression...")
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
            solver='lbfgs'
        )
        model.fit(self.X_train, self.y_train)
        self.models['Logistic Regression'] = model
        print("✓ Logistic Regression trained successfully")
        return model
    
    def train_decision_tree(self):
        """Train Decision Tree model"""
        print("\n🌳 Training Decision Tree...")
        model = DecisionTreeClassifier(
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        model.fit(self.X_train, self.y_train)
        self.models['Decision Tree'] = model
        print("✓ Decision Tree trained successfully")
        return model
    
    def train_xgboost(self):
        """Train XGBoost model (optional)"""
        try:
            import xgboost as xgb
            print("\n⚡ Training XGBoost...")
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=7,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                eval_metric='logloss'
            )
            model.fit(self.X_train, self.y_train)
            self.models['XGBoost'] = model
            print("✓ XGBoost trained successfully")
            return model
        except ImportError:
            print("⚠️ XGBoost not installed, skipping...")
            return None
    
    def evaluate_models(self):
        """Evaluate all trained models"""
        print("\n📊 Evaluating models...")
        
        for model_name, model in self.models.items():
            print(f"\n{model_name}:")
            
            # Predictions
            y_pred = model.predict(self.X_test)
            
            # Metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(self.y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(self.y_test, y_pred, average='weighted', zero_division=0)
            cm = confusion_matrix(self.y_test, y_pred)
            
            # Store metrics
            self.model_metrics[model_name] = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'confusion_matrix': cm.tolist(),
                'classification_report': classification_report(
                    self.y_test, y_pred, 
                    target_names=self.label_encoder.classes_,
                    output_dict=True
                )
            }
            
            print(f"  Accuracy:  {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall:    {recall:.4f}")
            print(f"  F1-Score:  {f1:.4f}")
        
        return self.model_metrics
    
    def get_best_model(self):
        """Get the best performing model"""
        best_model_name = max(
            self.model_metrics,
            key=lambda x: self.model_metrics[x]['f1_score']
        )
        return best_model_name, self.models[best_model_name]
    
    def get_feature_importance(self, model_name='Random Forest'):
        """Extract feature importance from tree-based models"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            return importance_df.head(20)
        
        return None
    
    def save_models(self, output_dir='../../backend/model'):
        """Save trained models and preprocessing objects"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 Saving models to {output_path}...")
        
        # Save best model
        best_model_name, best_model = self.get_best_model()
        joblib.dump(best_model, output_path / 'saved_model.pkl')
        print(f"✓ Saved best model: {best_model_name}")
        
        # Save all models
        with open(output_path / 'all_models.pkl', 'wb') as f:
            pickle.dump(self.models, f)
        print("✓ Saved all trained models")
        
        # Save scaler
        joblib.dump(self.scaler, output_path / 'scaler.pkl')
        print("✓ Saved scaler")
        
        # Save label encoder
        joblib.dump(self.label_encoder, output_path / 'label_encoder.pkl')
        print("✓ Saved label encoder")
        
        # Save feature names
        with open(output_path / 'feature_names.pkl', 'wb') as f:
            pickle.dump(self.feature_names, f)
        print("✓ Saved feature names")
        
        # Save metrics
        with open(output_path / 'model_metrics.json', 'w') as f:
            json.dump(self.model_metrics, f, indent=2)
        print("✓ Saved model metrics")
        
        # Save model info
        model_info = {
            'best_model': best_model_name,
            'dataset': 'CICIDS2017',
            'test_size': 0.2,
            'models_trained': list(self.models.keys()),
            'features_count': len(self.feature_names),
            'classes': self.label_encoder.classes_.tolist()
        }
        with open(output_path / 'model_info.json', 'w') as f:
            json.dump(model_info, f, indent=2)
        print("✓ Saved model info")


def main():
    """Main training pipeline"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'dataset.csv'
    
    # Initialize trainer
    trainer = ModelTrainer(str(data_path))
    
    # Load and preprocess
    df = trainer.load_data()
    trainer.preprocess_data(df)
    
    # Train models
    trainer.train_random_forest()
    trainer.train_logistic_regression()
    trainer.train_decision_tree()
    trainer.train_xgboost()
    
    # Evaluate
    metrics = trainer.evaluate_models()
    
    # Get best model
    best_model_name, best_model = trainer.get_best_model()
    print(f"\n🏆 Best Model: {best_model_name}")
    print(f"   F1-Score: {metrics[best_model_name]['f1_score']:.4f}")
    
    # Feature importance
    importance_df = trainer.get_feature_importance()
    print("\n📊 Top 20 Important Features:")
    print(importance_df)
    
    # Save models
    trainer.save_models()
    
    print("\n✅ Training completed successfully!")


if __name__ == "__main__":
    main()
