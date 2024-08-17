APPROACH TO BUILD THE CRAWLER
* We are going to use the following python libraries to achieve the task .

1. `requests` library to fetch the pages.
2. `beautifulsoup4` to parse the response received from the response
object.
3. `pymongo` to connect to mongodb where we are going to store the data.
* Yes that’s it, that’s all we need.

* We will build a python class named `Crawler` inside the `crawler.py` file.
* The first thing we want to do is to make a connection with our database using
“ `pymongo`” library.
```pyhton
client = pymongo.MongoClient(connect_url_to_mongodb)
db = client.name_of_database
```
* After the connection is made we are going to define two methods inside the
class “`Crawler`” named `start_crawling` and `crawl`.
* Both of the methods mentioned above are going to take two arguments:
* url (string containing the url to the page we want to parse)
* depth(integer parameter to control the number of pages your program crawls)


![crawler visualize](https://github.com/nullblocks/FingSearch/assets/110848103/56e3fb66-d2ca-42eb-bcd6-4a03cc6a95f6)
