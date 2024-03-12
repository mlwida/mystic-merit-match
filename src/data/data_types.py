"""
Contains classes for a representation of the raw data as an intermediate step for actual feature generation.
"""


class Language:
    """
    A class representing a language skill or requirement
    """

    def __init__(self, title: str, rating: str, must_have: bool):
        """
        Initialize a new language object
        :param title: name / title of the language
        :param rating: standardized rating from A1 to C2
        :param must_have: only in context of a job
        """
        self.title = title
        self.rating = rating
        self.must_have = must_have

    def __repr__(self):
        return f"Language({self.title},{self.rating},{self.must_have})"


class Talent:
    """
    A class representing a Talent (job candidate).
    """

    def __init__(self, languages: dict[Language], job_roles: list[str], seniority: str, salary_expectation: int,
                 degree: str) -> None:
        """
        Initialize a new Talent object.

        :param languages: language skills of candidate with key = language title
        :param job_roles: interested in these job roles
        :param seniority: current level of seniority
        :param salary_expectation: expected salary for interesting jobs
        :param degree: the highest degree
        """
        # language_title: rating
        self.languages = languages
        self.job_roles = job_roles
        self.seniority = seniority
        self.salary_expectation = salary_expectation
        self.degree = degree

    @classmethod
    def create(cls, raw_json: {}) -> "Talent":
        """
        Create a new instance of Talent from raw json data.

        During generation, some minor preprocessing is performed
        * 'none' is replaced as None
        * languages are managed as a dict with key = 'language title' to ease access

        :param raw_json: json-dictionary represent a talent from the input data
        :return: instance of Talent
        """
        languages = {}
        for entry in raw_json.get("languages", []):
            title = entry.get("title", None)
            rating = entry.get("rating", None)
            if title is not None and rating is not None:
                languages[title] = Language(title, rating, False)
        seniority = raw_json.get("seniority", None)
        if seniority == "none":
            seniority = None
        degree = raw_json.get("degree", None)
        if degree == "none":
            degree = None

        return cls(languages=languages, job_roles=raw_json.get("job_roles", []),
                   seniority=seniority, salary_expectation=raw_json.get("salary_expectation", None), degree=degree)

    def __repr__(self):
        return f"Talent({self.languages},{self.job_roles},{self.seniority}," \
               f"{self.salary_expectation},{self.degree})"


class Job:
    """
    A class representing a Job.
    """

    def __init__(self, languages: dict[Language], job_roles: list[str], seniorities: list[str], max_salary: int,
                 min_degree: str) -> None:
        """
        Initialize a new Job object.

        :param languages: language requirements with key = language title
        :param job_roles: applicable job roles
        :param seniorities: applicable level of seniority
        :param max_salary: max payed salary
        :param min_degree: minimum required degree
        """
        # language_title: rating
        self.languages = languages
        self.job_roles = job_roles
        self.seniorities = seniorities
        self.max_salary = max_salary
        self.min_degree = min_degree

    @classmethod
    def create(cls, raw_json: {}) -> "Job":
        """
        Create a new instance of Job from raw json data.

        During generation, some minor preprocessing is performed
        * 'none' is replaced by None
        * languages are managed as a dict with key = 'language title' to ease access

        :param raw_json: json dictionary represent a job from the input data
        :return: instance of Job
        """
        languages = {}
        for entry in raw_json.get("languages", []):
            title = entry.get("title", None)
            rating = entry.get("rating", None)
            must_have = entry.get("must_have", False)
            if title is not None and rating is not None:
                languages[title] = Language(title, rating, must_have)

        seniorities = raw_json.get("seniorities", [])
        seniorities = [None if s == 'none' else s for s in seniorities]

        min_degree = raw_json.get("min_degree", None)
        if min_degree == "none":
            min_degree = None

        return cls(languages=languages, job_roles=raw_json.get("job_roles", []),
                   seniorities=seniorities, max_salary=raw_json.get("max_salary", None), min_degree=min_degree)

    def __repr__(self):
        return f"Job({self.languages},{self.job_roles},{self.seniorities}," \
               f"{self.max_salary},{self.min_degree})"
