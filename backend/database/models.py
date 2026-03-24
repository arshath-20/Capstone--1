"""
Database Models and ORM Setup
SQLAlchemy models for storing predictions and logs
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pathlib import Path
import json

Base = declarative_base()

class PredictionLog(Base):
    """Model for storing prediction logs"""
    __tablename__ = 'prediction_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    features = Column(JSON)  # Store input features as JSON
    prediction = Column(String)  # BENIGN or attack type
    confidence = Column(Float)  # Confidence score
    is_attack = Column(Boolean)  # True if attack detected
    model_used = Column(String)  # Name of model used
    probabilities = Column(JSON)  # Class probabilities
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': int(self.id) if self.id else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'prediction': self.prediction,
            'confidence': float(self.confidence) if self.confidence else None,
            'is_attack': self.is_attack,
            'model_used': self.model_used
        }

class BatchAnalysisLog(Base):
    """Model for storing batch analysis logs"""
    __tablename__ = 'batch_analysis_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    filename = Column(String)  # Original CSV filename
    total_samples = Column(Integer)  # Total samples analyzed
    attack_count = Column(Integer)  # Number of attacks detected
    benign_count = Column(Integer)  # Number of benign samples
    accuracy = Column(Float)  # If ground truth available
    results_summary = Column(JSON)  # Summary statistics
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': int(self.id) if self.id else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'filename': self.filename,
            'total_samples': int(self.total_samples) if self.total_samples else None,
            'attack_count': int(self.attack_count) if self.attack_count else None,
            'benign_count': int(self.benign_count) if self.benign_count else None,
            'results_summary': self.results_summary
        }

class SystemMetrics(Base):
    """Model for storing system performance metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_predictions = Column(Integer)  # Total predictions made
    total_attacks_detected = Column(Integer)  # Total attacks detected
    total_benign = Column(Integer)  # Total benign
    avg_confidence = Column(Float)  # Average confidence score
    model_accuracy = Column(Float)  # Model accuracy (if test data available)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': int(self.id) if self.id else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'total_predictions': int(self.total_predictions) if self.total_predictions else None,
            'total_attacks_detected': int(self.total_attacks_detected) if self.total_attacks_detected else None,
            'total_benign': int(self.total_benign) if self.total_benign else None,
            'avg_confidence': float(self.avg_confidence) if self.avg_confidence else None,
            'model_accuracy': float(self.model_accuracy) if self.model_accuracy else None
        }


class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_path: str = 'intrusion_detection.db'):
        """Initialize database manager"""
        self.db_path = Path(db_path)
        self.engine = None
        self.SessionLocal = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database connection"""
        db_url = f'sqlite:///{self.db_path}'
        self.engine = create_engine(db_url, connect_args={'check_same_thread': False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        print(f"✓ Database initialized: {self.db_path}")
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def add_prediction_log(self, session: Session, prediction: dict) -> PredictionLog:
        """Add a prediction log"""
        log = PredictionLog(
            features=prediction.get('features'),
            prediction=prediction.get('prediction'),
            confidence=prediction.get('confidence'),
            is_attack=prediction.get('is_attack'),
            model_used=prediction.get('model_used', 'Random Forest'),
            probabilities=prediction.get('probabilities')
        )
        session.add(log)
        session.commit()
        return log
    
    def add_batch_analysis(self, session: Session, analysis: dict) -> BatchAnalysisLog:
        """Add a batch analysis log"""
        log = BatchAnalysisLog(
            filename=analysis.get('filename'),
            total_samples=analysis.get('total_samples'),
            attack_count=analysis.get('attack_count'),
            benign_count=analysis.get('benign_count'),
            results_summary=analysis.get('results_summary')
        )
        session.add(log)
        session.commit()
        return log
    
    def get_prediction_logs(self, session: Session, limit: int = 100) -> list:
        """Get recent prediction logs"""
        return session.query(PredictionLog).order_by(
            PredictionLog.timestamp.desc()
        ).limit(limit).all()
    
    def get_batch_logs(self, session: Session, limit: int = 50) -> list:
        """Get recent batch analysis logs"""
        return session.query(BatchAnalysisLog).order_by(
            BatchAnalysisLog.timestamp.desc()
        ).limit(limit).all()
    
    def get_statistics(self, session: Session) -> dict:
        """Get overall statistics"""
        prediction_logs = session.query(PredictionLog).all()
        batch_logs = session.query(BatchAnalysisLog).all()
        
        total_predictions = len(prediction_logs)
        attack_count = sum(1 for log in prediction_logs if log.is_attack)
        benign_count = total_predictions - attack_count
        
        avg_confidence = (
            sum(log.confidence for log in prediction_logs) / total_predictions
            if total_predictions > 0 else 0
        )
        
        total_batch_samples = sum(log.total_samples for log in batch_logs)
        total_batch_attacks = sum(log.attack_count for log in batch_logs)
        
        # Convert to native Python types for JSON serialization
        return {
            'total_predictions': int(total_predictions),
            'total_attacks': int(attack_count),
            'total_benign': int(benign_count),
            'average_confidence': float(avg_confidence),
            'total_batch_samples': int(total_batch_samples),
            'total_batch_attacks': int(total_batch_attacks),
            'attack_percentage': float((attack_count / total_predictions * 100) if total_predictions > 0 else 0)
        }
    
    def clear_logs(self, session: Session, days: int = 30):
        """Clear logs older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        session.query(PredictionLog).filter(
            PredictionLog.timestamp < cutoff_date
        ).delete()
        session.query(BatchAnalysisLog).filter(
            BatchAnalysisLog.timestamp < cutoff_date
        ).delete()
        session.commit()


# Global database manager instance
_db_manager = None

def get_db_manager(db_path: str = None):
    """Get or create database manager"""
    global _db_manager
    if _db_manager is None:
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'intrusion_detection.db'
        _db_manager = DatabaseManager(str(db_path))
    return _db_manager
