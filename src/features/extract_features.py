from data.data_types import Talent
from data.data_types import Job
from data.data_types import Language
import pandas as pd

NUMERICAL_LEVEL_PER_LANGUAGE = {"A1":1}


def numerical_level_for_language(language: Language) -> int:
    pass


def extract_features(talent: Talent, job: Job) -> pd.DataFrame:
    pass


# TODO continue
def extract_features_for_multiple_combinations(talents: list[Talent], jobs: list[Job]) -> pd.DataFrame:
    pass
