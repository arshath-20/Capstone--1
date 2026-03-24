# Configuration settings for Cyber Intrusion Detection System

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
DATA_DIR = PROJECT_ROOT / 'data'
MODEL_DIR = BACKEND_DIR / 'model'

# Backend configuration
BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', 8000))
BACKEND_RELOAD = os.getenv('BACKEND_RELOAD', True)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BACKEND_DIR}/intrusion_detection.db')

# Model configuration
MODEL_FILE = MODEL_DIR / 'saved_model.pkl'
SCALER_FILE = MODEL_DIR / 'scaler.pkl'
LABEL_ENCODER_FILE = MODEL_DIR / 'label_encoder.pkl'
FEATURE_NAMES_FILE = MODEL_DIR / 'feature_names.pkl'
ALL_MODELS_FILE = MODEL_DIR / 'all_models.pkl'
MODEL_INFO_FILE = MODEL_DIR / 'model_info.json'
MODEL_METRICS_FILE = MODEL_DIR / 'model_metrics.json'

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API configuration
API_BASE_URL = f'http://{BACKEND_HOST}:{BACKEND_PORT}'
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.75))

# Batch processing configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 32))
MAX_BATCH_SIZE = 10000

# Dataset configuration
DATASET_FILE = DATA_DIR / 'dataset.csv'
TEST_SIZE = 0.2
RANDOM_STATE = 42
STRATIFY = True

# Model training configuration
MODELS_TO_TRAIN = ['Random Forest', 'Logistic Regression', 'Decision Tree', 'XGBoost']
N_ESTIMATORS = 100
MAX_DEPTH = 15
LEARNING_RATE = 0.1

# Feature configuration
N_FEATURES = 82
N_IMPORTANT_FEATURES = 20
N_TOP_FEATURES = 10

# Frontend configuration
STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', 8501))
STREAMLIT_THEME = 'dark'

# System configuration
DEBUG = os.getenv('DEBUG', False) == 'True'
WORKERS = int(os.getenv('WORKERS', 4))
