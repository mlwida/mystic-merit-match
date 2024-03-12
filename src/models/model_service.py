"""
Provides methods to train, load and access a Model to make match predictions.
"""

import importlib.resources as resources
import time

import pandas as pd
import skops.io as sio
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from data.data_io import read_and_prepare_raw_data
from data.data_io import write_data_frame_to_resources
from data.data_types import Job
from data.data_types import Talent
from features.feature_extraction import FeatureExtractorManager


class Model:
    """
    An interface to access a trained model
    """

    def predict(self, talent_raw: dict, job_raw: dict) -> dict:
        """
        Predicts a label and confidence for the combination of job and talent, each represented by raw json input data
        :param self: the model object
        :param talent_raw: json-dictionary represent a talent as seen in the raw input data
        :param job_raw: json-dictionary represent a job as seen in the raw input data
        :return: dict with talent and job (unchanged) along with label and score / confidence
        """
        pass

    def predict_bulk(self, talents_raw: list[dict], jobs_raw: list[dict]) -> list[dict]:
        """
        Predicts a label and confidence for each combination of job and talent, each represented by raw json input data
        :param self: the model object
        :param talents_raw: list of json-dictionaries represent a talent as seen in the raw input data
        :param jobs_raw: list of json-dictionaries represent a job as seen in the raw input data
        :return: list of dictionaries with talent and job (unchanged) along with label and score
        """
        pass


class MysticMeritModel(Model):
    """
    Simple implementation of Model including data preprocessing before prediction.
    """

    def __init__(self, classifier: BaseEstimator) -> None:
        """
        Initialize an object of MysticMeritModel.
        :param classifer: binary classifier trained on tabular data to use internally
        """
        self.classifier = classifier
        pass

    def predict(self, talent_raw: dict, job_raw: dict) -> dict:
        """
        Predicts a label and confidence for the combination of job and talent, each represented by raw json input data.

        The resulting list of dictionaries is sorted by score in descending order.

        :param self: the model object
        :param talent_raw: json-dictionary represent a talent as seen in the raw input data
        :param job_raw: json-dictionary represent a job as seen in the raw input data
        :return: dict with talent and job (unchanged) along with label and score
        """
        talent = Talent.create(talent_raw)
        job = Job.create(job_raw)

        feature_extractor = FeatureExtractorManager()
        df_app = pd.DataFrame([feature_extractor.extract_features(talent, job)])

        # predict_proba is not defined in BaseEstimator ... example of duck typing approach in scikit-learn
        predict_prob = self.classifier.predict_proba(df_app)[0]
        classes = self.classifier.classes_
        confidence_per_class = {classes[index]: predict_prob[index] for index in range(0, len(classes))}

        prediction = self.classifier.predict(df_app)[0]
        confidence = confidence_per_class.get(prediction)

        return {
            "talent": talent_raw,
            "job": job_raw,
            "label": prediction,
            "score": confidence
        }

    def predict_bulk(self, talents_raw: list[dict], jobs_raw: list[dict]) -> list[dict]:
        """
        Predicts a label and confidence for each combination of job and talent, each represented by raw json input data.

        The resulting list of dictionaries is sorted by score in descending order.

        :param self: the model object
        :param talents_raw: list of json-dictionaries represent a talent as seen in the raw input data
        :param jobs_raw: list of json-dictionaries represent a job as seen in the raw input data
        :return: list of dictionaries with talent and job (unchanged) along with label and score
        """
        result = []
        for talent_raw in talents_raw:
            for job_raw in jobs_raw:
                result.append(self.predict(talent_raw, job_raw))

        return sorted(result, key=lambda entry: entry["score"], reverse=True)

    def __repr__(self) -> str:
        return f"MysticMeritModel({self.classifier.__repr__()})"


MODEL_FILE_NAME = "matching_model.skops"


def train_and_save_model() -> None:
    """
    Trains and saves a machine learning model based on internally specified data sources.

    1. Read the raw data and create an internal representation

    2. Extracts tabular features

    3. Learns model based on these features

    :raises OSError: If something went wrong during saving of the model
    """
    print(f"Start model training ...")
    start_time = time.time()

    raw_data = read_and_prepare_raw_data(drop_source=True, write_interim_data=True)

    # Note: In the next step it would be better to store the state of FeatureExtractor along with the model
    feature_extractor = FeatureExtractorManager()
    df = pd.DataFrame(list(raw_data.apply(
        lambda row: feature_extractor.extract_features(talent=row["talent"], job=row["job"]), 1)))
    # reattach label
    df["label"] = raw_data["label"]
    write_data_frame_to_resources(df, "data_files.processed", "data_final.csv")

    # shuffle rows. Should not matter, but I always get an icky feeling when seeing sorting by label
    df = df.sample(frac=1)

    df_without_label = df.loc[:, df.columns != 'label']
    clf = RandomForestClassifier()
    scores = cross_val_score(clf, df_without_label, df["label"], cv=10, scoring='accuracy')
    print(f"Model quality based on validation: "
          f"{scores.mean():.2%} accuracy with a standard deviation of {scores.std():.2%}")
    clf.fit(df_without_label, df["label"])

    model_as_bytes = sio.dumps(clf)
    # Writing into resources is not good style, let's do it here to ease program access
    path = resources.path("model_files", MODEL_FILE_NAME)
    try:
        with open(path.as_posix(), "wb") as file:
            file.write(model_as_bytes)
    except OSError:
        print(f"Failed to write model to {path}.")
        raise
    else:
        print(f"Successfully saved model to {path}.")
    print(f"Finished model training, took ~ {round(time.time() - start_time)} seconds.")


def load_model() -> Model:
    """
    Load the model from the model repository
    :return: instance of model is available
    :raises OSError: If loading was not possible
    """
    path = resources.path("model_files", MODEL_FILE_NAME)
    try:
        with open(path, "rb") as file:
            model_as_bytes = file.read()
            model = MysticMeritModel(sio.loads(model_as_bytes, trusted=True))
    except OSError:
        print(f"Failed to read the model from {path}. Maybe it has not been trained yet.")
        raise
    else:
        print(f"Successfully read the model from {path}")
    return model
