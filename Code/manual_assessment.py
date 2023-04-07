import os

from elasticsearch7 import Elasticsearch
from Utils import Utils

# INDEX = 'homework3'
# CLOUD_ID = 'homework3:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ3NjJhZDM3NTU4MTY0OWM1ODM3ZTRiYjg5NjI5ZmFiNyQyMWU0ZDM1MDQzNmY0NDA3OGIzZTY0NTMyN2Q0NTUzNg=='
# es = Elasticsearch(request_timeout = 1000, cloud_id = CLOUD_ID, http_auth= ('elastic', '74QCRsRmX0WpC67mIj0PZfDw'))
SIZE = 200
INDEX = 'hw5indexugh'
QUERIES = ["Black Lives Matter", "Womens rights", "Racial justice", "Disability rights", "Social Justice Movements"]
utils = Utils()
es = Elasticsearch("http://localhost:9200")

# modify input queries through stemming, shifting to lowercase, and removing stop words
# stores the modified queries in a dictionary as key-value : (qID, query)
def query_analyzer(queries):
    q_list ={}

    for id, query in enumerate(queries):
        body = {
            "tokenizer": "standard",
            "filter": ["porter_stem", "lowercase"],
            "text": query
        }

        res = es.indices.analyze(body=body, index=INDEX)
        q_list[id] = [list["token"] for list in res["tokens"]]

    return q_list


# uses built-in elasticsearch method to rank documents
# @param given dictionary of queries
def es_search(queries):
    relevant_docs = {}

    for idx, query in queries.items():  # query_list stores (id, query) key value pairs
        print(query)
        body = {
            "size": SIZE,
            "query": {
                "match": {"content": " ".join(query)}  # convert query array back into string
            }
        }
        res_es_search = es.search(index=INDEX, body=body)
        relevant_docs[idx + 1] = res_es_search

    return relevant_docs

def save_urls(relevant_docs):
    file_base = "/Users/ellataira/Desktop/homework--5-ellataira/Results/doc_urls_query_"
    for query_id, docs in relevant_docs.items():
        file_name = file_base + str(query_id) + ".txt"
        with open(file_name, 'w') as opened:
            for d in docs['hits']['hits']:
                opened.write(d['_id'] + "\n")
        opened.close()

# outputs search results to a file
# uses fields specific to ES builtin search
# the ES builtin search already sorts the hits in decresing order, so there is no need to reorder before saving
def save_to_file_for_es_builtin(relevant_docs, doc_name):
    f = '/Users/ellataira/Library/Mobile Documents/com~apple~CloudDocs/Desktop/is4200/homework--5-ellataira/Results/' + doc_name + '.txt'

    if os.path.exists(f):
        os.remove(f)

    with open(f, 'w') as f:
        for query_id, docs in relevant_docs.items():
            count = 1
            for d in docs['hits']['hits']:
                f.write(str(query_id) + ' Q0 ' + str(d['_id']) + ' ' + str(count) + ' ' + str(d['_score']) + ' Exp\n')
                count += 1

    f.close()

if __name__ == "__main__":
    queries = query_analyzer(QUERIES)
    relevant_docs = es_search(queries)
    save_to_file_for_es_builtin(relevant_docs, "es_builtin")
    save_urls(relevant_docs)
    # save_urls(relevant_docs)