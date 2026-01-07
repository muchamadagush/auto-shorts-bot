import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def click_element(driver, xpath, name="element"):
    """Fungsi bantu untuk klik elemen dengan aman"""
    try:
        btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", btn)
        print(f"      👉 Klik tombol: {name}")
        return True
    except:
        return False

def upload_to_facebook_reels(file_path, caption):
    print(f"📘 [FB BOT] Memulai proses upload (Mode Hantu)...")
    
    # --- SETUP BROWSER ---
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--headless=new") # Mode Hantu Aktif
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 1. Login
        driver.get("https://www.facebook.com/")
        if os.path.exists("fb_cookies.json"):
            with open("fb_cookies.json", 'r') as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in ["Strict", "Lax", "None"]: c['sameSite'] = "Strict"
                    try: driver.add_cookie(c)
                    except: continue
            driver.refresh()
            time.sleep(5)
        else:
            print("      ❌ Cookies FB tidak ditemukan!")
            return False
        
        # 2. Buka Halaman Creator
        driver.get("https://www.facebook.com/reels/create")
        time.sleep(8)
        driver.execute_script("document.body.style.zoom='70%'") # Zoom out agar tombol kelihatan
        
        # 3. Upload File
        try:
            file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        except:
            file_input = driver.find_element(By.TAG_NAME, "input")
            
        file_input.send_keys(os.path.abspath(file_path))
        print("      📤 Mengirim file ke server FB...")
        time.sleep(15) # Tunggu upload
        
        # --- SCREEN 1: UPLOAD SELESAI -> KLIK NEXT ---
        print("      ➡️ [Screen 1] Mencari tombol Next...")
        if not click_element(driver, "//div[@aria-label='Next'] | //span[contains(text(), 'Next')]", "Next (1)"):
             # Coba bahasa indo
             click_element(driver, "//div[@aria-label='Selanjutnya'] | //span[contains(text(), 'Selanjutnya')]", "Selanjutnya (1)")
        time.sleep(5)

        # --- SCREEN 2: EDIT REEL -> KLIK NEXT ---
        print("      ➡️ [Screen 2] Mencari tombol Next...")
        if not click_element(driver, "//div[@aria-label='Next'] | //span[contains(text(), 'Next')]", "Next (2)"):
             click_element(driver, "//div[@aria-label='Selanjutnya'] | //span[contains(text(), 'Selanjutnya')]", "Selanjutnya (2)")
        time.sleep(5)

        # --- SCREEN 3 (POPUP): REVIEW AUDIENCE -> KLIK CONTINUE ---
        # Ini langkah krusial yang ada di screenshot Anda
        print("      👀 [Popup] Cek apakah ada popup Audience...")
        try:
            # Cari tombol 'Continue' atau 'Lanjutkan' di dalam dialog
            popup_btn_xpath = "//div[@role='dialog']//span[contains(text(), 'Continue')] | //div[@role='dialog']//span[contains(text(), 'Lanjutkan')]"
            if click_element(driver, popup_btn_xpath, "Continue (Popup Audience)"):
                time.sleep(3) # Tunggu popup hilang
        except:
            print("      ℹ️ Tidak ada popup audience, lanjut.")

        # --- SCREEN 4: REEL SETTINGS -> CAPTION & POST ---
        print("      📝 [Screen 4] Isi Caption & Post...")
        
        # A. Isi Caption
        try:
            # Sesuai screenshot: "Describe your reel..."
            caption_xpath = "//div[@aria-label='Describe your reel...'] | //div[@aria-label='Deskripsikan reel Anda...'] | //div[@role='textbox']"
            caption_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, caption_xpath)))
            
            # Klik & Isi (Pakai ActionChains biar kuat)
            actions = ActionChains(driver)
            actions.move_to_element(caption_box).click().perform()
            time.sleep(1)
            
            clean_caption = caption.encode('ascii', 'ignore').decode('ascii')
            actions.send_keys(clean_caption).perform()
            print("      ✅ Caption terisi!")
        except Exception as e:
            print(f"      ⚠️ Gagal isi caption: {e}")

        time.sleep(2)

        # B. Klik POST (Tombol Biru)
        print("      🚀 Mencari tombol Post/Publish...")
        post_xpath = "//div[@aria-label='Post'] | //span[contains(text(), 'Post')] | //div[@aria-label='Posting'] | //span[contains(text(), 'Posting')]"
        
        if click_element(driver, post_xpath, "TOMBOL POST"):
            print("      ⏳ Menunggu finalisasi server (20 detik)...")
            time.sleep(20)
            return True
        else:
            print("      ❌ Gagal klik Post. Mencoba alternatif...")
            # Coba cari tombol Publish/Terbitkan jika Post gak ketemu
            alt_xpath = "//div[@aria-label='Publish'] | //span[contains(text(), 'Publish')]"
            if click_element(driver, alt_xpath, "TOMBOL PUBLISH"):
                time.sleep(20)
                return True
            
            print("      ❌ Timeout: Tombol Post tidak ditemukan.")
            return False

    except Exception as e:
        print(f"      ❌ Error Fatal: {e}")
        return False
    finally:
        driver.quit()