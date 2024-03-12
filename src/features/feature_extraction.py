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

from data.data_types import Job
from data.data_types import Talent

# This ordinal encoding does not represent a ground truth, especially not the differences or ratio.
# These values are approximate enough (IMHO), so that a machine learning model may make use of it.
# Example: C2 "-" B1 "=" 3 "=" B2 "-" A1 = 3. During model training will see if this number is useful or not.
# None handling may vary.
NUMERICAL_LEVEL_PER_LANGUAGE_RATING = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
NUMERICAL_LEVEL_PER_SENIORITY = {"junior": 1, "midlevel": 2, "senior": 3}
NUMERICAL_LEVEL_PER_DEGREE = {"apprenticeship": 1, "bachelor": 2, "master": 3, "doctorate": 4}


class FeatureExtractor:
    """
    A feature extractor extracts tabular features (columns) from a combination of Talent and Job, hence transforming
    unstructured into tabular data.
    """

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features for the given Talent and Job
        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
        pass


class FeatureExtractorManager(FeatureExtractor):
    """
    A class representing a collector for multiple FeatureExtractors for easier access.
    """

    def __init__(self):
        """
        Init an object of FeatureExtractorManager by registering the default FeatureExtractor instances.
        """
        self.extractors = []
        self.register(SeniorityFeatureExtractor())
        self.register(DegreeFeatureExtractor())
        self.register(SalaryFeatureExtractor())
        self.register(JobRolesFeatureExtractor())
        self.register(LanguageFeatureExtractor())

    def register(self, extractor: FeatureExtractor) -> None:
        """
        Register the specified extractor.
        :param extractor: Instance of FeatureExtractor to register
        :return: None
        """
        self.extractors.append(extractor)

    def clear(self) -> None:
        """
        Clear the registered instance of FeatureExtractor.
        :return: None
        """
        self.extractors = []

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features for the given Talent and Job by calling all registered instances of FeatureExtractor
        in order of registration.

        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
        row = {}
        # Note: Calls to these instances could be executed in parallel, because they are independent of each other
        for feature_extractor in self.extractors:
            row.update(feature_extractor.extract_features(talent, job))
        return row


class SeniorityFeatureExtractor(FeatureExtractor):
    """
    Class representing an extractor for features about seniority.
    """

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features about seniority matching for the given Talent and Job.

        Extracted features:

        * t_seniority_missing: If the seniority is missing for the talent
        * t_seniority: Numerical representation of the talent's seniority if available, else 0
        * j_min_seniority: Minimum of the numerical representations of the job's seniorities. None treated as 0.
        * j_max_seniority: Maximum of the numerical representations of the job's seniorities. None treated as 0.
        * tj_diff_seniority: t_seniority-j_min_seniority if no match, else 0

        Analysis has shown, that for seniority None ...

        * ... talents desire lead, head but also IC roles. May mean they see themselves in a higher position or forgot.
        * ... jobs with None in the list only aim at job roles on IC level. May mean they don't care about seniority.

        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
        row = {}
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


class DegreeFeatureExtractor(FeatureExtractor):
    """
    Class representing an extractor for features about degree.
    """

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features about degree matching for the given Talent and Job.

        Extracted features:

        * t_degree: Numerical representation of the talent's degree if available, else 0
        * j_degree: Numerical representation of the job's minimum degree if available, else 0
        * tj_diff_degree: t_degree-j_degree

        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
        row = {}
        row["t_degree"] = NUMERICAL_LEVEL_PER_DEGREE.get(talent.degree, 0)
        row["j_degree"] = NUMERICAL_LEVEL_PER_DEGREE.get(job.min_degree, 0)
        # negative if tenant is under-qualified, else if overqualified (module None occurrences)
        row["tj_diff_degree"] = row["t_degree"] - row["j_degree"]

        return row


class SalaryFeatureExtractor(FeatureExtractor):
    """
    Class representing an extractor for features about salary.
    """

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features about salary matching for the given Talent and Job.

        Extracted features:

        * tf_salary_diff: job's max salary - talent's salary expectation, normalized by job's max salary

        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
        # negative if expected salary is above job max salary, else positive
        # normalized by max_salary to represent a percentage. +1 to avoid diff by zero
        row = {"tf_salary_diff": (job.max_salary - talent.salary_expectation + 1) / (job.max_salary + 1)}
        return row


class JobRolesFeatureExtractor(FeatureExtractor):
    """
    Class representing an extractor for features about job roles.
    """

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features about job roles matching for the given Talent and Job.

        Extracted features:

        * tf_role_match: 1 if the talent's desired roles overlap with the job's target roles, else 0.

        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
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


class LanguageFeatureExtractor(FeatureExtractor):
    """
    Class representing an extractor for features about languages and their ratings.
    """

    def extract_features(self, talent: Talent, job: Job) -> dict:
        """
        Extract a row with features about language (rating) matching for the given Talent and Job.

        Extracted features:

        * j_lang_importance: Number of job's must-have languages.
        * tj_lang_avg_diff: Average difference between job's must-have language ratings and the candidates skills

        :param talent: Talent object
        :param job: Job object
        :return: dictionary with value per feature name
        """
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
