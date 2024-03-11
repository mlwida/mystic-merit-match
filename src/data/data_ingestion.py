import importlib.resources as resources

import pandas as pd

from data.data_types import Talent
from data.data_types import Job

pd.set_option("display.width", 1000)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 50)
pd.set_option("display.max_colwidth", None)


def read_raw_data():
    with resources.open_text("data_files.raw", "data.json") as file:
        df = pd.read_json(file, orient="records")
    return df


def parse_talent(df):
    df["talent_parsed"] = df.apply(lambda row: Talent.create(row["talent"]), 1)


def parse_job(df):
    df["job_parsed"] = df.apply(lambda row: Job.create(row["job"]), 1)

# TODO think about restructuring ... doc needed

def read_and_prepare_raw_data():
    df = read_raw_data()
    parse_job(df)
    parse_talent(df)
    df["talent"] = df["talent_parsed"]
    df["job"] = df["job_parsed"]
    return df.drop(columns=["job_parsed","talent_parsed"])

def find_all_keys(json_data):
    result = []
    if isinstance(json_data, dict):
        result.append(json_data.keys())
    elif isinstance(json_data, list):
        for item in json_data:
            result.append(find_all_keys(item))
    return result
