import os
import requests
import random
from dotenv import load_dotenv

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OUTPUT_FOLDER = "bahan_video"
BASE_URL = "https://api.pexels.com/videos/search"

if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

def download_file(url, filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(filepath): return filepath
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        return filepath
    except: return None

def search_single_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 3, "orientation": "portrait", "size": "medium"}
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        data = response.json()
        if not data.get("videos"): return None
        
        chosen = random.choice(data['videos'])
        best_file = next((f for f in chosen['video_files'] if f['file_type'] == 'video/mp4' and f['width'] >= 720), chosen['video_files'][0])
        
        clean_name = "".join(x for x in query if x.isalnum())[:10]
        return download_file(best_file['link'], f"{clean_name}_{chosen['id']}.mp4")
    except: return None

def download_scenes_visuals(scenes):
    print("👁️ Mencari Visual Cerdas...")
    video_paths = []
    for i, scene in enumerate(scenes):
        path = search_single_video(scene.get('visual_specific', ''))
        if not path:
            path = search_single_video(scene.get('visual_general', ''))
        if not path:
            path = search_single_video("abstract background vertical")
        
        if path: video_paths.append(path)
        else: print(f"   ⚠️ Gagal total scene {i+1}")
    return video_paths