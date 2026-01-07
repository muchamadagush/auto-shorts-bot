import os
import json
import asyncio
import edge_tts
import google.generativeai as genai
from dotenv import load_dotenv
import re
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

VOICE = "id-ID-GadisNeural"
OUTPUT_FOLDER = "bahan_video"

safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

KAMUS_LAFAL = {
    "subscribe": "sab-skraib", "like": "laik", "comment": "komen", "share": "syer",
    "channel": "cenel", "youtube": "yu-tub", "google": "gugel", "guys": "gais",
    "content": "konten", "background": "bek-graun", "download": "don-lod",
    "upload": "ap-lod", "online": "on-lain", "fyp": "ef-wai-pi", "viral": "vai-rel",
    "video": "vidio", "halo": "hallo", "gadget": "ged-jet", "wow": "waw",
    "check": "cek", "out": "aut"
}

def perbaiki_lafal(teks):
    teks_lower = teks.lower()
    for kata_asli, cara_baca in KAMUS_LAFAL.items():
        pola = r'\b' + re.escape(kata_asli) + r'\b'
        teks_lower = re.sub(pola, cara_baca, teks_lower)
    return teks_lower

def cari_ide_topik_otomatis(niche):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "Fakta Unik Dunia"
    genai.configure(api_key=api_key)
    try: model = genai.GenerativeModel('gemini-2.5-flash', safety_settings=safety_settings)
    except: model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
    
    print(f"🤔 Mencari ide viral di niche '{niche}'...")
    prompt = f"Berikan 1 topik video Shorts SPESIFIK & UNIK tentang '{niche}'. HANYA TULIS TOPIKNYA SAJA."
    try: return model.generate_content(prompt).text.strip().replace('"', '').replace("'", "")
    except: return "Fakta Unik Dunia"

def clean_json_text(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match: return match.group(0)
        else: return text
    except: return text

def generate_script(topic):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return None

    genai.configure(api_key=api_key)
    try: model = genai.GenerativeModel('gemini-2.5-flash', safety_settings=safety_settings)
    except: model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)

    print(f"🧠 Merancang Strategi Konten: {topic}...")
    prompt = f"""
    Buatkan konten Shorts tentang: "{topic}".
    
    PERINTAH VISUAL:
    1. 'visual_specific': Deskripsi objek fisik detail (Contoh: "Cat eating cucumber scared").
    2. 'visual_general': Kata kunci luas 1-2 kata (Contoh: "Funny Cat").
    
    FORMAT OUTPUT JSON WAJIB:
    {{
        "judul_viral": "JUDUL CLICKBAIT KAPITAL EMOJI",
        "deskripsi_seo": "Deskripsi singkat...",
        "hashtags": ["#Shorts", "#Viral"],
        "scenes": [
            {{
                "teks": "Narasi scene 1...", 
                "visual_specific": "detail description english",
                "visual_general": "broad keyword english"
            }},
            {{
                "teks": "Narasi scene 2...", 
                "visual_specific": "detail description english",
                "visual_general": "broad keyword english"
            }}
        ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json_text(raw_text))
        print(f"✅ Naskah siap! ({len(data['scenes'])} scenes)")
        return data
    except Exception as e:
        print(f"❌ Gagal naskah: {e}")
        return None

async def generate_audio_per_scene(scenes):
    print("🗣️ Merekam audio per scene...")
    audio_paths = []
    for i, scene in enumerate(scenes):
        teks = perbaiki_lafal(scene['teks'])
        filename = f"scene_{i}.mp3"
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        try:
            communicate = edge_tts.Communicate(teks, VOICE, rate="+10%")
            await communicate.save(output_path)
            audio_paths.append(output_path)
            print(f"   🎙️ Scene {i+1} OK.")
        except: return None
    return audio_paths