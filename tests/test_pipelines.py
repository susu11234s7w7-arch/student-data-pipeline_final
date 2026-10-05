import json
import pandas as pd
from pathlib import Path
from src.common import clean_and_transform

def test_clean_fills_missing_values():
    df = pd.DataFrame([{"id":1,"name":" A ","city":None,"age":20,"score":None,"department":"CS"},{"id":2,"name":"B","city":"Sanaa","age":22,"score":80,"department":"CS"}])
    out = clean_and_transform(df, __import__('logging').getLogger("test"))
    assert out["score"].isna().sum() == 0
    assert out.loc[0,"name"] == "A"

def test_csv_pipeline():
    from src.csv_pipeline import run
    df = run()
    assert not df.empty
    assert {"id","name","city","age","score","department"}.issubset(df.columns)

def test_json_pipeline():
    from src.json_pipeline import run
    df = run()
    assert len(df) == 5

def test_independent_outputs_exist():
    from src.csv_pipeline import run as csv_run
    from src.json_pipeline import run as json_run
    csv_run(); json_run()
    assert Path("data/csv/processed/students_csv_processed.csv").exists()
    assert Path("data/json/processed/students_json_processed.csv").exists()
