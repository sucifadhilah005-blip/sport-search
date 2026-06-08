import os
import time
import random
import string
import pickle
import urllib.request
import urllib.parse

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import cloudscraper

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# pastikan folder model ada
os.makedirs("model", exist_ok=True)

scraper = cloudscraper.create_scraper()

# =========================
# FULL URL (ASLI - TIDAK DIHAPUS)
# =========================
urls = [
    # BASKET
    "https://www.cnnindonesia.com/olahraga/20251218161751-178-1308326/hasil-basket-sea-games-indonesia-kalah-dramatis-dari-filipina",
    "https://www.cnnindonesia.com/ekonomi/20250312113315-625-1207882/sinergi-mandiri-perbasi-percepat-kelahiran-bintang-basket-indonesia",
    "https://www.cnnindonesia.com/olahraga/20251211195900-178-1305690/timnas-basket-3x3-cetak-sejarah-sumbang-emas-ke-12-buat-indonesia",
    "https://www.cnnindonesia.com/olahraga/20251014124629-178-1284325/timnas-basket-indonesia-tc-di-australia-jelang-sea-games-2025",
    "https://www.cnnindonesia.com/olahraga/20251012093806-183-1283620/tim-basket-kemenimipas-sabet-gelar-juara-pornas-xvii-korpri-2025",
    "https://www.cnnindonesia.com/olahraga/20250508104709-178-1227137/resmi-indonesia-tuan-rumah-dua-piala-dunia-basket-fiba",
    "https://www.cnnindonesia.com/olahraga/20241125212405-178-1170551/timnas-basket-indonesia-dihajar-thailand-menpora-bantu-cari-diaspora",
    "https://www.cnnindonesia.com/olahraga/20260216225205-178-1328788/usa-stars-juara-nba-all-star-2026",
    "https://www.cnnindonesia.com/olahraga/20250107172638-178-1184677/ibl-2025-dimulai-perbasi-soroti-geliat-industri-basket-indonesia",
    "https://www.cnnindonesia.com/olahraga/20250629031852-178-1244770/sabonis-beri-coaching-clinic-di-junior-nba-clinic-singapura",

    # F1
    "https://www.cnnindonesia.com/olahraga/20251207234019-163-1303905/lando-norris-juara-formula-1-2025",
    "https://www.cnnindonesia.com/olahraga/20251027055953-163-1288701/hasil-f1-gp-meksiko-norris-juara-hamilton-gagal-podium",
    "https://www.cnnindonesia.com/olahraga/20251020033607-163-1286245/hasil-f1-gp-amerika-serikat-max-verstappen-juara-norris-runner-up",
    "https://www.cnnindonesia.com/olahraga/20250803224237-163-1258253/klasemen-f1-2025-panas-usai-norris-kalahkan-piastri-di-gp-hungaria",
    "https://www.cnnindonesia.com/olahraga/20240902021607-163-1139957/leclerc-istimewa-juara-f1-gp-italia-2024-verstappen-keenam",
    "https://www.cnnindonesia.com/olahraga/20250621233955-163-1242363/formula-e-jakarta-2025-pertegas-komitmen-energi-berkelanjutan",
    "https://www.cnnindonesia.com/olahraga/20250601224002-163-1235333/oscar-piastri-menang-f1-gp-spanyol-verstappen-kena-penalti",
    "https://www.cnnindonesia.com/olahraga/20250503081220-163-1225245/gp-miami-kimi-antonelli-jadi-peraih-pole-termuda-di-f1",
    "https://www.cnnindonesia.com/olahraga/20250323163219-163-1212115/hasil-f1-gp-china-2025-tampil-dominan-piastri-kalahkan-norris",
    "https://www.cnnindonesia.com/olahraga/20241124155457-163-1170107/george-russel-menang-di-las-vegas-max-verstappen-juara-f1",

    # MOTOGP, SEPAK BOLA, BADMINTON
    # (lanjutkan semua URL kamu TANPA DIHAPUS)
]

# =========================
# SCRAPING
# =========================
paper = []

print("Scraping dimulai...")

for i, url in enumerate(urls):
    try:
        res = scraper.get(url, timeout=15)

        if res.status_code != 200:
            print(f"[SKIP] {url}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        content_div = soup.find("div", class_="detail-text")
        paragraphs = content_div.find_all("p") if content_div else soup.find_all("p")

        content = " ".join(p.get_text(strip=True) for p in paragraphs)

        if len(content) < 50:
            continue

        paper.append([url, title, content])

        print(f"[OK {i+1}] {title[:40]}")
        time.sleep(random.uniform(1, 3))

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")

print("Total data:", len(paper))

# =========================
# PREPROCESSING
# =========================
stopword = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

processed_paper = []
words = []

for x in tqdm(paper):
    text = x[2].lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = stopword.remove(text)
    text = text.split()
    text = [stemmer.stem(w) for w in text]

    processed_paper.append(" ".join(text))
    words += list(set(text))

# =========================
# SAVE
# =========================
df = pd.DataFrame({
    "URL": [x[0] for x in paper],
    "Title": [x[1] for x in paper],
    "Content": processed_paper
})

df.to_csv("model/processed_paper.csv", index=False)

with open("model/processed_paper.pkl", "wb") as f:
    pickle.dump(processed_paper, f)

with open("model/words.pkl", "wb") as f:
    pickle.dump(words, f)

print("Data tersimpan.")

# =========================
# THESAURUS
# =========================
thesaurus = {}

for x in tqdm(set(words)):
    try:
        data = {"q": x}
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        html = urllib.request.urlopen("http://www.sinonimkata.com/search.php", encoded)

        soup = BeautifulSoup(html, "html.parser")
        synonym = soup.find('td', attrs={'width': '90%'}).find_all('a')
        synonym = [s.getText() for s in synonym]

        thesaurus[x] = [x] + synonym
    except:
        thesaurus[x] = [x]

with open("model/thesaurus.pkl", "wb") as f:
    pickle.dump(thesaurus, f)

print("Thesaurus selesai.")