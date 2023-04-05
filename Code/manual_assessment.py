from elasticsearch7 import Elasticsearch
from Utils import Utils

INDEX = 'homework3'
CLOUD_ID = 'homework3:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ3NjJhZDM3NTU4MTY0OWM1ODM3ZTRiYjg5NjI5ZmFiNyQyMWU0ZDM1MDQzNmY0NDA3OGIzZTY0NTMyN2Q0NTUzNg=='
es = Elasticsearch(request_timeout = 1000, cloud_id = CLOUD_ID, http_auth= ('elastic', '74QCRsRmX0WpC67mIj0PZfDw'))
SIZE = 200
QUERIES = ["Black Lives Matter", "Womens rights", "Racial justice", "Disability rights", "Social Justice Movements"]
utils = Utils()

# modify input queries through stemming, shifting to lowercase, and removing stop words
# stores the modified queries in a dictionary as key-value : (qID, query)
def query_analyzer(queries):
    q_list =[]

    for query in queries:
        body = {
            "tokenizer": "standard",
            "filter": ["porter_stem", "lowercase"],
            "text": query
        }

        res = es.indices.analyze(body=body, index=INDEX)
        q_list.append([list["token"] for list in res["tokens"]])

    return q_list

# uses built-in elasticsearch method to rank documents
# @param given dictionary of queries
def es_search(queries):
    relevant_docs = {}

    for idx, query in enumerate(queries):  # query_list stores (id, query) key value pairs
        print(query)
        body = {
            "size": SIZE,
            "query": {
                "match": {"content": " ".join(query)}  # convert query array back into string
            }
        }
        res_es_search = es.search(index=INDEX, body=body)
        relevant_docs[idx] = [d['_id'] for d in res_es_search['hits']['hits']]

    return relevant_docs

def save_urls(relevant_docs):
    file_base = "/Users/ellataira/Desktop/is4200/homework--5-ellataira/Results/doc_urls_query_"
    for query_id, urls in relevant_docs.items():
        file_name = file_base + str(query_id) + ".txt"
        with open(file_name, 'w') as opened:
            for url in urls:
                opened.write(url + "\n")
        opened.close()

if __name__ == "__main__":
    queries = query_analyzer(QUERIES)
    relevant_docs = es_search(queries)
    save_urls(relevant_docs)