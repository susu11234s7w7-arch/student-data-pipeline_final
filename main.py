import argparse
from src.csv_pipeline import run as run_csv
from src.json_pipeline import run as run_json
from src.api_pipeline import run as run_api
from src.mongodb_pipeline import run as run_mongodb

PIPELINES = {"csv": run_csv, "json": run_json, "api": run_api, "mongodb": run_mongodb}

def main():
    parser = argparse.ArgumentParser(description="Independent Student Data ETL Pipelines")
    parser.add_argument("source", choices=["csv","json","api","mongodb","all"], help="Pipeline to run")
    args = parser.parse_args()
    if args.source == "all":
        for name, pipeline in PIPELINES.items():
            print(f"\n=== {name.upper()} PIPELINE ===")
            try:
                df = pipeline()
                print(f"Completed: {len(df)} records")
            except Exception as exc:
                print(f"FAILED: {exc}")
    else:
        df = PIPELINES[args.source]()
        print(f"{args.source.upper()} pipeline completed: {len(df)} records")
        print(df.head().to_string(index=False))

if __name__ == "__main__":
    main()
