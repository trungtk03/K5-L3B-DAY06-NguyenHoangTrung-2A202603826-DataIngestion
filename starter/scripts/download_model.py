import sys
import os

print("Starting model download script...", flush=True)
try:
    from sentence_transformers import SentenceTransformer
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading {model_name}...", flush=True)
    model = SentenceTransformer(model_name)
    print(f"Success! Dimensions: {model.get_sentence_embedding_dimension()}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
