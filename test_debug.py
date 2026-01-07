import os
import time
import facebook_bot
import tiktok_bot
import uploader
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

def buat_video_dummy():
    print("🎬 Membuat video dummy 'video_test.mp4'...")
    # Buat video biru durasi 10 detik
    # Kita tidak pakai TextClip biar tidak error ImageMagick
    clip = ColorClip(size=(720, 1280), color=(0, 0, 255), duration=10)
    clip.fps = 24
    
    filename = "video_test.mp4"
    # Render tanpa audio biar cepat
    clip.write_videofile(filename, codec="libx264", audio=False, logger=None)
    return filename

def main():
    print("\n" + "="*40)
    print("🛠️ TOOL DEBUGGING UPLOAD")
    print("="*40)
    print("Video dummy akan dibuat otomatis.")
    print("Pastikan browser Chrome tertutup sebelum mulai!")
    print("-" * 20)
    print("1. Test Upload Facebook Reels")
    print("2. Test Upload TikTok")
    print("3. Test Upload YouTube Shorts")
    print("0. Keluar")
    
    pilihan = input("\nPilih target test (1/2/3): ")
    
    if pilihan == "0": return

    # 1. Bikin Video
    video_path = os.path.abspath(buat_video_dummy())
    
    # 2. Siapkan Metadata Dummy
    timestamp = int(time.time())
    judul = f"TEST UPLOAD {timestamp}"
    caption = f"Ini video test upload otomatis.\n\n#test #coding #bot {timestamp}"

    # 3. Eksekusi
    if pilihan == "1":
        print("\n📘 Memulai Test Facebook...")
        print("   (Browser akan muncul, JANGAN DISENTUH mouse-nya)")
        sukses = facebook_bot.upload_to_facebook_reels(video_path, caption)
        print(f"\nasil FB: {'✅ SUKSES' if sukses else '❌ GAGAL'}")
        
    elif pilihan == "2":
        print("\n🎵 Memulai Test TikTok...")
        print("   (Browser akan muncul, JANGAN DISENTUH mouse-nya)")
        # Pastikan tiktok_bot.py sudah diset headless=False
        sukses = tiktok_bot.upload_to_tiktok(video_path, judul, "#test")
        print(f"\nHasil TikTok: {'✅ SUKSES' if sukses else '❌ GAGAL'}")
        
    elif pilihan == "3":
        print("\n🟥 Memulai Test YouTube...")
        sukses = uploader.upload_video(video_path, judul, caption, "private")
        print(f"\nHasil YouTube: {'✅ SUKSES' if sukses else '❌ GAGAL'}")

    # Hapus video dummy setelah selesai (opsional)
    # if os.path.exists(video_path): os.remove(video_path)

if __name__ == "__main__":
    main()