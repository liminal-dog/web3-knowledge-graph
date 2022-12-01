import logging
from gql.transport.requests import log as requests_logger
requests_logger.setLevel(logging.WARNING)
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import re
from newspaper import Article
import json
import time


class MirrorScraperHelper():
    
    def get_transations(self, query_string, counter=0):
        time.sleep(counter)
        if counter > 10:
            return None
        transport = AIOHTTPTransport(url="https://arweave.net/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql(query_string)
        try:
            results = client.execute(query)
        except Exception as e:
            logging.error(f"An exception occured getting transactions, {e}")
            return self.get_transations(query_string, counter=counter+1)
        if results != None:
            return results
        else:
            return self.get_transations(query_string, counter=counter+1)
    
    def get_all_transactions(self, startBlock, step):
        stopBlock = startBlock + step
        cursor = ""
        all_results = []

        query_string = """
                {{
                    transactions(first:100,{} block: {{min:{}, max:{}}}, tags: {{name: "App-Name", values: "MirrorXYZ"}}) {{
                        edges {{
                        cursor
                            node {{
                                id
                                tags{{
                                    name
                                    value
                                }}
                                block {{
                                    timestamp
                                    height
                                }}
                            }}
                        }}
                    }}
                }}
                """
        
        results = ["init"]
        while len(results) > 0:
            content = self.get_transations(query_string.format(cursor, startBlock, stopBlock))
            if content:
                results = content.get("transactions", {"edges": []})["edges"]
            else:
                results = []
            all_results += results
            if len(results) > 0:
                cursor = f'after: "{results[-1]["cursor"]}", '
        return all_results

    def getArweaveTxs(self, startBlock, endBlock, initialStep):
        step = initialStep
        results = []

        currentBlock = startBlock
        while currentBlock < endBlock:
            returned = self.get_all_transactions(currentBlock, step)
            logging.info(f"==========> Retrieved {len(returned)} transactions from block {currentBlock} to block {currentBlock+step}")
            if len(returned) == 100 and step != 1:
                step = step // 10
                currentBlock -= step
            elif len(returned) < 10 and step < initialStep:
                step = step * 10
                currentBlock -= step
            else:
                results += returned
            currentBlock += step

        return results


    def get_urls(self, text):
        URL_REGEX = r"""((?:(?:https|ftp|http)?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|org|uk)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|uk|ac)\b/?(?!@)))"""
        urls = re.findall(URL_REGEX, text)
        urls = [url for url in urls if ".gif" not in url]
        urls = [url for url in urls if ".jpg" not in url]
        urls = [url for url in urls if ".png" not in url]
        urls = [url for url in urls if ".jpeg" not in url]
        urls = [url for url in urls if ".mp4" not in url]
        urls = [url for url in urls if ".mp3" not in url]
        return urls


    def scrape_urls(self, urls):
        output_list = []
        for url in urls:
            try:
                article = Article(url)
                article.download()
                article.parse()
                if article.text != "" and article.text is not None:
                    if article.publish_date is None:
                        publish_date = 0
                    else:
                        publish_date = article.publish_date.timestamp()
                    output_list.append(
                        {"text": article.text, "title": article.title, "publish_date": publish_date, "url": url}
                    )
            except:
                pass
        return output_list


    def parse_items(self, entry):
        txHash = entry[1]
        body = json.loads(entry[0])["content"].get("body", "")
        urls = self.get_urls(body)
        scraped_urls = self.scrape_urls(urls)
        for idx in range(len(scraped_urls)):
            scraped_urls[idx]["transaction"] = txHash
        return scraped_urls
