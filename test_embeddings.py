from utils.embeddings import get_embeddings

embeddings = get_embeddings()

vector = embeddings.embed_query("What is Java?")

print("Success!")
print("Vector Length:", len(vector))