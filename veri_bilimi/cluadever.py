"""
=============================================================================
  TRENDYOL LAPTOP SCRAPER
  Açıklama : Trendyol'dan laptop ürünlerini çeker ve Excel'e kaydeder.
  Kullanım  : pip install requests beautifulsoup4 openpyxl pandas
              python trendyol_laptop_scraper.py
  Not       : Scraping yasal ve etik sınırlar dahilinde kullanılmalıdır.
              robots.txt dosyasına ve site kullanım koşullarına uyunuz.
=============================================================================
"""

import requests
import time
import random
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# ─── Ayarlar ────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.trendyol.com/",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

BASE_URL = "https://www.trendyol.com/sr"
SEARCH_PARAMS = {
    "q": "laptop",
    "qt": "laptop",
    "st": "laptop",
    "os": "1",
}

MAX_PAGES = 10          # Kaç sayfa çekileceği (her sayfada ~24-48 ürün)
DELAY_MIN = 1.5         # İstekler arası minimum bekleme (saniye)
DELAY_MAX = 3.5         # İstekler arası maksimum bekleme (saniye)
OUTPUT_FILE = "trendyol_laptops_raw.xlsx"


# ─── Yardımcı Fonksiyonlar ──────────────────────────────────────────────────

def clean_price(price_text: str) -> float | None:
    """'12.499,99 TL' → 12499.99"""
    try:
        cleaned = re.sub(r"[^\d,.]", "", price_text)
        # Türkçe format: nokta binlik, virgül ondalık
        cleaned = cleaned.replace(".", "").replace(",", ".")
        return float(cleaned)
    except Exception:
        return None


def clean_rating(rating_text: str) -> float | None:
    """'4,5' veya '4.5' → 4.5"""
    try:
        return float(rating_text.replace(",", ".").strip())
    except Exception:
        return None


def clean_review_count(text: str) -> int:
    """'(1.234)' → 1234"""
    try:
        digits = re.sub(r"[^\d]", "", text)
        return int(digits) if digits else 0
    except Exception:
        return 0


# ─── Sayfa Çekme ────────────────────────────────────────────────────────────

def fetch_page(page_number: int) -> BeautifulSoup | None:
    params = {**SEARCH_PARAMS, "pi": page_number}
    try:
        resp = SESSION.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"  [!] Sayfa {page_number} alınamadı: {e}")
        return None


# ─── Ürün Ayrıştırma ────────────────────────────────────────────────────────

def parse_product_cards(soup: BeautifulSoup) -> list[dict]:
    """Bir arama sayfasındaki ürün kartlarını ayrıştırır."""
    products = []

    # Trendyol zaman zaman CSS sınıflarını değiştirebilir;
    # en güvenilir seçici listesi:
    card_selectors = [
        "div.p-card-wrppr",
        "div[data-id]",
        "li.column.col-l-1-4",
    ]

    cards = []
    for sel in card_selectors:
        cards = soup.select(sel)
        if cards:
            break

    for card in cards:
        try:
            # ── Ürün adı ve marka ──────────────────────────────────────────
            brand_el = card.select_one(
                ".prdct-desc-cntnr-ttl, [class*='brand'], [class*='marka']"
            )
            name_el = card.select_one(
                ".prdct-desc-cntnr-name, [class*='product-name'], [class*='urun-adi']"
            )
            brand = brand_el.get_text(strip=True) if brand_el else "Bilinmiyor"
            name  = name_el.get_text(strip=True)  if name_el  else "Bilinmiyor"

            # ── Fiyat ─────────────────────────────────────────────────────
            price_el = card.select_one(
                ".prc-box-dscntd, .prc-box-sllng, [class*='discountedPrice'], [class*='price']"
            )
            price_try = clean_price(price_el.get_text()) if price_el else None

            # ── Orijinal fiyat (indirim öncesi) ───────────────────────────
            orig_el = card.select_one(".prc-box-orgnl, [class*='originalPrice']")
            orig_price_try = clean_price(orig_el.get_text()) if orig_el else None

            # ── Puan ──────────────────────────────────────────────────────
            rating_el = card.select_one(
                ".ratings [title], [class*='rating-score'], [class*='star-rating']"
            )
            if rating_el:
                rating_raw = rating_el.get("title") or rating_el.get_text()
                rating = clean_rating(rating_raw)
            else:
                rating = None

            # ── Yorum sayısı ──────────────────────────────────────────────
            review_el = card.select_one(
                ".ratingCount, [class*='review-count'], [class*='yorum']"
            )
            review_count = clean_review_count(review_el.get_text()) if review_el else 0

            # ── Ürün URL ──────────────────────────────────────────────────
            link_el = card.select_one("a[href]")
            url = ("https://www.trendyol.com" + link_el["href"]
                   if link_el and link_el.get("href", "").startswith("/") else "")

            # ── Ürün ID ───────────────────────────────────────────────────
            product_id = card.get("data-id", "")

            if name != "Bilinmiyor" and price_try:
                products.append({
                    "Urun_ID"        : product_id,
                    "Marka"          : brand,
                    "Laptop_Adi"     : f"{brand} {name}",
                    "Fiyat_TRY"      : price_try,
                    "Orijinal_Fiyat" : orig_price_try,
                    "Indirimde"      : 1 if orig_price_try and orig_price_try > price_try else 0,
                    "Kullanici_Puani": rating,
                    "Yorum_Sayisi"   : review_count,
                    "URL"            : url,
                    "Kaynak"         : "Trendyol",
                    "Cekme_Tarihi"   : datetime.today().strftime("%Y-%m-%d"),
                })

        except Exception as e:
            continue  # Hatalı kartı atla, devam et

    return products


