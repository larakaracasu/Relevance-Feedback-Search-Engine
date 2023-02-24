import sys
import pprint
import html
from sklearn.feature_extraction.text import CountVectorizer
import itertools
from googleapiclient.discovery import build


def badPrecisionInput(precision):
    # Validates the precision input, returns true if it cannot be converted to float
    try:
        float(precision)
        return False
    except ValueError:
        return True


def htmlProcessing(htmlObject, html_tags_final, stop_words, lexicon):
    # Creates a lexicon by processing HTML objects like title and snippet,
    for term in htmlObject:
        if len(term) > 0 and term[0] == '&': # continue if it's HTML entity
            continue
        for tag in html_tags_final:
            if tag in term.lower():
                term = term.replace(tag, '') # we're removing the HTML tags from the words in html
        term = ''.join(letter for letter in term if letter.isalnum()) # only keeping the alphanumeric terms
        if term.lower() not in stop_words and term.lower() != '': # only add it to lexicon if it's not a stop word or empty word
            lexicon[term.lower()] = 0


def relevanceVectorSummation(document, html_tags_final, relevant, stop_words, relevant_running_sum,
                             nonrelevant_running_sum):
    # This function calculates the running sum of relevant and nonrelevant returns the words from relevant documents
    relevant_doc_string = ''
    for term in document:
        if len(term) > 0 and term[0] == '&': # skipping the HTML entities again
            continue
        for tag in html_tags_final:
            if tag in term.lower():
                term = term.replace(tag, '')
        term = ''.join(letter for letter in term if letter.isalnum())
        if term.lower() != '' and relevant.lower() == "y":
            relevant_doc_string += term + " "
        if term.lower() not in stop_words and term.lower() != '':
            if relevant.lower() == "y":
                relevant_running_sum[term.lower()] += 1  # adding it to relevant running sum
            elif relevant.lower() == "n":
                nonrelevant_running_sum[term.lower()] += 1 # adding it to nonrelevant running sum
    return relevant_doc_string


def orderGenerator(query, relevant_doc_list):
    # Generates all orders of the query terms, which then picks the order with the highest ngrams
    engine_vectorizer = CountVectorizer(ngram_range=(1, 3))  # transforming into vector space
    engine_vectorizer.fit_transform(relevant_doc_list)
    query_order = list(itertools.permutations(query))
    ngrams = []
    for order in query_order: # computing the each ngram for each order
        string_order = ' '.join(order) # combining the query terms into a string
        transformed = engine_vectorizer.transform([string_order])
        ngrams.append(transformed)
    ngrams_count = []
    for ngram in ngrams: # computing the count of n-grams in each order
        ngrams_count.append(ngram.toarray()[0])
    order_count = []
    for count in ngrams_count:
        order_count.append(sum(count))
    best_order_idx = order_count.index(max(order_count))  # get the order
    query = list(query_order[best_order_idx])  # converting it to list, otherwise it will be a tuple
    return query


