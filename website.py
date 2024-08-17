from dns.resolver import query
from flask import Flask,render_template,request,redirect,url_for
from pymongo import MongoClient
from flask_paginate import Pagination, get_page_args
import nltk
import requests
import pymongo
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import os
import string
import json
import random
app = Flask(__name__,template_folder='templates')
# app.debug = True

@app.route("/")
def home():
    quote = get_quote()   
    return render_template("index.html",quote=quote)

def get_quote():
	response = requests.get("https://zenquotes.io/api/random")
	json_data = json.loads(response.text)
	quote = json_data[0]['q']+ ' ---' + json_data[0]['a']
	return(quote)

def search_string_optimizations(search_string):
    # lowercasing the serch_results
    search_string = search_string.lower()

    # remove punctuations from the search_results
    translator = str.maketrans('', '', string.punctuation)
    search_string = search_string.translate(translator)

    # removing stopwords and tokenization from the search_results
    stop_words = set(stopwords.words("english"))
    word_tokens = word_tokenize(search_string)
    filtered_search_string = [
        word for word in word_tokens if word not in stop_words]

    # performing stemming in the search_results
    stemmer = PorterStemmer()
    word_tokens = word_tokenize(search_string)
    stems = [stemmer.stem(word) for word in word_tokens]
    return stems

def sort_rank(required, optimized_res):
    for result in required:
        for word in optimized_res:
            if word in result['title']:
                result['score'] += 2
            else:
                result['score'] += 0
            if word in result['description']:
                result['score'] += 1
            else:
                result['score'] += 0
    print('DONE ! DONE ! DONE')
    return sorted(required, key=lambda result: result['score'], reverse=True)

@app.route("/results/")
def result():
    client = MongoClient('localhost',27017)
    database = client.gluggle
    collection = database.queries
    search_string = request.args.get('query')
    search_history_collection = client.gluggle.search_history
    search_obj = {
        'query': search_string,
    }
    search_history_collection.insert_one(search_obj)
    optimized_res = search_string_optimizations(search_string)
    print(search_string)
    search_result = []
    required = []
    search_results = collection.find(
        {
            "$text": {
                "$search": search_string,
                '$caseSensitive': False
            }
        },
        {
            "score": {
                '$meta' : "textScore"
            }
        }). sort(
            [
                ('sort', {'$meta': 'textScore'}),
                ('_id', pymongo.DESCENDING)
            ]
        )

    for object in search_results:
        exist = False
        for result in required:
            if result['title'] == object['title'] or result['url'] == object['url']:
                exist = True
                break

        if exist == False:
            # print(dir(object))
            required.append(object)
        # print(required)

    required = sort_rank(required, optimized_res)

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    print("Search results are " , search_results)
    #total = 10
    total = len(list(search_results))

    #total = search_results.Count()
    #total = search_results.count_documents()
    #total = len(search_results)


    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('result.html',
                           required=required[offset:offset+per_page],
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           q=search_string
                           )

@app.route("/history/")
def history():
    client = MongoClient('localhost',27017)
    search_history_collection = client.gluggle.search_history
    search_results = search_history_collection.find({}).distinct("query")
    history = []
    history = search_results
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    total = len(history)
    print(history)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('history.html',
                           history=history[offset:offset+per_page],
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


if __name__ == "__main__":
    app.run(debug=True)
