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

def parse_netscape_cookies(cookie_file):
    """Membaca cookies.txt format Netscape agar bisa dipakai Selenium"""
    cookies = []
    try:
        with open(cookie_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip(): continue
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    cookie = {
                        'domain': parts[0],
                        'path': parts[2],
                        'secure': parts[3] == 'TRUE',
                        'expiry': int(parts[4]) if parts[4].isdigit() else 0,
                        'name': parts[5],
                        'value': parts[6]
                    }
                    cookies.append(cookie)
    except Exception as e:
        print(f"      ⚠️ Gagal baca cookies.txt: {e}")
    return cookies

def kill_popups(driver):
    """Fungsi pembunuh popup pengganggu"""
    try:
        # Cari tombol close/X pada modal apapun
        popups = driver.find_elements(By.XPATH, "//div[contains(@class, 'TUXModal')]//button | //button[contains(@class, 'css-118w77v-Buttonbox')]")
        for btn in popups:
            driver.execute_script("arguments[0].click();", btn)
            print("      🔨 Popup ditutup!")
            time.sleep(1)
    except: pass

def upload_to_tiktok(file_path, title, tags):
    print(f"🎵 [TIKTOK BOT] Memulai proses upload (Custom)...")
    
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--headless=new") # Mode Hantu
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 1. Login dengan cookies.txt
        driver.get("https://www.tiktok.com/")
        
        if os.path.exists("cookies.txt"):
            cookies = parse_netscape_cookies("cookies.txt")
            for c in cookies:
                # Filter domain agar sesuai session
                if ".tiktok.com" in c['domain'] or "tiktok.com" in c['domain']:
                    try: 
                        driver.add_cookie({
                            'name': c['name'], 'value': c['value'], 'domain': c['domain'], 
                            'path': c['path'], 'expiry': c['expiry']
                        })
                    except: continue
            driver.refresh()
            time.sleep(5)
        else:
            print("      ❌ File cookies.txt tidak ditemukan!")
            return False

        # 2. Buka Halaman Upload (Force English biar selector stabil)
        driver.get("https://www.tiktok.com/upload?lang=en")
        time.sleep(8)
        
        # Bersihkan popup awal (jika ada)
        kill_popups(driver)

        # 3. Upload File (Masuk ke dalam iframe jika perlu)
        try:
            # TikTok kadang pakai iframe untuk upload area
            iframe = driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframe) > 0:
                driver.switch_to.frame(iframe[0])
                file_input = driver.find_element(By.TAG_NAME, "input")
                file_input.send_keys(os.path.abspath(file_path))
                driver.switch_to.default_content()
            else:
                file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(os.path.abspath(file_path))
                
            print("      📤 Mengirim file ke server TikTok...")
            time.sleep(15) # Tunggu upload
        except Exception as e:
            print(f"      ❌ Gagal input file: {e}")
            return False

        # 4. Isi Caption
        try:
            print("      📝 Mencoba isi caption...")
            
            # Cek popup lagi siapa tau muncul setelah upload
            kill_popups(driver)

            caption_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'] | //div[contains(@class, 'DraftEditor-content')]"))
            )
            
            # Klik & Tulis
            actions = ActionChains(driver)
            actions.move_to_element(caption_box).click().perform()
            time.sleep(1)
            
            # Buat deskripsi: Judul + Tags (Max 2000 chars)
            full_caption = f"{title}\n\n{tags} #fyp"
            clean_caption = full_caption.encode('ascii', 'ignore').decode('ascii')
            
            actions.send_keys(clean_caption).perform()
            print("      ✅ Caption terisi!")
        except Exception as e:
            print(f"      ⚠️ Gagal isi caption (Skip): {e}")

        # 5. Scroll ke Bawah & Klik Post
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Cek popup terakhir (Copyright check dll)
        kill_popups(driver)

        print("      🚀 Mencari tombol Post...")
        # Selector tombol Post TikTok yang sering berubah
        btn_xpaths = [
            "//button[div[text()='Post']]", 
            "//button[contains(., 'Post')]",
            "//button[contains(@class, 'btn-post')]"
        ]
        
        posted = False
        for xpath in btn_xpaths:
            try:
                # Cari tombol yang enable (tidak disabled)
                btns = driver.find_elements(By.XPATH, xpath)
                for btn in btns:
                    if btn.is_enabled() and btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        print("      🎉 TOMBOL POST DIKLIK!")
                        posted = True
                        break
            except: continue
            if posted: break
        
        if posted:
            print("      ⏳ Menunggu finalisasi server (20 detik)...")
            time.sleep(20)
            return True
        else:
            print("      ❌ Timeout: Tombol Post tidak ditemukan/disabled.")
            return False

    except Exception as e:
        print(f"      ❌ Error Fatal: {e}")
        return False
    finally:
        driver.quit()