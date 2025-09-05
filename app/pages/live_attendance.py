import streamlit as st
import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
import pickle
import pathlib
from firebase.firebase_admin_init import get_firestore_client
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

def extract_embedding(face_img, resnet):
    face_img = face_img.resize((160, 160))
    face_tensor = torch.tensor(np.array(face_img)).permute(2, 0, 1).float() / 255.0
    face_tensor = (face_tensor - 0.5) / 0.5
    with torch.no_grad():
        emb = resnet(face_tensor.unsqueeze(0)).squeeze().numpy()
    return emb

def show_live_attendance():
    st.title('Live Attendance')
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', max_chars=10, key='live_class_name')
    date = st.date_input('Date', value=datetime.date.today(), key='live_date')
    uploaded_image = st.file_uploader('Upload or capture classroom image', type=['jpg', 'jpeg', 'png'], key='live_uploaded_image')
    if st.button('Analyze & Mark Attendance', key='live_analyze_btn'):
        if not class_name:
            st.error('Please enter the class.')
        elif not uploaded_image:
            st.error('Please upload or capture a classroom image.')
        else:
            try:
                img = Image.open(uploaded_image).convert('RGB')
                project_root = pathlib.Path(__file__).resolve().parents[2]
                model_dir = str(project_root / 'models')
                emb_path = str(pathlib.Path(model_dir) / f'embeddings_{class_name}.pkl')
                if not os.path.exists(emb_path):
                    st.error('No embeddings found for this class. Please retrain the model.')
                    st.stop()
                with open(emb_path, 'rb') as f:
                    class_embeddings = pickle.load(f)
                db = get_firestore_client()
                students_ref = db.collection('students').where('class', '==', class_name)
                students = {doc.to_dict()['register_number']: doc.to_dict()['name'] for doc in students_ref.stream()}
                mtcnn = MTCNN(keep_all=True, device='cpu')
                resnet = InceptionResnetV1(pretrained='vggface2').eval()
                boxes, _ = mtcnn.detect(img)
                if boxes is None or len(boxes) == 0:
                    st.warning('No faces detected in the image.')
                    st.stop()
                annotated_img = img.copy()
                draw = ImageDraw.Draw(annotated_img)
                try:
                    font = ImageFont.truetype("arial.ttf", 18)
                except:
                    font = None
                present = set()
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)
                    face = img.crop((x1, y1, x2, y2))
                    emb = extract_embedding(face, resnet)
                    min_dist = float('inf')
                    best_regno = None
                    for regno, emb_list in class_embeddings.items():
                        for known_emb in emb_list:
                            dist = np.linalg.norm(emb - known_emb)
                            if dist < min_dist:
                                min_dist = dist
                                best_regno = regno
                    THRESHOLD = 0.9  # Typical for FaceNet/ResNet
                    if min_dist < THRESHOLD:
                        present.add(best_regno)
                        draw.rectangle([x1, y1, x2, y2], outline="green", width=4)
                        label = best_regno
                        if font:
                            draw.text((x1, y1 - 22), label, fill="green", font=font)
                        else:
                            draw.text((x1, y1 - 22), label, fill="green")
                    else:
                        draw.rectangle([x1, y1, x2, y2], outline="red", width=4)
                        label = "Unknown"
                        if font:
                            draw.text((x1, y1 - 22), label, fill="red", font=font)
                        else:
                            draw.text((x1, y1 - 22), label, fill="red")
                absent = set(students.keys()) - present
                attendance_ref = db.collection('attendance').document(f'{class_name}_{date}')
                attendance_ref.set({
                    'class': class_name,
                    'date': str(date),
                    'present': list(present),
                    'absent': list(absent)
                })
                st.success('Attendance marked!')
                st.image(annotated_img, caption="Present students (green), Unknown (red)", use_column_width=True)
                st.write('### Present Students')
                st.write([f"{regno} - {students[regno]}" for regno in present])
                st.write('### Absent Students')
                st.write([f"{regno} - {students[regno]}" for regno in absent])
            except Exception as e:
                st.error(f'Error during attendance analysis: {e}')

if __name__ == '__main__':
    show_live_attendance()
