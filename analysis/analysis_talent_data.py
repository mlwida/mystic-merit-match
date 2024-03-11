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
    list_of_lists = talent_df.apply(lambda row: row["talent"].job_roles, 1)
    print(f"Talents with missing roles :{len([l for l in list_of_lists if not l])}")
    values = flatten_list(list_of_lists)
    print(pd.Series(values).sort_values().unique())


def analyse_languages(talent_df):
    print("Check languages")
    list_of_lists = talent_df.apply(lambda row: list(row["talent"].languages.keys()), 1)
    languages = flatten_list(list_of_lists)
    print(f"Talents with missing languages :{len([l for l in list_of_lists if not l])}")
    print(pd.Series(languages).sort_values().unique())
    print("Check language ratings")
    ratings = flatten_list(
        talent_df.apply(lambda row: [language.rating for language in row["talent"].languages.values()], 1))
    print(pd.Series(ratings).sort_values().unique())


# check properties
analyse_roles(talent_df)
analyse_languages(talent_df)

talent_df["seniority"] = talent_df.apply(lambda row: row["talent"].seniority, 1)
print(f"Seniority\n"
      f"Missing: {pd.isna(talent_df['seniority']).sum()}\n"
      f"Unique: {talent_df['seniority'].sort_values().unique()}")
talent_df["degree"] = talent_df.apply(lambda row: row["talent"].degree, 1)
print(f"Degree\n"
      f"Missing: {pd.isna(talent_df['degree']).sum()}\n"
      f"Unique: {talent_df['degree'].sort_values().unique()}")
talent_df["salary_expectation"] = talent_df.apply(lambda row: row["talent"].salary_expectation, 1)
print(f"Salary\n"
      f"Missing: {pd.isna(talent_df['salary_expectation']).sum()}\n"
      f"\n{talent_df.salary_expectation.describe()}")

###
talent_df["job_roles"] = talent_df.apply(lambda row: row["talent"].job_roles, 1)
values = flatten_list(talent_df.loc[pd.isna(talent_df["seniority"])].apply(lambda row: row["talent"].job_roles, 1))
print(f"Desired roles with own seniority None: {pd.Series(values).sort_values().unique()}")

# Seniority here can represent actual managers (lead, head)
# AND is also applied to jobs on individual contributor level
# => so None may mean "other values do not apply" , "higher-ranked" and probably "Choose to not specify"
