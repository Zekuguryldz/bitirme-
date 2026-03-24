import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)


# ---------- market ----------
def get_markets():
    return supabase.table("market").select("*").execute()

def insert_market(market_adi: str):
    return supabase.table("market").insert({"market_adi": market_adi}).execute()


# ---------- urunler ----------
def get_urunler():
    return supabase.table("urunler").select("*").execute()

def insert_urun(market_id: int, urun_ad: str, urun_url: str, urun_kategori: str):
    return supabase.table("urunler").insert({
        "market_id": market_id,
        "urun_ad": urun_ad,
        "urun_url": urun_url,
        "urun_kategori": urun_kategori,
    }).execute()


# ---------- fiyat_zaman_serisi ----------
def insert_fiyat(urun_id: int, urun_fiyat: float, gramaj_degeri: float, gramaj_birimi: str, birim_fiyat: float):
    return supabase.table("fiyat_zaman_serisi").insert({
        "urun_id": urun_id,
        "urun_fiyat": urun_fiyat,
        "gramaj_degeri": gramaj_degeri,
        "gramaj_birimi": gramaj_birimi,
        "birim_fiyat": birim_fiyat,
    }).execute()

def get_fiyat_gecmisi(urun_id: int):
    return supabase.table("fiyat_zaman_serisi").select("*").eq("urun_id", urun_id).order("kazima_tarihi").execute()


# ---------- anomali ----------
def insert_anomali(ilgili_urun_id: int, eski_degeri: float, yeni_degeri: float):
    return supabase.table("anomali").insert({
        "ilgili_urun_id": ilgili_urun_id,
        "eski_degeri": eski_degeri,
        "yeni_degeri": yeni_degeri,
    }).execute()

def get_anomaliler(urun_id: int):
    return supabase.table("anomali").select("*").eq("ilgili_urun_id", urun_id).execute()


# ---------- kullanicilar ----------
def get_or_create_kullanici(telegram_chat_id: int):
    result = supabase.table("kullanicilar").select("*").eq("telegram_chat_id", telegram_chat_id).execute()
    if result.data:
        return result.data[0]
    insert = supabase.table("kullanicilar").insert({"telegram_chat_id": telegram_chat_id}).execute()
    return insert.data[0]


# ---------- bildirim_kurali ----------
def insert_bildirim_kurali(urun_id: int, kullanici_id: int, yuzdesel_artis: float, esik_deger: float, bildirim_merkezi: str):
    return supabase.table("bildirim_kurali").insert({
        "urun_id": urun_id,
        "kullanici_id": kullanici_id,
        "yuzdesel_artis": yuzdesel_artis,
        "esik_deger": esik_deger,
        "bildirim_merkezi": bildirim_merkezi,
        "kural_aktif_kontrolu": True,
    }).execute()

def get_aktif_kurallar():
    return supabase.table("bildirim_kurali").select("*").eq("kural_aktif_kontrolu", True).execute()


# ---------- gecmis_bildirimler ----------
def insert_gecmis_bildirim(tetiklenen_kural: int, basari_testi: bool, mesaj_icerigi: str):
    return supabase.table("gecmis_bildirimler").insert({
        "tetiklenen_kural": tetiklenen_kural,
        "basari_testi": basari_testi,
        "mesaj_icerigi": mesaj_icerigi,
    }).execute()
