import clip
import torch
from PIL import Image
import requests
import numpy as np


def download_image(url, image_path):# Recieves url and dowloads image
    try:
        print(f"Downloading: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded: {image_path}")
        else:
            print(f"Failed to download {image_path} from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


def generate_embedding(image_path): # Use openAI CLIP to embed image
    try:
        print("Generating embedding")
        model, preprocess = clip.load("ViT-B/32", device="cpu")
        
        image = Image.open(image_path).convert('RGB') 
        image = preprocess(image).unsqueeze(0) 
        
        with torch.no_grad():
            embedding = model.encode_image(image)
        
        embedding_np = embedding.cpu().numpy().flatten()
        
        return embedding_np
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None
        
        
def generate_text_embedding(text):
        model, preprocess = clip.load("ViT-B/32", device="cpu")

        # Generate the text embedding
        text_token = clip.tokenize([text]) 
        with torch.no_grad():
            text_embedding = model.encode_text(text_token)  # Get text embedding
        text_embedding_np = text_embedding.cpu().numpy().flatten() 
        return text_embedding_np


