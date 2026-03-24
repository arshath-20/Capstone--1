"""
Main FastAPI Application
Central entry point for the backend server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys
import json
import numpy as np

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Custom JSON encoder for numpy/pandas types
class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy and pandas types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes
from api.routes import router as api_router

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    """
    # Startup
    logger.info("🚀 Starting Cyber Intrusion Detection System Backend")
    from model.predict import get_predictor
    try:
        predictor = get_predictor()
        logger.info(f"✓ Model loaded successfully")
        logger.info(f"✓ Available features: {len(predictor.get_feature_names())}")
        logger.info(f"✓ Classes: {predictor.get_classes()}")
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}")
    
    from database.models import get_db_manager
    try:
        db_manager = get_db_manager()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Cyber Intrusion Detection System Backend")

# Create FastAPI app
app = FastAPI(
    title="Cyber Intrusion Detection System",
    description="Real-time network intrusion detection using machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# Add custom JSON encoder
# Override default JSONResponse to use custom encoder
from starlette.responses import JSONResponse as StarletteJSONResponse

class CustomJSONResponse(StarletteJSONResponse):
    """Custom JSON response that handles numpy types"""
    def render(self, content):
        return json.dumps(
            content,
            cls=NumpyEncoder,
        ).encode("utf-8")

# Update app to use custom response class
app.default_response_class = CustomJSONResponse

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        'name': 'Cyber Intrusion Detection System',
        'version': '1.0.0',
        'description': 'Real-time network intrusion detection using machine learning',
        'endpoints': {
            'POST /api/predict': 'Make a single prediction',
            'POST /api/batch_predict': 'Make batch predictions from CSV',
            'GET /api/metrics': 'Get model performance metrics',
            'GET /api/logs': 'Get recent prediction logs',
            'GET /api/statistics': 'Get overall statistics',
            'GET /api/health': 'Health check',
            'GET /docs': 'API documentation (Swagger UI)',
            'GET /redoc': 'API documentation (ReDoc)'
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={'detail': 'Internal server error'}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
