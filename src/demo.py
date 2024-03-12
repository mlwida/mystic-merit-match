from functools import cmp_to_key

from data.data_io import read_raw_data
from models.model_service import train_and_save_model
from search import Search


def pretty_printing_search_result(result: [dict]) -> None:
    """
    Pretty prints the result of matching calls to an instance of Search.
    
    :param result: Result of a matching call to an instance of Search
    :return: None
    """
    print("\n######################################\n# Search Results \n######################################")
    counter = 1
    for entry in result:
        formatted_map = '\n'.join([f'{k}: {v}' for k, v in entry.items()])
        print(f"Entry {counter}\n{formatted_map}\n")
        counter += 1


def alternative_sorting(result: [dict]) -> [dict]:
    """
    In Search a sorting purley by score is requested. This score is the confidence of the model in the predicted label.
    In order to see the top matches between jobs and candidates first, this function is sorting the result based on
    the confidence in the positive class a.k.a. label=True (in descending order)

    :param result: input result from a matching call to Search
    :return: result sorted based on the confidence / score for label True
    """

    def compare(e1, e2):
        score_e1 = e1["score"] if e1["label"] else 1 - e1["score"]
        score_e2 = e2["score"] if e2["label"] else 1 - e2["score"]
        return score_e2 - score_e1

    return sorted(result, key=cmp_to_key(compare))


# load raw data, preprocess and save data in two stages and finally train and save the model
train_and_save_model()

# init an instance of Search
search = Search()

# No let's play around ...
raw_data = read_raw_data()
raw_data = raw_data.drop(columns="label")

single_search_result = [search.match(raw_data.iloc[0]["talent"], raw_data.iloc[0]["job"])]
pretty_printing_search_result(single_search_result)

bulk_search_result = search.match_bulk([raw_data.iloc[0]["talent"], raw_data.iloc[1001]["talent"]],
                                       [raw_data.iloc[0]["job"], raw_data.iloc[1001]["job"]])
pretty_printing_search_result(bulk_search_result)

print("\n---------------------------------------------------------------------------------------------------------\n")
print("Here is the same result, but sorted based on the confidence in the positive class, "
      "i.e. top matches at the start !\n")
bulk_search_result_alt = alternative_sorting(bulk_search_result)
pretty_printing_search_result(bulk_search_result_alt)
