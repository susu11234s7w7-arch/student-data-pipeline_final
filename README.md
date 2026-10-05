# Student Data Independent ETL Pipelines

## Project purpose

This project implements **four independent ETL/Data Integration pipelines** for the same student-data processing problem. The sources are intentionally kept separate so each pipeline can be executed, validated, cleaned, transformed, logged, and evaluated independently.

## Architecture

```text
CSV     -> CSV Pipeline     -> CSV Processed Output
JSON    -> JSON Pipeline    -> JSON Processed Output
REST API-> API Pipeline     -> API Processed Output
MongoDB -> MongoDB Pipeline -> MongoDB Processed Output
```

There is **no cross-source integration step** in the new design. This is intentional: the goal is to compare how each source is extracted and processed independently.

## Common ETL stages

Each pipeline follows the applicable sequence:

`Extract -> Validate -> Clean -> Transform -> Final Validation -> Load`

The extraction stage differs by source:
- CSV: `pandas.read_csv`
- JSON: `json.load` + DataFrame
- API: `requests.get` + JSON + pagination
- MongoDB: `MongoClient` + `find`

## Project structure

```text
student_data_pipeline/
├── data/
│   ├── csv/{raw,processed}/
│   ├── json/{raw,processed}/
│   ├── api/{raw,processed}/
│   └── mongodb/{raw,processed}/
├── logs/
├── src/
│   ├── common.py
│   ├── csv_pipeline.py
│   ├── json_pipeline.py
│   ├── api_pipeline.py
│   └── mongodb_pipeline.py
├── tests/
├── main.py
└── requirements.txt
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run one pipeline

```bash
python main.py csv
python main.py json
python main.py api
python main.py mongodb
```

Run all four:

```bash
python main.py all
```

## MongoDB setup

The MongoDB pipeline expects a running MongoDB server by default:

- URI: `mongodb://localhost:27017/`
- Database: `student_pipeline`
- Collection: `students`

You can override them with environment variables:

```text
MONGODB_URI
MONGODB_DATABASE
MONGODB_COLLECTION
```

Example document schema:

```json
{
  "id": 201,
  "name": "Ahmed",
  "city": "Sanaa",
  "age": 22,
  "score": 90,
  "department": "Computer Science"
}
```

## Testing

```bash
python -m pytest -q
```

## Outputs

Every source has its own processed output. No processed file is merged with another source.

Logs are also separated by pipeline:

- `logs/csv_pipeline.log`
- `logs/json_pipeline.log`
- `logs/api_pipeline.log`
- `logs/mongodb_pipeline.log`
