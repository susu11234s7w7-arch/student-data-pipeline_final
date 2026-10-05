import json
import os

import pandas as pd

from .common import DATA, get_logger, validate, clean_and_transform


def run() -> pd.DataFrame:
    logger = get_logger("mongodb_pipeline")

    try:
        from pymongo import MongoClient
    except ImportError as e:
        raise RuntimeError(
            "Install dependencies with: pip install -r requirements.txt"
        ) from e

    # -----------------------------
    # MongoDB Configuration
    # -----------------------------

    uri = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017/"
    )

    db_name = os.getenv(
        "MONGODB_DATABASE",
        "suhail"
    )

    collection_name = os.getenv(
        "MONGODB_COLLECTION",
        "alhaj"
    )

    logger.info(
        "Connecting to MongoDB: database=%s collection=%s",
        db_name,
        collection_name
    )

    # -----------------------------
    # Connect
    # -----------------------------

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000
    )

    client.admin.command("ping")

    collection = client[
        db_name
    ][
        collection_name
    ]

    # -----------------------------
    # Extract
    # -----------------------------

    docs = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    if not docs:
        client.close()
        raise ValueError(
            "MongoDB collection is empty"
        )

    logger.info(
        "Extracted %s MongoDB documents",
        len(docs)
    )

    # -----------------------------
    # Save Raw Data
    # -----------------------------

    raw_path = (
        DATA
        / "mongodb/raw/students_raw.json"
    )

    with open(
        raw_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            docs,
            f,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    # -----------------------------
    # Normalize Documents
    # -----------------------------

    normalized = []
    rejected = []

    for doc in docs:

        # ID
        student_id = doc.get(
            "student_id"
        )

        # Name
        name = doc.get(
            "name"
        )

        # Age
        age = doc.get(
            "age"
        )

        # City:
        # Supports both:
        # city: "Sanaa"
        # address: {"city": "Sanaa"}
        city = doc.get("city")

        if city is None:
            address = doc.get("address")

            if isinstance(address, dict):
                city = address.get("city")

        # GPA:
        # Supports both:
        # gpa: 3.6
        # academic: {"gpa": 3.9}
        gpa = doc.get("gpa")

        if gpa is None:
            academic = doc.get("academic")

            if isinstance(academic, dict):
                gpa = academic.get("gpa")

        # Department:
        # Use major if available
        department = doc.get(
            "major"
        )

        if department is None:
            department = "MongoDB Source"

        # -------------------------
        # Validate critical fields
        # -------------------------

        if (
            student_id is None
            or name is None
            or age is None
            or city is None
            or gpa is None
        ):
            rejected.append(doc)
            continue

        normalized.append(
            {
                "id": student_id,
                "name": name,
                "city": city,
                "age": age,
                "gpa": gpa,
                "department": department
            }
        )

    # -----------------------------
    # Save Rejected Records
    # -----------------------------

    rejected_path = (
        DATA
        / "mongodb/rejected_records.csv"
    )

    if rejected:
        pd.DataFrame(
            rejected
        ).to_csv(
            rejected_path,
            index=False,
            encoding="utf-8-sig"
        )

        logger.warning(
            "Rejected %s MongoDB records",
            len(rejected)
        )

    if not normalized:
        client.close()

        raise ValueError(
            "No valid MongoDB records after normalization"
        )

    # -----------------------------
    # Create DataFrame
    # -----------------------------

    df = pd.DataFrame(
        normalized
    )

    # -----------------------------
    # Transform GPA → Score
    # -----------------------------

    df["gpa"] = pd.to_numeric(
        df["gpa"],
        errors="coerce"
    )

    df["score"] = (
        df["gpa"] * 25
    ).clip(
        0,
        100
    ).round(2)

    # Remove temporary GPA column
    df = df.drop(
        columns=["gpa"]
    )

    # -----------------------------
    # First Validation
    # -----------------------------

    validate(
        df,
        logger
    )

    # -----------------------------
    # Cleaning + Transformation
    # -----------------------------

    df = clean_and_transform(
        df,
        logger
    )

    # -----------------------------
    # Final Validation
    # -----------------------------

    validate(
        df,
        logger
    )

    # -----------------------------
    # Load
    # -----------------------------

    output = (
        DATA
        / "mongodb/processed/"
        "students_mongodb_processed.csv"
    )

    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    logger.info(
        "MongoDB pipeline completed: %s records",
        len(df)
    )

    client.close()

    return df