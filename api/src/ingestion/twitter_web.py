# src/ingestion/twitter_web.py
import sys
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def _build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def _collect_tweets(driver, limit: int) -> List[Dict]:
    data: List[Dict] = []

    last_height = driver.execute_script("return document.body.scrollHeight")
    while len(data) < limit:
        tweets = driver.find_elements(By.XPATH, '//article')
        for t in tweets[len(data):limit]:
            try:
                author = t.find_element(By.XPATH, './/div[@data-testid="User-Name"]').text
            except:
                author = None

            try:
                text = t.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            except:
                text = ""

            try:
                published = t.find_element(By.TAG_NAME, "time").get_attribute("datetime")
            except:
                published = None

            try:
                like_count = t.find_element(By.XPATH, './/div[@data-testid="like"]').text or "0"
            except:
                like_count = "0"

            try:
                retweet_count = t.find_element(By.XPATH, './/div[@data-testid="retweet"]').text or "0"
            except:
                retweet_count = "0"

            try:
                reply_count = t.find_element(By.XPATH, './/div[@data-testid="reply"]').text or "0"
            except:
                reply_count = "0"

            try:
                permalink = t.find_element(By.XPATH, ".//a[contains(@href, '/status/')]").get_attribute("href")
            except:
                permalink = None

            data.append({
                "author": author,
                "text": text,
                "publishedAt": published,
                "likeCount": like_count,
                "retweetCount": retweet_count,
                "replyCount": reply_count,
                "permalink": permalink,
            })

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    if not data:
        print("[WARN] Nenhum tweet carregado!", file=sys.stderr)
        with open("debug_twitter.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    return data

def scrape_twitter_profile(username: str, limit: int = 10) -> List[Dict]:
    """Raspa tweets de um perfil específico."""
    url = f"https://twitter.com/{username}"
    return _scrape(url, limit)


def scrape_twitter_hashtag(hashtag: str, limit: int = 10) -> List[Dict]:
    """Raspa tweets de uma hashtag específica."""
    url = f"https://twitter.com/hashtag/{hashtag}"
    return _scrape(url, limit)


def scrape_twitter_post(url: str, limit: int = 10) -> List[Dict]:
    """Raspa respostas de um post específico (URL completa do tweet)."""
    return _scrape(url, limit)

def _scrape(url: str, limit: int) -> List[Dict]:
    driver = _build_driver()
    driver.get(url)
    time.sleep(5)
    
    try:
        data = _collect_tweets(driver, limit)
    finally:
        driver.quit()
    return data

def scrape_twitter_many(body: dict, limit: int = 10) -> Dict[str, Any]:
    profiles = body.get("profiles", []) or []
    hashtags = body.get("hashtags", []) or []
    posts = body.get("posts", []) or []

    total_items = len(profiles) + len(hashtags) + len(posts)

    driver = _build_driver()
    time.sleep(2)

    profiles_results: List[Dict[str, Any]] = []
    hashtags_results: List[Dict[str, Any]] = []
    posts_results: List[Dict[str, Any]] = []

    try:
        for username in profiles:
            url = f"https://twitter.com/{username}"
            print(f"👤 Varrendo perfil @{username}", file=sys.stderr)
            driver.get(url)
            time.sleep(5)
            data = _collect_tweets(driver, limit)
            profiles_results.append({"id": username, "data": data})

        for tag in hashtags:
            url = f"https://twitter.com/hashtag/{tag}"
            print(f"#️⃣ Varrendo hashtag #{tag}", file=sys.stderr)
            driver.get(url)
            time.sleep(5)
            data = _collect_tweets(driver, limit)
            hashtags_results.append({"id": tag, "data": data})

        for url in posts:
            print(f"💬 Varrendo post {url}", file=sys.stderr)
            driver.get(url)
            time.sleep(5)
            data = _collect_tweets(driver, limit)
            posts_results.append({"id": url, "data": data})

    finally:
        driver.quit()
        print(f"🧹 Sessão encerrada após {total_items} itens.", file=sys.stderr)
        
    return { "sumary": {"total": total_items, "sucess": len(profiles_results + hashtags_results + posts_results)}, "profiles": profiles_results, "hashtags": hashtags_results, "posts": posts_results }
