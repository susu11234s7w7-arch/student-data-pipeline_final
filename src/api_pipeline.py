import json
import requests
import pandas as pd

from .common import DATA, get_logger, validate, clean_and_transform


URL = "https://dummyjson.com/users"


def run(pages: int = 3, limit: int = 10) -> pd.DataFrame:
    logger = get_logger("api_pipeline")

    records = []
    raw_pages = []

    # Extract: API + Pagination
    for page in range(pages):
        skip = page * limit

        logger.info(
            "API request page=%s skip=%s limit=%s",
            page + 1,
            skip,
            limit
        )

        response = requests.get(
            URL,
            params={
                "skip": skip,
                "limit": limit
            },
            timeout=10
        )

        response.raise_for_status()

        payload = response.json()

        raw_pages.append(payload)

        records.extend(
            payload.get("users", [])
        )

        if not payload.get("users"):
            break

    # Save Raw API data
    raw_path = DATA / "api/raw/users_raw.json"

    with open(
        raw_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            raw_pages,
            f,
            ensure_ascii=False,
            indent=2
        )

    # Convert API records to DataFrame
    df = pd.DataFrame(records)

    # Extract city from nested address
    if "address" in df.columns:
        df["city"] = df["address"].apply(
            lambda x: x.get("city")
            if isinstance(x, dict)
            else None
        )

        df = df.drop(
            columns=["address"]
        )

    # Create full name
    if (
        "name" not in df.columns
        and {"firstName", "lastName"}.issubset(df.columns)
    ):
        df["name"] = (
            df["firstName"].fillna("")
            + " "
            + df["lastName"].fillna("")
        )

    # Transform age into score from 0 to 100
    age = pd.to_numeric(
        df.get(
            "age",
            pd.Series(dtype=float)
        ),
        errors="coerce"
    )

    df["score"] = (
        (age - 18) / (60 - 18) * 100
    ).clip(
        0,
        100
    ).round(2)

    # Identify the source
    df["department"] = "API Source"

    # Keep common schema
    keep = [
        "id",
        "name",
        "city",
        "age",
        "score",
        "department"
    ]

    df = df[
        [c for c in keep if c in df.columns]
    ]

    # Validation
    validate(
        df,
        logger
    )

    # Cleaning + Transformation
    df = clean_and_transform(
        df,
        logger
    )

    # Final validation
    validate(
        df,
        logger
    )

    # Load processed result
    output = (
        DATA
        / "api/processed/students_api_processed.csv"
    )

    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    logger.info(
        "API pipeline completed: %s",
        output
    )

    return df