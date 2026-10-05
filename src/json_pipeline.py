import json
import pandas as pd
from .common import DATA, get_logger, validate, clean_and_transform

def run() -> pd.DataFrame:
    logger = get_logger("json_pipeline")
    source = DATA / "json/raw/students.json"
    output = DATA / "json/processed/students_json_processed.csv"
    logger.info("Extract JSON: %s", source)
    with open(source, encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    validate(df, logger)
    df = clean_and_transform(df, logger)
    validate(df, logger)
    df.to_csv(output, index=False, encoding="utf-8-sig")
    logger.info("JSON pipeline completed: %s", output)
    return df
