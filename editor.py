import os
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'): PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUTPUT_FILE = "hasil_video_final.mp4"

def create_text_image(text, width, height, fontsize=60, color='white', bg_color=None):
    img = Image.new('RGBA', (width, height), bg_color if bg_color else (0,0,0,0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", fontsize)
    except: font = ImageFont.load_default()
    
    # Text Wrap Simpel
    lines = []
    words = text.split()
    current_line = words[0]
    for word in words[1:]:
        if draw.textlength(current_line + " " + word, font=font) < width - 100:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    y_text = (height - (len(lines) * fontsize * 1.5)) / 2
    for line in lines:
        w = draw.textlength(line, font=font)
        x_text = (width - w) / 2
        # Outline Hitam
        for i in range(-2, 3):
            for j in range(-2, 3):
                draw.text((x_text+i, y_text+j), line, font=font, fill="black")
        draw.text((x_text, y_text), line, font=font, fill=color)
        y_text += fontsize * 1.5
        
    return np.array(img)

def assemble_video(scenes, audio_paths, video_paths, title_text):
    print("🎬 Merakit Video (High Quality)...")
    clips = []
    
    for i in range(min(len(audio_paths), len(video_paths))):
        try:
            aud = AudioFileClip(audio_paths[i])
            vid = VideoFileClip(video_paths[i])
            
            # Loop video jika kependekan
            if vid.duration < aud.duration: vid = vid.loop(duration=aud.duration)
            else: vid = vid.subclip(0, aud.duration)
            
            # Resize Portrait
            vid = vid.resize(height=1920)
            if vid.w > 1080: vid = vid.crop(x1=(vid.w/2)-540, width=1080)
            else: vid = vid.resize(width=1080)
            
            vid = vid.set_audio(aud)
            if i > 0: vid = vid.crossfadein(0.5) # Efek Transisi
            clips.append(vid)
        except Exception as e: print(f"Skip scene {i}: {e}")

    if not clips: return None
    
    final_clip = concatenate_videoclips(clips, method="compose", padding=-0.5)
    
    # Overlay Judul
    img_title = create_text_image(title_text, 1080, 500, 70, 'yellow')
    clip_title = ImageClip(img_title).set_duration(final_clip.duration).set_position(('center', 150))
    
    final = CompositeVideoClip([final_clip, clip_title], size=(1080, 1920))
    final.write_videofile(OUTPUT_FILE, fps=30, codec='libx264', audio_codec='libmp3lame', threads=4, logger=None)
    
    for c in clips: c.close()
    final.close()
    return OUTPUT_FILE