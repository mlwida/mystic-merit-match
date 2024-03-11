import pandas as pd
from data import data_ingestion

# Hacky script for quick manual analysis, hence no docs here

df = data_ingestion.read_raw_data()
data_ingestion.parse_job(df)
job_df = pd.DataFrame({"job": df["job_parsed"]})


def flatten_list(list_of_lists):
    return [item for single_list in list_of_lists for item in single_list]


def analyse_list_field(job_df, field_name):
    print(f"Check {field_name}")
    list_of_lists = job_df.apply(lambda row: row["job"].__getattribute__(field_name), 1)
    print(f"Missing :{len([l for l in list_of_lists if not l])}")
    values = flatten_list(list_of_lists)
    print(pd.Series(values).sort_values().unique())


def analyse_languages(job_df):
    print("Check languages")
    list_of_lists = job_df.apply(lambda row: list(row["job"].languages.keys()), 1)
    languages = flatten_list(list_of_lists)
    print(f"Jobs with missing languages :{len([l for l in list_of_lists if not l])}")
    print(pd.Series(languages).sort_values().unique())
    print("Check language ratings")
    ratings = flatten_list(job_df.apply(lambda row: [language.rating for language in row["job"].languages.values()], 1))
    print(pd.Series(ratings).sort_values().unique())


# check properties
analyse_list_field(job_df, "job_roles")
analyse_languages(job_df)
analyse_list_field(job_df, "seniorities")

job_df["min_degree"] = job_df.apply(lambda row: row["job"].min_degree, 1)
print(f"Min degree\n"
      f"Missing:{pd.isna(job_df['min_degree']).sum()}\n"
      f"Unique: {job_df['min_degree'].sort_values().unique()}")
job_df["max_salary"] = job_df.apply(lambda row: row["job"].max_salary, 1)
print(f"Max Salary"
      f"Missing:{pd.isna(job_df['max_salary']).sum()}\n"
      f"\n{job_df.max_salary.describe()}")

job_df["none_seniority_allowed"] = job_df.apply(lambda x: None in x["job"].seniorities, 1)
job_df["job_roles"] = job_df.apply(lambda row: row["job"].job_roles, 1)
roles_sen_none = flatten_list(job_df.loc[job_df["none_seniority_allowed"]].apply(lambda row: row["job"].job_roles, 1))
print(f"Job roles which allow seniority None: {pd.Series(roles_sen_none).sort_values().unique()}")

# Seniority in case of jobs is solely used for jobs on individual contributor level.
# Some titles include manager although being individual contributor (e.g. marketing manager)
