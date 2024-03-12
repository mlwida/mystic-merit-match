# mystic-merit-match

To enter the circle of those who are searching for the best code and data wizards, you have to go on a quest to prove that your merits are true. 

## Overview

1. Job and talent in raw data is read and each represented by a separate class (**data_io.py**)
2. Based on the still unstructured classes Job and Talent tabular features are extracted (**feature_extraction.py**)
3. Based on this tabular data a plain Random Forest model is trained and checked with crossvalidation. (**model_service.py**)
4. Most of the work for the model application is done in the model classes (also **model_service.py**)

Checkout **feature_extraction.py** for the detailed feature engineering strategy.

For playing around I recommend **demo.py**

## How to install

```
virtualenv .venv
source .venv/bin/activate
python -m pip install .
```

For the used specific package versions check _requirements.txt_.

## More

Project layout inspired by [Cookie Cutter](https://drivendata.github.io/cookiecutter-data-science/)