"""

This module provides methods for feature extraction for a combination of Talent and Job.

Convention for feature names: If a feature is calculated based on a ...
* talent property, it gets a t-prefix
* job property, it gets a j-prefix
* combination of talent and job property, it gets a tj-prefix

Also note:
* Due to the restrictions on machine learning libraries, only numerical features will be returned.
* Assignment data set has only 1000 observations per label. So it is very difficult for the machine learning algo
 to learn if we got too many features, so one-hot-encoding is not used.

"""

from pandas import DataFrame as DataFrame

from data.data_types import Job
from data.data_types import Talent

# This ordinal encoding does not represent a ground truth, especially not the differences or ratio.
# These values are approximate enough (IMHO), so that a machine learning model may make use of it.
# Example: C2 "-" B1 "=" 3 "=" B2 "-" A1 = 3. During model training will see if this number is useful or not.
# None handling may vary.
NUMERICAL_LEVEL_PER_LANGUAGE_RATING = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
NUMERICAL_LEVEL_PER_SENIORITY = {"junior": 1, "midlevel": 2, "senior": 3}
NUMERICAL_LEVEL_PER_DEGREE = {"apprenticeship": 1, "bachelor": 2, "master": 3, "doctorate": 4}


# TODO add missing doc

# TODO move the label addition somewhere else ... or better this whole method
def prepare_feature_set(raw_data: DataFrame) -> DataFrame:
    prepared_rows = list(raw_data.apply(lambda row: extract_features(talent=row["talent"], job=row["job"]), 1))
    prepared_df = DataFrame(prepared_rows)
    prepared_df["label"] = raw_data["label"]
    return prepared_df


# TODO continue here
def extract_features_for_multiple_combinations(talents: list[Talent], jobs: list[Job]) -> DataFrame:
    pass


def extract_features(talent: Talent, job: Job) -> dict:
    row = {}
    # These single methods calls can be abstracted by interfaces ((talent,job) -> dict)
    # and be managed by a factory module
    # This way it can be individually calculated (in parallel !) and tested.
    # For this assignment it feels like over-engineering
    # Each method calculates multiple features to avoid duplicate computations
    row.update(extract_features_about_seniority(talent, job))
    row.update(extract_features_about_degree(talent, job))
    row.update(extract_features_about_salary(talent, job))
    row.update(extract_features_about_roles(talent, job))

    # Tried various strategies for language, but none did improve the accuracy, so skip
    #row.update(extract_features_about_languages(talent, job))
    return row


def extract_features_about_seniority(talent: Talent, job: Job) -> dict:
    row = {}
    # Analysis has shown, that for seniority None ...
    # * ... talents desire lead, head but also IC roles. May mean they see themselves in a higher position or forgot.
    # * ... jobs with None in the list only aim at job roles on IC level. May mean they don't care about seniority.
    # None ur unknown in NUMERICAL_LEVEL_PER_SENIORITY is treated as 0

    row["t_seniority_missing"] = 1 if talent.seniority is None else 0
    row["t_seniority"] = NUMERICAL_LEVEL_PER_SENIORITY.get(talent.seniority, 0)
    seniority_num_values = [NUMERICAL_LEVEL_PER_SENIORITY.get(job_sen, 0) for job_sen in job.seniorities]
    row["j_min_seniority"] = min(seniority_num_values)
    row["j_max_seniority"] = max(seniority_num_values)
    if row["j_min_seniority"] <= row["t_seniority"] <= row["j_max_seniority"]:
        # Read min diff is 0, perfect match
        row["tj_diff_seniority"] = 0
    else:
        # negative if tenant is under-qualified, else if overqualified (module None occurrences)
        row["tj_diff_seniority"] = row["t_seniority"] - row["j_min_seniority"]
    return row


def extract_features_about_degree(talent: Talent, job: Job) -> dict:
    row = {}
    # None ur unknown in NUMERICAL_LEVEL_PER_DEGREE is treated as 0
    row["t_degree"] = NUMERICAL_LEVEL_PER_DEGREE.get(talent.degree, 0)
    row["j_degree"] = NUMERICAL_LEVEL_PER_DEGREE.get(job.min_degree, 0)
    # negative if tenant is under-qualified, else if overqualified (module None occurrences)
    row["tj_diff_degree"] = row["t_degree"] - row["j_degree"]

    return row


def extract_features_about_salary(talent: Talent, job: Job) -> dict:
    # negative if expected salary is above job max salary, else positive
    # normalized by max_salary to represent a percentage. +1 to avoid diff by zero
    row = {"tf_salary_diff": (job.max_salary - talent.salary_expectation + 1) / (job.max_salary + 1)}
    return row


def extract_features_about_roles(talent: Talent, job: Job) -> dict:
    row = {}
    # 1 is "role match", 0 otherwise. Without a curated taxonomy (and more observations)
    # we would have to perform some more sophisticated natural language processing methods
    match = 0
    for desired_role in talent.job_roles:
        if desired_role in job.job_roles:
            match = 1
            break

    row["tf_role_match"] = match
    return row


def extract_features_about_languages(talent: Talent, job: Job) -> dict:
    # Not analyzed ... native German speakers without explicit certificate have C2 ?
    sum_lang_importance = 0
    sum_lang_diff = 0
    for job_language in job.languages.values():
        if job_language.must_have:
            sum_lang_importance += 1
            job_rating = NUMERICAL_LEVEL_PER_LANGUAGE_RATING.get(job_language.rating, 0)
            candidate_rating = 0

            talent_language = talent.languages.get(job_language.title, None)
            if talent_language is not None:
                candidate_rating = NUMERICAL_LEVEL_PER_LANGUAGE_RATING.get(talent_language.rating, 0)
            # if positive, then the candidate has more language capabilities than requested, else negative
            sum_lang_diff += (candidate_rating - job_rating)
            if candidate_rating >= job_rating:
                match = 1

    row = {"j_lang_importance": sum_lang_importance,
           "tj_lang_avg_diff": sum_lang_diff / sum_lang_importance if sum_lang_importance > 0 else 0}
    return row
