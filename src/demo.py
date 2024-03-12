from data.data_io import read_raw_data
from models.model_service import train_and_save_model
from search import Search


def pretty_printing_search_result(result: dict) -> str:
    """
    Pretty prints the result of matching calls to an instance of Search.
    
    :param result: Result of a matching call to an instance of Search
    :return: pretty printed string representation of the result
    """
    print("\n######################################\n# Search Results \n######################################")
    counter = 1
    for entry in result:
        formatted_map = '\n'.join([f'{k}:{v}' for k, v in entry.items()])
        print(f"Entry {counter}\n{formatted_map}\n")
        counter += 1


# load raw data, preprocess and save data in two stages and finally train and save the model
train_and_save_model()

# init an instance of Search
search = Search()

# No let's play around ...
raw_data = read_raw_data()
raw_data = raw_data.drop(columns="label")
# shuffle
raw_data = raw_data.sample(frac=1)

single_search_result = [search.match(raw_data.iloc[0]["talent"], raw_data.iloc[0]["job"])]
pretty_printing_search_result(single_search_result)

bulk_search_result = search.match_bulk([raw_data.iloc[0]["talent"], raw_data.iloc[1]["talent"]],
                                       [raw_data.iloc[0]["job"], raw_data.iloc[1]["job"]])
pretty_printing_search_result(bulk_search_result)