# ─── Detay Sayfasından Özellik Çekme (Opsiyonel) ───────────────────────────

def fetch_product_specs(url: str) -> dict:
    """
    İsteğe bağlı: Ürün detay sayfasından teknik özellikler çeker.
    RAM, işlemci, ekran boyutu vb. için kullanılabilir.
    Hız nedeniyle varsayılan olarak devre dışı; aktif etmek için
    main() içinde use_detail_pages=True yapın.
    """
    specs = {}
    try:
        time.sleep(random.uniform(1.0, 2.0))
        resp = SESSION.get(url, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Özellik tablosu
        spec_rows = soup.select("table.detail-attr-table tr, ul.detail-attr-list li")
        for row in spec_rows:
            cells = row.select("td, span")
            if len(cells) >= 2:
                key   = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                specs[key] = value

    except Exception:
        pass
    return specs


# ─── Ana Fonksiyon ──────────────────────────────────────────────────────────

def main(max_pages: int = MAX_PAGES, use_detail_pages: bool = False):
    print("=" * 60)
    print(" TRENDYOL LAPTOP SCRAPER")
    print(f" Hedef: {max_pages} sayfa | Detay sayfaları: {use_detail_pages}")
    print("=" * 60)

    all_products = []

    for page in range(1, max_pages + 1):
        print(f"\n[{page}/{max_pages}] Sayfa çekiliyor...")
        soup = fetch_page(page)

        if soup is None:
            print(f"  Sayfa {page} atlandı.")
            continue

        products = parse_product_cards(soup)

        if not products:
            print(f"  Sayfa {page}: Ürün bulunamadı, durduruluyor.")
            break

        if use_detail_pages:
            for prod in products:
                if prod["URL"]:
                    specs = fetch_product_specs(prod["URL"])
                    prod.update(specs)

        all_products.extend(products)
        print(f"  +{len(products)} ürün | Toplam: {len(all_products)}")

        #礼貌延迟 – Sunucuyu yormamak için bekle
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        print(f"  {delay:.1f}s bekleniyor...")
        time.sleep(delay)

    # ── Kaydet ──────────────────────────────────────────────────────────────
    if all_products:
        df = pd.DataFrame(all_products)

        # Duplikaları temizle
        before = len(df)
        df.drop_duplicates(subset=["Urun_ID"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        print(f"\nDuplikat temizlendi: {before} → {len(df)} ürün")

        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Kaydedildi: {OUTPUT_FILE}  ({len(df)} satır)")
        print(df[["Marka", "Fiyat_TRY", "Kullanici_Puani", "Yorum_Sayisi"]].describe())
    else:
        print("\nHiç ürün çekilemedi. Lütfen HTML yapısını kontrol edin.")

    return all_products


if __name__ == "__main__":
    main(max_pages=MAX_PAGES, use_detail_pages=False)