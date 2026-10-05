from pathlib import Path
import logging
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(LOGS / f"{name}.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(fh)
    return logger

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def clean_and_transform(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    df = standardize_columns(df)
    before = len(df)
    df = df.drop_duplicates().copy()
    for col in ["name", "city", "department"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
    for col in ["age", "score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
    if "age" in df.columns:
        df["age"] = df["age"].round().astype("Int64")
    if "score" in df.columns:
        df["score"] = df["score"].round(2)
    if "score" in df.columns:
        df["score_level"] = pd.cut(df["score"], bins=[-1,59,74,89,101], labels=["Fail","Pass","Good","Excellent"])
    logger.info("Clean/transform: %s -> %s records", before, len(df))
    return df

def validate(df: pd.DataFrame, logger: logging.Logger) -> None:
    required = {"id", "name", "city", "age", "score", "department"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("Dataset is empty")
    logger.info("Validation passed: %s records", len(df))
