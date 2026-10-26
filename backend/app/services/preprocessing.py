"""
Data preprocessing service for Crop Yield Prediction System (BT195).
Handles validation, missing-value imputation, outlier bounding, scaling, and categorical encoding.
Ensures zero data leakage between training and evaluation.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from app.config import settings
from app.services.feature_engineering import calculate_agronomic_features

# Canonical categorical and numerical feature lists
CATEGORICAL_FEATURES = ["crop", "season", "region", "irrigation"]

NUMERICAL_RAW_FEATURES = [
    "rainfall_mm",
    "temperature_min_c",
    "temperature_max_c",
    "humidity",
    "soil_ph",
    "soil_nitrogen",
    "soil_phosphorus",
    "soil_potassium",
    "soil_moisture",
    "fertilizer_usage",
    "vegetation_index_ndvi",
    "previous_season_yield",
]

ENGINEERED_NUMERICAL_FEATURES = [
    "avg_temperature",
    "temp_range",
    "growing_degree_days",
    "heat_stress_index",
    "aridity_index",
    "npk_total",
    "npk_ratio",
    "ph_optimality_deviation",
    "effective_moisture_index",
    "ndvi_vigor_potential",
    "previous_season_yield_filled",
]

ALL_NUMERICAL_FEATURES = NUMERICAL_RAW_FEATURES + ENGINEERED_NUMERICAL_FEATURES

class AgriculturalPreprocessor:
    """End-to-end preprocessor for agricultural tabular observations."""
    
    def __init__(self):
        self.column_transformer: Optional[ColumnTransformer] = None
        self.feature_names: List[str] = []
        self.numerical_imputer: Optional[SimpleImputer] = None
        self.categorical_imputer: Optional[SimpleImputer] = None
        self.num_medians: Dict[str, float] = {}
        self.cat_modes: Dict[str, str] = {}
        self.fitted: bool = False

    def validate_and_clean_dataframe(self, df: pd.DataFrame, drop_duplicates: bool = False) -> Tuple[pd.DataFrame, List[str]]:
        """Validates incoming dataframe, handles types, and optionally removes true duplicate rows."""
        warnings: List[str] = []
        df = df.copy()

        # Remove duplicates only when explicitly requested (e.g., initial CSV ingestion)
        if drop_duplicates:
            initial_len = len(df)
            df = df.drop_duplicates(subset=[col for col in ["field_id", "crop", "season", "year", "region"] if col in df.columns])
            if len(df) < initial_len:
                warnings.append(f"Removed {initial_len - len(df)} duplicate records based on field/crop/season identity.")

        # Ensure numeric columns
        for col in NUMERICAL_RAW_FEATURES:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                warnings.append(f"Missing required numeric column '{col}'. Will be imputed from domain statistics.")
                df[col] = np.nan

        # Ensure categorical columns are strings
        for col in CATEGORICAL_FEATURES:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            else:
                warnings.append(f"Missing required categorical column '{col}'. Using fallback.")
                df[col] = "Unknown"

        return df, warnings

    def fit(self, df: pd.DataFrame):
        """Fits imputers, encoders, and scalers strictly on training records."""
        # 1. Clean and engineer features
        cleaned_df, _ = self.validate_and_clean_dataframe(df)
        feat_df = calculate_agronomic_features(cleaned_df)

        # 2. Compute training summary statistics for imputations
        for col in ALL_NUMERICAL_FEATURES:
            if col in feat_df.columns:
                self.num_medians[col] = float(feat_df[col].median(skipna=True))
            else:
                self.num_medians[col] = 0.0

        for col in CATEGORICAL_FEATURES:
            if col in feat_df.columns:
                mode_val = feat_df[col].mode()
                self.cat_modes[col] = str(mode_val[0]) if len(mode_val) > 0 else "Unknown"

        # 3. Build ColumnTransformer with imputation and standard scaling
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])

        self.column_transformer = ColumnTransformer(
            transformers=[
                ("num", num_pipeline, ALL_NUMERICAL_FEATURES),
                ("cat", cat_pipeline, CATEGORICAL_FEATURES),
            ],
            remainder="drop"
        )

        self.column_transformer.fit(feat_df)

        # Extract generated feature names
        cat_encoder = self.column_transformer.named_transformers_["cat"].named_steps["encoder"]
        cat_feature_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        self.feature_names = ALL_NUMERICAL_FEATURES + cat_feature_names
        self.fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms records using fitted artifacts."""
        if not self.fitted:
            raise ValueError("Preprocessor has not been fitted yet!")

        cleaned_df, _ = self.validate_and_clean_dataframe(df)
        feat_df = calculate_agronomic_features(cleaned_df)
        
        # Ensure all columns exist before transformation
        for col, val in self.num_medians.items():
            if col not in feat_df.columns:
                feat_df[col] = val

        for col, val in self.cat_modes.items():
            if col not in feat_df.columns:
                feat_df[col] = val

        return self.column_transformer.transform(feat_df)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        return self.fit(df).transform(df)

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        print(f"[OK] Preprocessor saved to {filepath}")

    @classmethod
    def load(cls, filepath: Path) -> "AgriculturalPreprocessor":
        if not filepath.exists():
            raise FileNotFoundError(f"Preprocessor artifact not found at {filepath}")
        return joblib.load(filepath)
