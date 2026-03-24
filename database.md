# Veritabanı Tabloları ve İlişkileri

## 1. market
- `market_id` → Primary Key
- `market_adi`

### Bağlı olduğu / bağlanan
- `urunler.market_id` → `market.market_id`

---

## 2. urunler
- `id` → Primary Key
- `market_id` → Foreign Key → `market.market_id`
- `urun_ad`
- `urun_url`
- `urun_kategori`
- `eklenme_tarihi`

### Bağlı olduğu / bağlanan
- `urunler.market_id` → `market.market_id`
- `fiyat_zaman_serisi.urun_id` → `urunler.id`
- `anomali.ilgili_urun_id` → `urunler.id`
- `bildirim_kurali.urun_id` → `urunler.id`

---

## 3. fiyat_zaman_serisi
- `kayit_id` → Primary Key
- `urun_id` → Foreign Key → `urunler.id`
- `urun_fiyat`
- `gramaj_degeri`
- `gramaj_birimi`
- `birim_fiyat`
- `kazima_tarihi`

### Bağlı olduğu
- `fiyat_zaman_serisi.urun_id` → `urunler.id`

---

## 4. anomali
- `anomali_id` → Primary Key
- `ilgili_urun_id` → Foreign Key → `urunler.id`
- `eski_degeri`
- `yeni_degeri`
- `anomali_tespit_tarihi`

### Bağlı olduğu
- `anomali.ilgili_urun_id` → `urunler.id`

---

## 5. bildirim_kurali
- `kural_id` → Primary Key
- `urun_id` → Foreign Key → `urunler.id`
- `yuzdesel_artis`
- `esik_deger`
- `bildirim_merkezi`
- `kural_aktif_kontrolu`
- `olusturulma_tarihi`

### Bağlı olduğu / bağlanan
- `bildirim_kurali.urun_id` → `urunler.id`
- `gecmis_bildirimler.tetiklenen_kural` → `bildirim_kurali.kural_id`

---

## 6. gecmis_bildirimler
- `bildirim_id` → Primary Key
- `tetiklenen_kural` → Foreign Key → `bildirim_kurali.kural_id`
- `bildirim_tarihi`
- `basari_testi`
- `mesaj_icerigi`

### Bağlı olduğu
- `gecmis_bildirimler.tetiklenen_kural` → `bildirim_kurali.kural_id`

---

## 7. kullanicilar
- `kullanici_id` → Primary Key
- `telegram_chat_id`

### Bağlı olduğu / bağlanan
- Tanımladığın şemaya göre şu an başka tabloya bağlı değil
