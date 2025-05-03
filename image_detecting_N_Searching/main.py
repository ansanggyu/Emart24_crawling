#2024-11-11 16:38
#수정자: 안상규
#설명: post방식으로 전송받은 이미지파일을 cromadb와 비교하여 유사도를 측정 후, 비슷한 결과 5개를 json형식으로 반환해주는 API
#실행 명령어: python -m uvicorn main:app --reload --port 8001
#postman 호출시 : POST설정, Body -> form-data -> Key값: file, File선택 -> Value값: 비교할 이미지(jpg .jpeg .png)후 send요청

from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError
import torch
from transformers import CLIPProcessor, CLIPModel
import chromadb
import os
import io
import logging
import pickle

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

client = chromadb.Client()
collection = client.create_collection("image_embeddings")

logging.basicConfig(level=logging.INFO)

# 임베딩 캐시 파일 경로 설정
embedding_dir = "image_embeddings"
os.makedirs(embedding_dir, exist_ok=True)

# 임베딩 저장 함수
def save_embedding(image_file, embedding):
    try:
        embedding_path = os.path.join(embedding_dir, f"{image_file}.pkl")
        with open(embedding_path, "wb") as f:
            pickle.dump(embedding, f)
        logging.info(f"Embedding saved: {image_file}")
    except Exception as e:
        logging.error(f"Failed to save embedding for {image_file}: {e}")

# 임베딩 로드 함수
def load_embedding(image_file):
    try:
        embedding_path = os.path.join(embedding_dir, f"{image_file}.pkl")
        if os.path.exists(embedding_path):
            with open(embedding_path, "rb") as f:
                embedding = pickle.load(f)
            logging.info(f"Embedding loaded: {image_file}")
            return embedding
        else:
            logging.warning(f"No cached embedding for: {image_file}")
            return None
    except Exception as e:
        logging.error(f"Error loading embedding for {image_file}: {e}")
        return None

# 이미지 임베딩 계산 함수
def get_image_embedding(image_bytes, image_file):
    # 캐시된 임베딩이 있는지 먼저 확인
    cached_embedding = load_embedding(image_file)
    if cached_embedding is not None:
        logging.info(f"Loaded cached embedding for {image_file}")
        return cached_embedding

    try:
        # 이미지를 열고 임베딩 계산
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")  # 이미지 문제 해결 시도
        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            embeddings = model.get_image_features(**inputs)

        embedding = embeddings.squeeze().numpy()
        embedding = embedding.tolist()  # numpy 배열을 리스트로 변환

        # 계산된 임베딩 저장
        save_embedding(image_file, embedding)
        logging.info(f"Calculated and saved embedding for {image_file}")
        return embedding

    except UnidentifiedImageError as e:
        logging.error(f"Unidentified image error for {image_file}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error opening image {image_file}: {e}")
        return None

# 로컬 이미지들에 대한 임베딩 계산 및 저장
def process_local_images(image_folder):
    for image_file in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_file)

        try:
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()

            # 임베딩 계산 및 캐시 저장
            embedding = get_image_embedding(image_bytes, image_file)

            # 임베딩이 존재하면 ChromaDB에 추가
            if embedding is not None:
                try:
                    collection.add(
                        ids=[image_file],
                        documents=[image_file],
                        embeddings=[embedding]
                    )
                    logging.info(f"Image {image_file} added to ChromaDB.")
                except Exception as e:
                    logging.error(f"Failed to add {image_file} to ChromaDB: {e}")
            else:
                logging.warning(f"Skipping {image_file} due to embedding calculation failure.")
        
        except Exception as e:
            logging.error(f"Error processing file {image_file}: {e}")
            continue  # 예외가 발생해도 계속 진행

# 로컬 이미지 폴더 지정
image_folder = r"C:\Users\AHN\Desktop\Emart24_downloaded_images"
process_local_images(image_folder)

# FastAPI 앱 생성
app = FastAPI()

@app.post("/search/")
async def search_similar_images(file: UploadFile = File(...)):
    try:
        logging.info("Received search request for file: %s", file.filename)

        allowed_extensions = ['.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()

        if not (file.content_type.startswith('image/') and file_extension in allowed_extensions):
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image. Only .jpg, .jpeg, .png are allowed.")

        image_bytes = await file.read()
        logging.info("Read %d bytes from the uploaded image.", len(image_bytes))

        # 이미지 임베딩 계산
        new_embedding = get_image_embedding(image_bytes, file.filename)
        if new_embedding is None:
            raise HTTPException(status_code=400, detail="Failed to process the image.")

        logging.info("Calculated embedding for the uploaded image.")

        # ChromaDB에서 비슷한 이미지 찾기
        logging.info("Querying ChromaDB for similar images.")
        try:
            results = collection.query(query_embeddings=[new_embedding], n_results=5)
        except Exception as e:
            logging.error(f"Error querying ChromaDB: {e}")
            raise HTTPException(status_code=500, detail="Error querying ChromaDB.")

        # 쿼리 결과가 없는 경우 처리
        if not results.get("documents") or not results["documents"]:
            logging.warning("No similar images found in ChromaDB.")
            return {"message": "No similar images found."}

        logging.info("ChromaDB query results: %s", results)

        # ChromaDB에서 받은 결과를 적절히 반환
        similar_images = [{"image": doc, "score": score} for doc, score in zip(results["documents"], results["distances"])]
        logging.info(f"Found {len(similar_images)} similar images.")

        return {"similar_images": similar_images}
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))