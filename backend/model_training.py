import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import io
import base64
import pickle
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from tqdm import tqdm
from firebase.firebase_admin_init import get_firestore_client
import logging
import pathlib

logging.basicConfig(level=logging.INFO)

project_root = pathlib.Path(__file__).resolve().parents[1]
MODEL_DIR = str(project_root / 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

mtcnn = MTCNN(keep_all=True, device='cpu')
resnet = InceptionResnetV1(pretrained='vggface2').eval()

st.title('Model Training Debug - Face Detection')

def decode_base64_image(b64_string):
    img_bytes = base64.b64decode(b64_string)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    return img

def extract_embedding(face_img):
    face_img = face_img.resize((160, 160))
    face_tensor = torch.tensor(np.array(face_img)).permute(2, 0, 1).float() / 255.0
    face_tensor = (face_tensor - 0.5) / 0.5
    with torch.no_grad():
        emb = resnet(face_tensor.unsqueeze(0)).squeeze().numpy()
    return emb

def train_class_embeddings():
    db = get_firestore_client()
    students = db.collection('students').stream()
    class_data = {}
    for student in students:
        data = student.to_dict()
        cls = data['class']
        if cls not in class_data:
            class_data[cls] = []
        class_data[cls].append(data)
    for cls, students in class_data.items():
        embeddings_dict = {}
        st.subheader(f"Class: {cls}")
        # debug_dir = pathlib.Path(MODEL_DIR).parent / 'debug_training_faces' / cls
        # debug_dir.mkdir(parents=True, exist_ok=True)
        for student in tqdm(students, desc=f'Processing class {cls}'):
            regno = student.get('register_number', '')
            name = student.get('name', '')
            embeddings_dict.setdefault(regno, [])
            face_imgs = []
            for img_idx, img_b64 in enumerate(student['images']):
                try:
                    img = decode_base64_image(img_b64)
                    boxes, _ = mtcnn.detect(img)
                    if boxes is None or len(boxes) == 0:
                        logging.warning(f'No face detected for {regno} in class {cls}')
                        continue
                    areas = [(box[2]-box[0])*(box[3]-box[1]) for box in boxes]
                    idx = int(np.argmax(areas))
                    x1, y1, x2, y2 = map(int, boxes[idx])
                    face = img.crop((x1, y1, x2, y2))
                    emb = extract_embedding(face)
                    embeddings_dict[regno].append(emb)
                    # debug_img = img.copy()
                    # draw = ImageDraw.Draw(debug_img)
                    # draw.rectangle([x1, y1, x2, y2], outline="green", width=3)
                    # label = f"{regno}"
                    # try:
                    #     font = ImageFont.truetype("arial.ttf", 18)
                    # except:
                    #     font = None
                    # if font:
                    #     draw.text((x1, y1 - 22), label, fill="green", font=font)
                    # else:
                    #     draw.text((x1, y1 - 22), label, fill="green")
                    # debug_img.save(debug_dir / f"{regno}_{img_idx}.jpg")
                    # face_imgs.append(debug_img)
                except Exception as e:
                    logging.error(f'Error processing image for {regno}: {e}')
            if face_imgs:
                cols = st.columns(min(3, len(face_imgs)))
                for i, img in enumerate(face_imgs[:3]):
                    with cols[i]:
                        st.image(img, caption=f"{name} ({regno})", use_column_width=True)
        emb_path = os.path.join(MODEL_DIR, f'embeddings_{cls}.pkl')
        with open(emb_path, 'wb') as f:
            pickle.dump(embeddings_dict, f)
        logging.info(f'Embeddings for class {cls} saved.')

if __name__ == '__main__':
    train_class_embeddings()
