# reads csv file and fills postgres db
import polars as pl
from sqlalchemy import create_engine
import sys
import os
import argparse
from pathlib import Path
import logging


def main(input_file, output_file, logger):
    # reads csv
    df = pl.read_csv(input_file, separator="\t")

    # connects to db

    # Environment variables
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'mydatabase')
    db_user = os.getenv('DB_USER', 'myuser')
    db_password = os.getenv('DB_PASSWORD', 'mypassword')

    # Create the database engine using SQLAlchemy
    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    print("Connected to PostgreSQL!")

    df.write_database("teste",connection=engine)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")

    args = parser.parse_args()
    input_path = Path(args.input_file)
    output_path = Path(args.output_file)
    logging.basicConfig(level=logging.NOTSET)

    logger = logging.getLogger("annotate")
    logger.setLevel(logging.NOTSET)  # Allow all messages to pass to handlers
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)  # Only log INFO, WARNING, and ERROR to console
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler
    log_path = Path("logs") / "annotate.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_log = logging.FileHandler(filename=log_path)
    file_log.setLevel(logging.NOTSET)  # Log absolutely everything to file
    file_log.setFormatter(formatter)
    logger.addHandler(file_log)

    main(input_file=input_path, output_file=output_path, logger=logger)