import re
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")
CSV_PATH = "/Users/cmertmarangoz/Downloads/sokmarket_tum_kategoriler_20260323_1604_1425.csv"


# ---------- Birim normalizasyonu ----------
def normalize_gramaj(raw):
    """
    Input:  '1.5 Kg', '750 ml', '4 L', 'Belirtilmemis', '6 adet', None ...
    Output: (gramaj_degeri: float|None, gramaj_birimi: str|None)
    Kurallar:
      kg/kilo      → değeri *1000, birim='g'
      g/gr/gram    → birim='g'
      l/lt/litre   → değeri *1000, birim='ml'
      ml           → birim='ml'
      adet/ad/pk/paket/pcs/piece → birim='adet'
      belirtilmemis/yok/None    → (None, None)
    """
    if raw is None or str(raw).strip() == "":
        return None, None

    raw = str(raw).strip()

    if raw.lower() in ("belirtilmemis", "belirtilmemiş", "-", "yok", "nan"):
        return None, None

    # sayı + birim ayır  (virgüllü ondalık da desteklenir)
    match = re.match(r"^([\d.,]+)\s*([a-zA-ZğüşıöçĞÜŞİÖÇ]+)$", raw)
    if not match:
        return None, None

    sayi_str = match.group(1).replace(",", ".")
    birim_str = match.group(2).lower().strip()

    try:
        sayi = float(sayi_str)
    except ValueError:
        return None, None

    # --- ağırlık ---
    if birim_str in ("kg", "kilo", "kilogram"):
        return sayi * 1000, "g"
    if birim_str in ("g", "gr", "gram"):
        return sayi, "g"

    # --- hacim ---
    if birim_str in ("l", "lt", "litre", "liter"):
        return sayi * 1000, "ml"
    if birim_str in ("ml", "mililitre", "milliliter"):
        return sayi, "ml"

    # --- adet ---
    if birim_str in ("adet", "ad", "pk", "paket", "pcs", "piece", "li", "lu", "lü", "lı"):
        return sayi, "adet"

    return None, None


def birim_fiyat_hesapla(fiyat, gramaj_degeri):
    if gramaj_degeri and gramaj_degeri > 0 and fiyat:
        return round(fiyat / gramaj_degeri, 6)
    return None


# ---------- Ana import ----------
def main():
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip() for c in df.columns]

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # --- Market kaydı ---
    cur.execute(
        "INSERT INTO market (market_adi) VALUES (%s) ON CONFLICT DO NOTHING RETURNING market_id",
        ("ŞOK Market",)
    )
    row = cur.fetchone()
    if row:
        market_id = row[0]
    else:
        cur.execute("SELECT market_id FROM market WHERE market_adi = %s", ("ŞOK Market",))
        market_id = cur.fetchone()[0]
    conn.commit()
    print(f"ŞOK Market → market_id: {market_id}")

    # --- Urunleri ekle, fiyatları kaydet ---
    urun_rows = []
    fiyat_rows = []
    skipped = 0

    for _, row in df.iterrows():
        urun_ad    = str(row.get("Urun Adi", "")).strip()
        urun_url   = str(row.get("URL", "")).strip()
        kategori   = str(row.get("Site Kategori", "")).strip()
        marka      = str(row.get("Marka", "")).strip()
        marka      = None if marka in ("", "nan") else marka
        fiyat_raw  = row.get("Fiyat (TL)")
        gramaj_raw = row.get("Gramaj/Hacim")
        tarih_raw  = str(row.get("Cekim Tarihi", "")).strip()

        if not urun_ad or urun_ad == "nan":
            skipped += 1
            continue

        try:
            fiyat = float(str(fiyat_raw).replace(",", ".")) if fiyat_raw else None
        except ValueError:
            fiyat = None

        gramaj_degeri, gramaj_birimi = normalize_gramaj(gramaj_raw)
        birim_fiyat = birim_fiyat_hesapla(fiyat, gramaj_degeri)

        # tarih parse
        try:
            from datetime import datetime
            kazima_tarihi = datetime.strptime(tarih_raw, "%d.%m.%Y %H:%M:%S")
        except Exception:
            kazima_tarihi = None

        urun_rows.append((market_id, urun_ad, urun_url, kategori, marka, "ŞOK"))
        fiyat_rows.append((fiyat, gramaj_degeri, gramaj_birimi, birim_fiyat, kazima_tarihi))

    # Urunleri toplu ekle, id'leri geri al
    print(f"Inserting {len(urun_rows)} products...")
    urun_ids = []
    for urun, fiyat_data in zip(urun_rows, fiyat_rows):
        cur.execute(
            """INSERT INTO urunler (market_id, urun_ad, urun_url, urun_kategori, urun_marka, market_adi)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING id""",
            urun
        )
        urun_id = cur.fetchone()[0]
        urun_ids.append(urun_id)

        # fiyat_zaman_serisi
        fiyat, gramaj_degeri, gramaj_birimi, birim_fiyat, kazima_tarihi = fiyat_data
        cur.execute(
            """INSERT INTO fiyat_zaman_serisi
               (urun_id, urun_fiyat, gramaj_degeri, gramaj_birimi, birim_fiyat, kazima_tarihi)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (urun_id, fiyat, gramaj_degeri, gramaj_birimi, birim_fiyat, kazima_tarihi)
        )

    conn.commit()
    cur.close()
    conn.close()

    print(f"Done! {len(urun_rows)} urun + fiyat kaydedildi. {skipped} satir atlandı.")


if __name__ == "__main__":
    main()
