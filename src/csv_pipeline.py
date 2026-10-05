import pandas as pd
from .common import DATA, get_logger, validate, clean_and_transform

def run() -> pd.DataFrame:
    logger = get_logger("csv_pipeline")
    source = DATA / "csv/raw/students.csv"
    output = DATA / "csv/processed/students_csv_processed.csv"
    logger.info("Extract CSV: %s", source)
    df = pd.read_csv(source)
    validate(df, logger)
    df = clean_and_transform(df, logger)
    validate(df, logger)
    df.to_csv(output, index=False, encoding="utf-8-sig")
    logger.info("CSV pipeline completed: %s", output)
    return df