def main():
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.

    # reading in the stop words and html tags from the respective txt files
    with open('stop_word.txt') as stop_words_file:
        stop_words = [stop_word.strip() for stop_word in stop_words_file]

    with open('html_tags.txt') as html_tags_file:
        html_tags = [html_tag.strip() for html_tag in html_tags_file]

    html_tags_open = ["<" + html_tag + ">" for html_tag in html_tags]
    html_tags_close = ["</" + html_tag + ">" for html_tag in html_tags]
    html_tags_final = html_tags_open + html_tags_close

    # parsing the command-line arguments
    if len(sys.argv) != 5 or badPrecisionInput(sys.argv[3]):
        print("Usage: python3 search_engine.py <API Key> <Engine Key> <Precision> <Query>\n")
        return

    developerKey = sys.argv[1]
    cx = sys.argv[2]
    precision = float(sys.argv[3])
    query = sys.argv[4]

    # Accessing Google API
    service = build(
        "customsearch", "v1", developerKey=developerKey
    )

    lexicon = dict()
    #query = query.split(" ")
    query_list = query.split(" ")
    for term in query_list:
        lexicon[term.lower()] = 0
        if term.lower() in stop_words:
            stop_words.remove(term.lower()) # if a query term is one the stop words, we exclude it from the stop words

    while True:
    # our main loop here

        res = (
            service.cse()
            .list(
                q=query,
                cx=cx,
            )
            .execute())
        
        query = query_list
        # printing the parameters
        print("Parameters:\nClient key: ", developerKey, "\nEngine key: ", cx, "\nQuery: ", ' '.join(query),
              '\nPrecision: ', str(precision))
        print("\nGoogle Search Results:" + "\n" + "======================")

        current_precision = 0.0

        # if there's less than 10 results (including 0), we simply terminate the program, as per the requirements
        if int(res['searchInformation']['totalResults']) < 10:
            print('Number of results found is less than 10, terminating the program...')
            return

        for i, item in enumerate(res["items"]): # looping the results

            if "fileFormat" in item: # we are skipping if the format is not HTML
                continue

            formattedUrl = item["formattedUrl"]
            htmlTitle = item["htmlTitle"]
            htmlSnippet = item["htmlSnippet"]

            htmlTitle = htmlTitle.split(" ")
            htmlSnippet = htmlSnippet.split(" ")

            # removing the stop words and HTML tags from the title and snippet
            htmlProcessing(htmlTitle, html_tags_final, stop_words, lexicon)
            htmlProcessing(htmlSnippet, html_tags_final, stop_words, lexicon)

        query_vector = lexicon.copy() # a vector representation of the query
        for word in query:
            query_vector[word] += 1

        # having counters below for the number of relevant and nonrelevant documents
        relevant_doc_count = 0
        relevant_running_sum = lexicon.copy()
        nonrelevant_doc_count = 0
        nonrelevant_running_sum = lexicon.copy()
        relevant_doc_list = []

        for i, item in enumerate(res["items"]):

            formattedUrl = item["formattedUrl"]
            htmlTitle = item["htmlTitle"]
            htmlSnippet = item["htmlSnippet"]

            for tag in html_tags_final: # removing HTML tags
                if tag in htmlTitle:
                    htmlTitle = htmlTitle.replace(tag, '')
                if tag in htmlSnippet:
                    htmlSnippet = htmlSnippet.replace(tag, '')

            # printing the results
            print("\n")
            print("Result " + str(i + 1))
            print(html.unescape("URL: " + formattedUrl))
            print(html.unescape("Title: " + htmlTitle))
            print(html.unescape("Summary: " + htmlSnippet + "\n"))

            htmlTitle = htmlTitle.split(" ")
            htmlSnippet = htmlSnippet.split(" ")
            document = htmlTitle + htmlSnippet

            if "fileFormat" in item: # skipping if it's not an HTML file, won't progress through the result
                print('This is a NON-HTML file, not getting an input, progressing...')
                continue

            relevant = input(f"Relevant (Y/N)? ")

            while (relevant.lower() not in ["y", "n"]): # gets the input until it is valid
                relevant = input(f"Your input was not 'Y' or 'N'. Enter again: ")
            if relevant.lower() == "y":
                current_precision += 1
                relevant_doc_count += 1
            elif relevant.lower() == "n":
                nonrelevant_doc_count += 1

            relevant_doc_string = relevanceVectorSummation(document, html_tags_final, relevant, stop_words,
                                                           relevant_running_sum, nonrelevant_running_sum)

            if relevant_doc_string != '':
                relevant_doc_list.append(relevant_doc_string)

        num_of_html_files = relevant_doc_count + nonrelevant_doc_count
        current_precision /= num_of_html_files # we calculate it this way, so non-html files won't have any effect

        if current_precision >= precision: # the precision is reached
            break

        if relevant_doc_count == 0: # terminate if all of them are nonrelevant
            return

        beta = 0.75
        gamma = 0.15  # from "Relevance Feedback in Information Retrieval", 1983

        final_vector = query_vector.copy()

        for key, value in relevant_running_sum.items():
            relevant_running_sum[key] /= relevant_doc_count
            final_vector[key] += beta * relevant_running_sum[key] # executing the algorithm

        for key, value in nonrelevant_running_sum.items():
            nonrelevant_running_sum[key] /= nonrelevant_doc_count
            final_vector[key] -= gamma * nonrelevant_running_sum[key]
            if final_vector[key] < 0: # if it goes to negative, we set it back to 0
                final_vector[key] = 0

        # final_list = [(val, key) for key, val in final_vector.items() if key not in query]

        # for terms that are not in the query, we create a list of tuples to represent the weight and the word.
        final_list = []
        for key, val in final_vector.items():
            if key not in query:
                final_list.append((val, key))

        final_list.sort(reverse=True) # sorting in reverse order of weights
        top_term_key = final_list[0][1]
        second_term_key = final_list[1][1]

        print("\nFEEDBACK SUMMARY\n", "\nQuery: ", ' '.join(query), "\nPrecision: ", current_precision,
              "\nStill below the desired precision of ", precision, "\nIndexing results...\n", "Augmenting by ",
              top_term_key, second_term_key)

        # we append the top two key to the query
        query.append(top_term_key)
        query.append(second_term_key)
        query = orderGenerator(query, relevant_doc_list) # and call the order generator to decide on the ordering
        query_string = " ".join(query)

if __name__ == "__main__":
    main()
