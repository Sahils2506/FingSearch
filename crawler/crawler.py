from bs4 import BeautifulSoup
import requests
import pymongo
import urllib.parse
import sys


class Crawler():

    connection_url = "mongodb://127.0.0.1:27017/"

    client = pymongo.MongoClient(connection_url)

    # db = client.results
    db = client.gluggle

    disallowed_links = []

    def start_crawl(self, url, depth):
        robots_url = urllib.parse.urljoin(url, '/robots.txt')

        try:
            robots = requests.get(robots_url)
        except:
            print("robots not found!!!")
            self.crawl(url, depth)

        soup = BeautifulSoup(robots.text, 'lxml')

        content = soup.find('p').text

        for word in content:
            if word[0] == '/':
                self.disallowed_links.append(urllib.parse.urljoin(url, word))

        print("robots found and appended in disallowed_links...")

        self.crawl(url, depth, self.disallowed_links)

    def crawl(self, url, depth, *disallowed_links):

        try:
            print(f"Crawling url {url} at depth: {depth}")
            response = requests.get(url)
        except:
            print(f"Failed to perform HTTP GET request on {url}")
            return

        soup = BeautifulSoup(response.text, 'lxml')

        try:
            title = soup.find('title').text
            description = ''

            for tag in soup.findAll():
                if tag.name == 'p':
                    description += tag.text.strip().replace('\n', '')

        except:
            print("Failed to retrieve title and description...")
            return

        query = {
            'url': url,
            'title': title,
            'description': description,
        }

        # search_results = self.db.search_results database.queries
        search_results = self.db.queries

        search_results.insert_one(query)

        search_results.create_index(
            [
                ('url', pymongo.TEXT),
                ('title', pymongo.TEXT),
                ('description', pymongo.TEXT)
            ],
            name='search_results',
            default_language="english"
        )

        if depth == 0:
            return

        links = soup.findAll('a')

        for link in links:
            try:
                if link['href'] not in disallowed_links:
                    if 'http' in link['href']:
                        self.crawl(link['href'], depth-1, disallowed_links)
                    else:
                        link['href'] = urllib.parse.urljoin(url, link['href'])
                        self.crawl(link['href'], depth-1, disallowed_links)
            except KeyError:
                print("no links retrieved from the page")
                pass

        self.client.close()


spider = Crawler()

spider.start_crawl(
    sys.argv[1], int(sys.argv[2])
)
