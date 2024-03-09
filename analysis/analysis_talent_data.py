import pandas as pd
from data import data_ingestion

# Hacky script for quick manual analysis, hence no docs here

df = data_ingestion.read_raw_data()
data_ingestion.parse_talent(df)
talent_df = pd.DataFrame({"talent": df["talent_parsed"]})


def flatten_list(list_of_lists):
    return [item for single_list in list_of_lists for item in single_list]


def analyse_roles(talent_df):
    print("Check job_roles")
    values = flatten_list(talent_df.apply(lambda row: row["talent"].job_roles, 1))
    print(pd.Series(values).sort_values().unique())


def analyse_languages(job_df):
    print("Check languages")
    languages = flatten_list(job_df.apply(lambda row: list(row["talent"].languages.keys()), 1))
    print(pd.Series(languages).sort_values().unique())
    print("Check language ratings")
    ratings = flatten_list(job_df.apply(lambda row: [language.rating for language in row["talent"].languages.values()], 1))
    print(pd.Series(ratings).sort_values().unique())


# check properties
analyse_roles(talent_df)
analyse_languages(talent_df)

talent_df["seniority"] = talent_df.apply(lambda row: row["talent"].seniority, 1)
print(f"Seniority\n:{talent_df['seniority'].sort_values().unique()}")
talent_df["degree"] = talent_df.apply(lambda row: row["talent"].degree, 1)
print(f"Degree:\n{talent_df['degree'].sort_values().unique()}")
talent_df["salary_expectation"] = talent_df.apply(lambda row: row["talent"].salary_expectation, 1)
print(f"Salary:\n{talent_df.salary_expectation.describe()}")
