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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains # Import Penting!
from selenium.common.exceptions import TimeoutException

# --- FUNGSI BANTU ---
def parse_netscape_cookies(cookie_file):
    cookies = []
    try:
        with open(cookie_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip(): continue
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    cookies.append({
                        'domain': parts[0], 'path': parts[2], 'secure': parts[3] == 'TRUE',
                        'expiry': int(parts[4]) if parts[4].isdigit() else 0,
                        'name': parts[5], 'value': parts[6]
                    })
    except Exception as e:
        print(f"      ⚠️ Gagal baca cookies.txt: {e}")
    return cookies

def kill_popups(driver):
    try:
        popups = driver.find_elements(By.XPATH, "//div[contains(@class, 'TUXModal')]//button | //button[contains(@class, 'css-118w77v-Buttonbox')] | //button[text()='Done'] | //button[text()='Close']")
        for btn in popups:
            driver.execute_script("arguments[0].click();", btn)
            print("      🔨 Popup ditutup!")
            time.sleep(0.5)
    except: pass

def safe_navigate(driver, url):
    """Navigasi aman: Kalau loading kelamaan, paksa stop dan lanjut"""
    try:
        driver.get(url)
    except TimeoutException:
        print(f"      ⚠️ Loading lama ({url}), memaksa stop & lanjut...")
        driver.execute_script("window.stop();")
    except Exception as e:
        print(f"      ⚠️ Error navigasi: {e}")

def robust_file_upload(driver, file_path):
    """Mencari tombol upload dengan Retry Logic"""
    abs_path = os.path.abspath(file_path)
    for attempt in range(5):
        try:
            inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if inputs:
                inputs[0].send_keys(abs_path)
                print("      ✅ Upload via Main Content.")
                return True
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for frame in iframes:
                try:
                    driver.switch_to.frame(frame)
                    inputs_frame = driver.find_elements(By.XPATH, "//input[@type='file']")
                    if inputs_frame:
                        inputs_frame[0].send_keys(abs_path)
                        print(f"      ✅ Upload via Iframe.")
                        driver.switch_to.default_content() 
                        return True
                    driver.switch_to.default_content()
                except:
                    driver.switch_to.default_content()
        except: pass
        print(f"      🔍 Mencari tombol upload... (Percobaan {attempt+1}/5)")
        time.sleep(2)
    return False

# --- FUNGSI UTAMA ---
def upload_to_tiktok(file_path, title, tags):
    print(f"🎵 [TIKTOK BOT] Upload (Ghost Mode + Super Clean)...")
    
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new") # Ghost Mode
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-dev-shm-usage") 
    options.add_argument("--no-sandbox")
    options.add_argument("--mute-audio") 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(60)
    
    try:
        # A. Login
        safe_navigate(driver, "https://www.tiktok.com/about")
        if os.path.exists("cookies.txt"):
            cookies = parse_netscape_cookies("cookies.txt")
            for c in cookies:
                if "tiktok.com" in c['domain']:
                    try: driver.add_cookie({'name': c['name'], 'value': c['value'], 'domain': c['domain'], 'path': c['path'], 'expiry': c['expiry']})
                    except: continue
            time.sleep(2)
        else:
            print("      ❌ File cookies.txt tidak ditemukan!")
            return False

        # B. Halaman Upload
        print("      ➡️ Menuju halaman upload...")
        safe_navigate(driver, "https://www.tiktok.com/tiktokstudio/upload?lang=en")
        time.sleep(5)
        
        if "login" in driver.current_url:
            print("      ❌ Login gagal.")
            return False
        kill_popups(driver)

        # C. Upload File
        print("      📤 Mengirim file video...")
        if robust_file_upload(driver, file_path):
            print("      ⏳ Menunggu proses upload (20s)...")
            time.sleep(20)
        else:
            print("      ❌ Gagal menemukan tombol upload.")
            return False

        # D. Isi Caption
        try:
            print("      📝 Menulis caption...")
            kill_popups(driver)

            caption_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'] | //div[contains(@class, 'DraftEditor-content')]"))
            )
            driver.execute_script("arguments[0].click();", caption_box)
            time.sleep(1)

            # --- UPDATE: HAPUS TEKS SUPER KUAT ---
            print("      🧹 Membersihkan caption default...")
            
            # Cara 1: Javascript (Force Clear)
            try: driver.execute_script("arguments[0].innerText = '';", caption_box)
            except: pass
            
            # Cara 2: ActionChains Ctrl+A -> Delete
            try:
                actions = ActionChains(driver)
                actions.click(caption_box)
                actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)
                actions.send_keys(Keys.BACK_SPACE)
                actions.perform()
            except: pass

            # Cara 3: Spam Backspace (Manual Cleaning) - Hapus 50 karakter terakhir
            for _ in range(50):
                caption_box.send_keys(Keys.BACK_SPACE)
            
            time.sleep(1) # Beri nafas sedikit

            # Susun Teks Baru
            cta = "Follow buat update seru tiap hari! 🔥"
            full_caption = f"{title.upper()} 😱\n\n👇 {cta}\n\n{tags} #fyp"
            
            try: caption_box.send_keys(full_caption)
            except: caption_box.send_keys(full_caption.encode('ascii', 'ignore').decode('ascii'))
            
            print("      ✅ Caption Terisi!")
            
        except Exception as e:
            print(f"      ⚠️ Gagal isi caption: {e}")

        # E. Post
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        kill_popups(driver)

        print("      🚀 Klik Post...")
        btn_xpaths = ["//button[div[text()='Post']]", "//button[contains(., 'Post')]", "//button[contains(@class, 'btn-post')]"]
        posted = False
        for xpath in btn_xpaths:
            try:
                btns = driver.find_elements(By.XPATH, xpath)
                for btn in btns:
                    if btn.is_enabled() and btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        posted = True; break
            except: continue
            if posted: break
        
        if posted:
            print("      ⏳ Finalisasi (20 detik)...")
            time.sleep(20)
            return True
        else:
            print("      ❌ Tombol Post tidak ketemu.")
            return False

    except Exception as e:
        print(f"      ❌ Error Fatal: {e}")
        return False
    finally:
        driver.quit()