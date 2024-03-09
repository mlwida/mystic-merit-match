from collections import namedtuple


# The classes feel here a little bit like overkill, because the raw json structure is not that deeply nested. It is here
# to increase code readability and have a place to define the standardized data format.
# Internal list / dict structures are kept most of the time, because this will ease processing later

class Language:

    def __init__(self, title: str, rating: str, must_have: bool):
        self.title = title
        self.rating = rating
        self.must_have = must_have

    def __repr__(self):
        return f"Language({self.title},{self.rating},{self.must_have}"


class Talent:

    def __init__(self, languages: dict[Language], job_roles: list[str], seniority: str, salary_expectation: int,
                 degree: str) -> None:
        """
        A Talent represents a potential job candidate

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
        Create a new instance from raw json data
        """
        languages = {}
        for entry in raw_json.get("languages", []):
            title = entry.get("title", None)
            rating = entry.get("rating", None)
            if title is not None and rating is not None:
                languages[title] = Language(title, rating, False)

        return cls(languages=languages, job_roles=raw_json.get("job_roles", []),
                   seniority=raw_json.get("seniority", None),
                   salary_expectation=raw_json.get("salary_expectation", None), degree=raw_json.get("degree", None))

    def __repr__(self):
        return f"Talent({self.languages},{self.job_roles},{self.seniority}," \
               f"{self.salary_expectation},{self.degree})"


class Job:

    def __init__(self, languages: dict[Language], job_roles: list[str], seniorities: list[str], max_salary: int,
                 min_degree: str) -> None:
        """
        An available job

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
        Create a new instance from raw json data
        """
        languages = {}
        for entry in raw_json.get("languages", []):
            title = entry.get("title", None)
            rating = entry.get("rating", None)
            must_have = entry.get("must_have", False)
            if title is not None and rating is not None:
                languages[title] = Language(title, rating, must_have)

        return cls(languages=languages, job_roles=raw_json.get("job_roles", []),
                   seniorities=raw_json.get("seniorities", []),
                   max_salary=raw_json.get("max_salary", None), min_degree=raw_json.get("min_degree", None))

    def __repr__(self):
        return f"Talent({self.languages},{self.job_roles},{self.seniorities}," \
               f"{self.max_salary},{self.min_dgree})"
