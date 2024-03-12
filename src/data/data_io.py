"""
Provides methods for reading and first preprocessing of raw input data plus some utils functions.
"""

import importlib.resources as resources

import pandas as pd

from data.data_types import Job
from data.data_types import Talent


def read_raw_data():
    """
    Reads the csv with raw json data from the internal data source.
    :return:DataFrame representing the csv
    :raises OSError: if e.g. the file is not there
    """
    path = resources.path("data_files.raw", "data.json")
    try:
        with open(path.as_posix()) as file:
            df = pd.read_json(file, orient="records")
    except OSError:
        print(f"Failed to read data from {path}")
        raise
    else:
        print(f"Successfully read {df.shape[0]} rows from {path}")
    return df


def read_and_prepare_raw_data(drop_source: bool = True, write_interim_data: bool = False) -> pd.DataFrame:
    """
    Reads the raw data from internal data source and adds columns for Job and Talent, the internal representation

    Afterward the columns for job and talent contain the new internal representation. The source data can be found
    in 'talent_source' and 'job_source' respectively.

    :param drop_source: if True, then the source columns for talent and job are dropped.
    :param write_interim_data: if True, then the new DataFrame is also written to the internal data repository
    :return: a DataFrame with new columns added for classes Job and Talent
    """
    df = read_raw_data()
    print("Add columns for Job and Talent, the internal representation of raw json data")
    if not drop_source:
        df["job_source"] = df["job"]
    df["job"] = df.apply(lambda row: Job.create(row["job"]), 1)
    if not drop_source:
        df["talent_source"] = df["talent"]
    df["talent"] = df.apply(lambda row: Talent.create(row["talent"]), 1)

    if write_interim_data:
        write_data_frame_to_resources(df, "data_files.interim", "data_internal_representation.csv")

    return df


def write_data_frame_to_resources(df: pd.DataFrame, package_name: str, file_name: str) -> None:  # TODO doc
    """
    Write the specified DataFrame to the specified Path.

     Writing into resources is not good style, let's do it here to ease program access.

    :param df: Instance of DataFrame to write
    :param package_name: Name of the package to write to
    :param file_name: File name to use
    :return: None
    :raises OSErrror: If something went wrong during writing
    """

    path = resources.path(package_name, file_name)
    try:
        df.to_csv(path.as_posix(), index=False)
    except OSError:
        print(f"Failed to write DataFrame to {path}.")
        raise
    else:
        print(f"Successfully wrote DataFrame to {path}.")
