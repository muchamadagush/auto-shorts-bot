import asyncio
import time
import random
import os
import shutil
from datetime import datetime, timedelta
import brain
import media
import editor
import uploader
import tiktok_bot 
import facebook_bot

# --- KONFIGURASI TARGET ---
LIST_NICHE = [
    "Fakta Unik", "Misteri Dunia", "Teknologi AI", "Tips Kesehatan", 
    "Sejarah Gelap", "Psikologi Manusia", "Motivasi Sukses", "Sains Populer"
]

def cleanup(path):
    """Membersihkan file sampah setelah upload"""
    print("🧹 Membersihkan ruang penyimpanan...")
    if path and os.path.exists(path):
        try: os.remove(path)
        except: pass
    
    folder_bahan = "bahan_video"
    if os.path.exists(folder_bahan):
        for filename in os.listdir(folder_bahan):
            file_path = os.path.join(folder_bahan, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e: pass
    
    if not os.path.exists("bahan_video"): os.makedirs("bahan_video")

async def job_satu_video():
    print("\n" + "="*40 + f"\n🎬 MULAI JOB BARU: {datetime.now().strftime('%H:%M')}\n" + "="*40)

    # 1. CARI IDE
    niche = random.choice(LIST_NICHE)
    topic = brain.cari_ide_topik_otomatis(niche)
    if not topic: return False
    
    data = brain.generate_script(topic)
    if not data: return False
    
    # 2. SIAPKAN BAHAN
    audio_paths = await brain.generate_audio_per_scene(data['scenes'])
    video_paths = media.download_scenes_visuals(data['scenes'])
    
    if not audio_paths or not video_paths: 
        print("❌ Gagal download bahan.")
        return False

    # 3. RENDER VIDEO
    final_path = editor.assemble_video(data['scenes'], audio_paths, video_paths, data['judul_viral'])
    
    if final_path:
        print("\n🚀 MEMULAI DISTRIBUSI VIDEO...")
        
        # Siapkan Caption
        tags_str = " ".join(data['hashtags'])
        desc_yt = f"{data['judul_viral']}\n\n{data['deskripsi_seo']}\n\n{tags_str} #Shorts"
        caption_fb = f"{data['judul_viral']}\n\n{tags_str} #Reels #VideoViral"
        
        # --- UPLOAD YOUTUBE ---
        print("\n[1/3] Upload YouTube Shorts...")
        yt_ok = uploader.upload_video(final_path, data['judul_viral'], desc_yt)
        
        # --- UPLOAD TIKTOK ---
        print("\n[2/3] Upload TikTok...")
        tt_ok = tiktok_bot.upload_to_tiktok(final_path, data['judul_viral'], tags_str)
        
        # --- UPLOAD FACEBOOK ---
        print("\n[3/3] Upload Facebook Reels...")
        fb_ok = facebook_bot.upload_to_facebook_reels(final_path, caption_fb)
        
        # Laporan Akhir
        print("\n" + "-"*30)
        print(f"📊 LAPORAN UPLOAD: {data['judul_viral']}")
        print(f"   YouTube  : {'✅ SUKSES' if yt_ok else '❌ GAGAL'}")
        print(f"   TikTok   : {'✅ SUKSES' if tt_ok else '❌ GAGAL'}")
        print(f"   Facebook : {'✅ SUKSES' if fb_ok else '❌ GAGAL'}")
        print("-"*30)

        # Hapus file hanya jika minimal 1 platform sukses
        if yt_ok or tt_ok or fb_ok:
            cleanup(final_path)
            return True
        else:
            print("⚠️ Semua upload gagal. File video disimpan untuk cek manual.")
            return False

    return False

async def main_loop():
    print("🤖 MESIN KONTEN OTOMATIS SIAP (YT + TT + FB)")
    print("   Tekan Ctrl+C untuk berhenti kapan saja.")
    
    # Cek kelengkapan file wajib
    if not os.path.exists("cookies.txt"): 
        print("⚠️ PERINGATAN: File 'cookies.txt' (TikTok) tidak ditemukan!")
    if not os.path.exists("fb_cookies.json"): 
        print("⚠️ PERINGATAN: File 'fb_cookies.json' (Facebook) tidak ditemukan!")

    while True:
        # Tentukan target harian (Misal: 2-4 video per hari)
        target_hari_ini = random.randint(2, 4)
        print(f"\n📅 JADWAL HARI INI: {target_hari_ini} Video")
        
        for i in range(target_hari_ini):
            await job_satu_video()
            
            # Jika masih ada sisa jadwal, istirahat dulu (3-5 jam)
            if i < target_hari_ini - 1:
                durasi_jeda = random.randint(3, 5) * 3600 
                jam_lanjut = (datetime.now() + timedelta(seconds=durasi_jeda)).strftime('%H:%M')
                print(f"\n☕ Bot istirahat {durasi_jeda/3600:.1f} jam (Lanjut pukul {jam_lanjut})...")
                time.sleep(durasi_jeda)
        
        # Tidur Panjang sampai besok pagi (Jam 7-9 Pagi)
        now = datetime.now()
        besok = now + timedelta(days=1)
        jam_bangun = random.randint(7, 9)
        waktu_bangun = besok.replace(hour=jam_bangun, minute=0, second=0)
        durasi_tidur = (waktu_bangun - now).total_seconds()
        
        if durasi_tidur > 0:
            print(f"\n🌙 Target harian selesai. Bot tidur sampai {waktu_bangun.strftime('%d-%m %H:%M')}...")
            time.sleep(durasi_tidur)

if __name__ == "__main__":
    try: asyncio.run(main_loop())
    except KeyboardInterrupt: print("\n🛑 Bot dihentikan manual.")
    except Exception as e: asyncio.run(main_loop())