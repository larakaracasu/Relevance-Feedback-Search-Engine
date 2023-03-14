# Relevance Feedback Search Engine

![](https://img.shields.io/github/license/ulasonat/relevance-feedback-search-engine?color=red&logo=red&style=flat-square)

This is a Python program that acts as a search engine using the Google Custom Search API. The program takes in a query and a precision, and returns a list of Google search results. It then prompts the user to mark the relevant documents and uses a feedback mechanism to perform a refined search. The program calculates the running sum of the relevant and non-relevant documents and uses a modified Rocchio algorithm to augment the query to improve its performance.

## Algorithms Executed

The program uses the following algorithms:

### Precision Evaluation

Precision refers to the fraction of relevant documents returned by the search engine divided by the total number of documents returned. The program computes the precision value and stops if the precision value is above the given precision threshold.

### Rocchio's Algorithm

The Rocchio's algorithm is an algorithm for relevance feedback in information retrieval. It is a modified version of the k-nearest neighbors algorithm that uses weighted sums to improve the search results. Given the user’s feedback on relevant and non-relevant documents, the program first calculates the running sum of relevant and non-relevant documents, respectively. It then uses the Rocchio algorithm to compute the final vector representation of the query.

### Order Generator

The order generator algorithm generates all possible orders of the query terms and picks the order that has the highest count of n-grams in the relevant documents.

## Dependencies

- `sklearn`
- `itertools`
- `googleapiclient`
- `pprint`
- `html`

## Usage

The program can be run from the terminal using the following command:

```python
python3 search_engine.py <API_Key> <Engine_Key> <Precision> <Query>
```
- `<API_Key>`: Your Google API Key
- `<Engine_Key>`: Your Google Engine Key
- `<Precision>`: The desired precision value
- `<Query>`: The search query

### Examples

```python
# Running the program with API Key, Engine Key, precision value of 0.8 and search query "artificial intelligence"
python3 search_engine.py your_api_key your_engine_key 0.8 "artificial intelligence"
```
The program will print search results and will prompt the user to enter feedback by marking the results as relevant (Y) or non-relevant (N). The program will use this feedback to refine the search query by selecting the top two relevant terms and generating a new query. The final search result will be displayed once the desired precision is achieved.
