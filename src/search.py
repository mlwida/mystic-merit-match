import models.model_service


class Search:
    """
    Class representing a lightweight search component to search for matches between jobs and talents / candidates.
    """

    def __init__(self) -> None:
        """
        Initialize an object of Search by loading the internally used model.
        """
        self.model = models.model_service.load_model()

    def match(self, talent: dict, job: dict) -> dict:
        """
        Calculates the prediction of being a match for a given talent and job.

        The returned score is a representation of the model's confidence in the predicted label.

        :param talent: raw json dictionary representing a talent
        :param job: raw json dictionary representing a job
        :return: dictionary with unchanged talent and job plus a predicted 'label' along with a 'score'
        """
        # ==> Method description <==
        # This method takes a talent and job as input and uses the machine learning
        # model to predict the label. Together with a calculated score, the dictionary
        # returned has the following schema:
        #
        # {
        #   "talent": ...,
        #   "job": ...,
        #   "label": ...,
        #   "score": ...
        # }
        #
        return self.model.predict(talent, job)

    def match_bulk(self, talents: list[dict], jobs: list[dict]) -> list[dict]:
        """
        Calculates the prediction of being a match for all combinations of given talents and jobs.

        The returned score is a representation of the model's confidence in the predicted label.

        :param talents: list of raw json dictionaries each representing a talent
        :param jobs: list of raw json dictionaries each representing a job
        :return: list of dictionaries each with one unchanged combination plus a predicted 'label' along with a 'score'
        """
        # ==> Method description <==
        # This method takes a multiple talents and jobs as input and uses the machine
        # learning model to predict the label for each combination. Together with a
        # calculated score, the list returned (sorted descending by score!) has the
        # following schema:
        #
        # [
        #   {
        #     "talent": ...,
        #     "job": ...,
        #     "label": ...,
        #     "score": ...
        #   },
        #   {
        #     "talent": ...,
        #     "job": ...,
        #     "label": ...,
        #     "score": ...
        #   },
        #   ...
        # ]
        #
        return self.model.predict_bulk(talents, jobs)
