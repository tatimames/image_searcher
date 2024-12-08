from elasticsearch import Elasticsearch
import utils

# Database connection data
es = Elasticsearch(
    hosts=[{'host': 'localhost', 'port': 9200, 'scheme':'https'}],
    basic_auth=('elastic', 'changeme'),
    verify_certs=False,  # Disable certificate verification
    ssl_show_warn=False  # Suppress SSL warnings in logs
)

index_name = "image_embeddings"

def insert_data(embedding, url):
    document = {
        'url': url,
        'embedding': embedding.tolist()
    }

    # Index the document in Elasticsearch
    es.index(index=index_name, id=url, body=document)
    print(f"Indexed {url} with ID {url}")
    

def does_url_exist(url): # Checks whether image URL already exists in DB 
    existing_doc = es.exists(index=index_name, id=url)
    print(existing_doc)
    return existing_doc


def query_db_text(text):
    try:
        text_embedding_np = utils.generate_text_embedding(text)

        # Query Elasticsearch for image embeddings
        query = {
            "size": 6, 
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": """
                            cosineSimilarity(params.text_embedding, 'embedding') + 1.0
                        """,
                        "params": {"text_embedding": text_embedding_np.tolist()}
                    }
                }
            }
        }

        response = es.search(index=index_name, body=query)

        # Extract and return the top results
        hits = response['hits']['hits']
        top_results = [hit["_source"]['url'] for hit in hits]

        return top_results

    except Exception as e:
        print(f"Error querying Elasticsearch: {e}")
        return None