import sys
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def _build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def _login_instagram(driver, user: str, password: str):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(2)
    driver.find_elements(By.NAME, "email")[0].send_keys(user)
    driver.find_elements(By.NAME, "pass")[0].send_keys(password)
    btn_login = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "#login_form > div > div.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xz9dl7a > div > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x6s0dn4.xz9dl7a.x1k70j0n.xzueoph.xzboxd6.x14l7nz5 > div > div",
            )
        )
    )
    btn_login.click()
    time.sleep(5)
    driver.refresh()

def _collect_comments(driver, limit: int) -> List[Dict]:
    data: List[Dict] = []
     # antes de scrollar, clica no botão que expande a área de comentários (se existir)
    try:
        expand_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div[1]/div[2]/div/div/div[2]/div[2]/div',
                )
            )
        )
        expand_btn.click()
        time.sleep(2)
    except Exception:
        # se o botão não existir nessa página, segue normalmente
        pass
    # scroller do painel de comentários — tenta seletores conhecidos em ordem
    scroller = None
    _scroller_candidates = [
        # layout novo de reels
        "/html/body/div[1]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div[2]",
        # layout antigo de reels/posts
        "//div[contains(@class,'x5yr21d') and contains(@class,'xw2csxc') "
        "and contains(@class,'x1odjw0f') and contains(@class,'x1n2onr6')]",
        # fallback genérico: div scrollável dentro do artigo
        "//article//div[@role='presentation' and .//ul]",
    ]
    for xpath in _scroller_candidates:
        try:
            scroller = driver.find_element(By.XPATH, xpath)
            break
        except Exception:
            continue

    if scroller is None:
        print("[WARN] Painel de comentários não encontrado — salvando debug_instagram.html", file=sys.stderr)
        with open("debug_instagram.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return []
    # helpers
    def _get_author(c) -> Optional[str]:
        try:
            a = c.find_element(By.XPATH, ".//a[starts-with(@href,'/') and not(contains(@href,'/p/'))][1]")
            return a.text.strip() or a.get_attribute("href").split("/")[-2]
        except:
            return None

    def _get_comment(c) -> str:
      # Procura um span que não esteja dentro de um <a></a>
        try:
            return c.find_element(By.XPATH, ".//div[contains(@class,'xdt5ytf') and contains(@class,'x1cy8zhl')]//span[normalize-space()!=''][1]").text.strip()
        except:
            return ""

    def _get_datetime(c) -> Optional[str]:
        try:
            return c.find_element(By.TAG_NAME, "time").get_attribute("datetime")
        except:
            return None

    _COMMENT_XPATHS = [
        # link de comentário (/p/.../c/...) com timestamp → sobe ao bloco do comentário
        ".//a[contains(@href,'/p/') and contains(@href,'/c/')]/time"
        "/ancestor::div[.//div[contains(@class,'xdt5ytf') and contains(@class,'x1cy8zhl')]][1]",
        # fallback: qualquer bloco com timestamp dentro do scroller
        ".//li[.//time]",
        ".//div[.//time and .//span[normalize-space()!='']]",
    ]

    def _find_comment_blocks():
        for xpath in _COMMENT_XPATHS:
            try:
                blocks = scroller.find_elements(By.XPATH, xpath)
                if blocks:
                    return blocks
            except Exception:
                continue
        return []

    seen: set = set()

    def _harvest():
        for c in _find_comment_blocks():
            if len(data) >= limit:
                break
            comment = _get_comment(c)
            if not comment or comment in seen:
                continue
            seen.add(comment)
            data.append({
                "author": _get_author(c),
                "comment": comment,
                "publishedAt": _get_datetime(c),
            })

    # coleta antes de qualquer scroll (comentários já visíveis)
    _harvest()

    # scroll limitado para evitar loop infinito
    max_scrolls = max(10, min(limit // 5, 40))
    for _ in range(max_scrolls):
        if len(data) >= limit:
            break
        prev_height = driver.execute_script("return arguments[0].scrollHeight", scroller)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroller)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroller)
        if new_height == prev_height:
            break  # fim do conteúdo
        _harvest()

    if not data:
        print("[WARN] Nenhum comentário coletado!", file=sys.stderr)
        with open("debug_instagram.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    return data

def scrape_instagram_much(user: str, password: str, body: dict, limit: int = 10):
    reels = body.get("reels", []) or []
    posts = body.get("posts", []) or []
    driver = _build_driver()
    _login_instagram(driver, user, password)
    time.sleep(5)

    reels_results = []
    posts_results = []
    total_items = len(reels) + len(posts)

    try:
        for rid in reels:
            url = f"https://www.instagram.com/reel/{rid}"
            driver.get(url)
            time.sleep(5)
            print(f"🎬 Varrendo reel {rid}", file=sys.stderr)
            data = _collect_comments(driver, limit)
            reels_results.append({"id": rid, "data": data})

        for pid in posts:
            url = f"https://www.instagram.com/p/{pid}"
            driver.get(url)
            time.sleep(5)
            print(f"📸 Varrendo post {pid}", file=sys.stderr)
            data = _collect_comments(driver, limit)
            posts_results.append({"id": pid, "data": data})

    finally:
        driver.quit()
        print(f"🧹 Sessão encerrada após {total_items} itens.", file=sys.stderr)

    return {"summary": {"total": total_items, "success": len(reels_results + posts_results)}, "reels": reels_results, "posts": posts_results}

def scrape_instagram_one(user: str, password: str, _mode: str, id: str, limit: int = 10) -> List[Dict]:
    try:
        driver = _build_driver()
        _login_instagram(driver, user, password)
        # /p/{id}/ works for both posts and reels and shows the comment panel
        # inline without requiring an extra click, unlike /reel/{id}/ which
        # hides comments behind the speech-bubble button.
        url = f"https://www.instagram.com/p/{id}/"
        driver.get(url)
        time.sleep(4)
        return _collect_comments(driver, limit)
    finally:
        driver.quit()