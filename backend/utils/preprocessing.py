"""
Data Preprocessing Utilities
Common preprocessing functions for data cleaning and transformation
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
import re

class DataPreprocessor:
    """Preprocesses network traffic data"""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare dataframe
        
        Args:
            df: Input dataframe
        
        Returns:
            Cleaned dataframe
        """
        df = df.copy()
        
        # Handle missing values
        df = df.fillna(df.mean(numeric_only=True))
        
        # Handle infinity values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        # Ensure all values are numeric (except Label)
        for col in df.columns:
            if col != 'Label':
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
        
        return df
    
    @staticmethod
    def normalize_features(X: np.ndarray, scaler=None) -> Tuple[np.ndarray, Any]:
        """
        Normalize features using StandardScaler
        
        Args:
            X: Feature matrix
            scaler: Optional pre-fitted scaler
        
        Returns:
            Normalized features and scaler
        """
        from sklearn.preprocessing import StandardScaler
        
        if scaler is None:
            scaler = StandardScaler()
            X_normalized = scaler.fit_transform(X)
        else:
            X_normalized = scaler.transform(X)
        
        return X_normalized, scaler
    
    @staticmethod
    def select_important_features(df: pd.DataFrame, n_features: int = 50) -> List[str]:
        """
        Select important features using variance and correlation
        
        Args:
            df: Dataframe with features
            n_features: Number of features to select
        
        Returns:
            List of selected feature names
        """
        # Calculate variance
        variance = df.var(numeric_only=True).sort_values(ascending=False)
        
        # Remove low variance features
        threshold = variance.quantile(0.1)
        important_features = variance[variance > threshold].index.tolist()
        
        # Limit to n_features
        return important_features[:n_features]
    
    @staticmethod
    def handle_outliers(X: np.ndarray, method: str = 'iqr') -> np.ndarray:
        """
        Handle outliers in features
        
        Args:
            X: Feature matrix
            method: 'iqr' for IQR method or 'zscore' for Z-score
        
        Returns:
            Array with outliers capped
        """
        X = X.copy()
        
        if method == 'iqr':
            Q1 = np.percentile(X, 25, axis=0)
            Q3 = np.percentile(X, 75, axis=0)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            X = np.clip(X, lower_bound, upper_bound)
        
        elif method == 'zscore':
            mean = np.mean(X, axis=0)
            std = np.std(X, axis=0)
            z_scores = np.abs((X - mean) / std)
            
            X[z_scores > 3] = np.median(X, axis=0)
        
        return X
    
    @staticmethod
    def balance_classes(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Balance class distribution using random undersampling
        
        Args:
            X: Features
            y: Labels
        
        Returns:
            Balanced X and y
        """
        from sklearn.utils import resample
        
        df = pd.DataFrame(X)
        df['target'] = y
        
        # Get counts
        target_counts = df['target'].value_counts()
        min_count = target_counts.min()
        
        balanced_dfs = []
        for target in df['target'].unique():
            target_df = df[df['target'] == target]
            if len(target_df) > min_count:
                target_df = resample(target_df, n_samples=min_count, random_state=42)
            balanced_dfs.append(target_df)
        
        balanced_df = pd.concat(balanced_dfs, ignore_index=True)
        
        X_balanced = balanced_df.drop('target', axis=1).values
        y_balanced = balanced_df['target'].values
        
        return X_balanced, y_balanced


class CSVProcessor:
    """Process CSV files for batch predictions"""
    
    @staticmethod
    def read_csv(file_path: str, expected_features: List[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Read and validate CSV file
        
        Args:
            file_path: Path to CSV file
            expected_features: Expected feature columns
        
        Returns:
            Dataframe and validation report
        """
        report = {
            'success': True,
            'rows': 0,
            'columns': 0,
            'errors': []
        }
        
        try:
            df = pd.read_csv(file_path)
            
            report['rows'] = len(df)
            report['columns'] = len(df.columns)
            
            # Check for required columns
            if expected_features:
                missing_cols = set(expected_features) - set(df.columns)
                if missing_cols:
                    report['errors'].append(f"Missing columns: {missing_cols}")
                    report['success'] = False
            
            # Check for empty dataframe
            if len(df) == 0:
                report['errors'].append("CSV file is empty")
                report['success'] = False
            
            return df, report
        
        except Exception as e:
            report['success'] = False
            report['errors'].append(str(e))
            return None, report
    
    @staticmethod
    def validate_features(df: pd.DataFrame, required_features: List[str]) -> Dict[str, Any]:
        """
        Validate CSV features
        
        Args:
            df: Input dataframe
            required_features: List of required feature names
        
        Returns:
            Validation report
        """
        report = {
            'valid': True,
            'missing_features': [],
            'extra_features': [],
            'invalid_types': [],
            'nan_count': 0
        }
        
        # Check missing features
        df_features = set(df.columns)
        required_set = set(required_features)
        
        report['missing_features'] = list(required_set - df_features)
        report['extra_features'] = list(df_features - required_set)
        
        # Check data types
        for col in required_features:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    report['invalid_types'].append(col)
        
        # Check NaN values
        report['nan_count'] = df[required_features].isnull().sum().sum()
        
        report['valid'] = (
            len(report['missing_features']) == 0 and
            len(report['invalid_types']) == 0 and
            report['nan_count'] == 0
        )
        
        return report
    
    @staticmethod
    def prepare_for_prediction(df: pd.DataFrame, feature_order: List[str]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Prepare CSV data for prediction
        
        Args:
            df: Input dataframe
            feature_order: Expected feature order
        
        Returns:
            Feature array and preparation report
        """
        report = {
            'success': True,
            'samples': 0,
            'warnings': []
        }
        
        try:
            # Make copy
            df = df.copy()
            
            # Remove Label column if present
            if 'Label' in df.columns:
                df = df.drop('Label', axis=1)
            
            # Select and reorder features
            df = df[feature_order]
            
            # Handle missing values
            df = df.fillna(df.mean(numeric_only=True))
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.fillna(0)
            
            # Check for remaining NaN or inf values
            if df.isnull().sum().sum() > 0:
                report['warnings'].append("Some NaN values were found and filled with 0")
            
            report['samples'] = len(df)
            
            return df.values, report
        
        except Exception as e:
            report['success'] = False
            report['warnings'].append(str(e))
            return None, report
