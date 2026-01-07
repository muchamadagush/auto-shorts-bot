import asyncio
import brain
import media
import editor

async def run_automation():
    print("=== 🤖 AUTO SHORTS GENERATOR v2.0 (MULTI-SCENE) ===")
    
    topic = input("Masukkan Topik Video: ")
    if not topic: return

    # 1. OTAK (Generate List of Scenes)
    print("\n[1/3] 🧠 Merancang Naskah...")
    data_konten = brain.generate_script(topic)
    if not data_konten: return
    
    scenes = data_konten['scenes']
    judul = data_konten['judul'].upper()
    print(f"   👉 Judul: {judul}")
    
    # Generate Audio Per Scene
    audio_paths = await brain.generate_audio_per_scene(scenes)
    if not audio_paths: return

    # 2. MATA (Download Video Per Scene)
    print("\n[2/3] 👁️ Mencari Visual...")
    video_paths = media.download_scenes_visuals(scenes)
    
    # Pastikan jumlah video sama dengan audio (kalau gagal download, script media udah handle fallback)
    if len(video_paths) != len(audio_paths):
        print("⚠️ Jumlah video dan audio tidak sinkron!")
        return

    # 3. TANGAN (Editing)
    print("\n[3/3] 🎬 Proses Editing...")
    final_video = editor.assemble_video(scenes, audio_paths, video_paths, judul)
    
    if final_video:
        print(f"\n✅ SUKSES! Video Multi-Context siap: {final_video}")

if __name__ == "__main__":
    try:
        asyncio.run(run_automation())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_automation())