# 🚀 Quick Start Guide - Twitter Scraper

## TL;DR - Cara Cepat

```bash
# 1. Set token
export TWITTER_AUTH_TOKEN="your_twitter_auth_token_here"

# 2. Run
./run_scraper.sh
```

## Langkah Lengkap

### 1️⃣ Persiapan (Sekali Saja)

```bash
# Install Python dependencies
pip install pandas openpyxl

# Install Node.js (jika belum)
# Ubuntu/Debian:
sudo apt-get install nodejs npm

# macOS:
brew install node
```

### 2️⃣ Dapatkan Twitter Token

1. Buka https://twitter.com atau https://x.com
2. Login ke akun Anda
3. Tekan F12 (Developer Tools)
4. Pergi ke tab **Application** (Chrome/Edge) atau **Storage** (Firefox)
5. Klik **Cookies** > pilih `https://twitter.com` atau `https://x.com`
6. Cari cookie bernama `auth_token`
7. Copy value-nya (string panjang)

### 3️⃣ Set Token

```bash
export TWITTER_AUTH_TOKEN="paste_token_anda_disini"
```

### 4️⃣ Pastikan File tweet.xlsx Ada

```bash
ls tweets-data/tweet.xlsx
```

Jika tidak ada, upload file tweet.xlsx Anda ke folder `tweets-data/`

### 5️⃣ Jalankan Scraper

```bash
./run_scraper.sh
```

Atau langsung dengan Python:

```bash
python3 get_Data.py
```

## 📂 Struktur File

```
crawling_sosmed/
├── get_Data.py              # Script utama
├── run_scraper.sh           # Wrapper script (recommended)
├── SCRAPER_README.md        # Dokumentasi lengkap
├── QUICK_START.md           # Panduan ini
└── tweets-data/
    ├── tweet.xlsx           # INPUT: Data tweets (required)
    └── {account}_all_replies.csv  # OUTPUT: Hasil scraping
```

## ✅ Checklist

- [ ] Python 3 terinstall (`python3 --version`)
- [ ] Node.js terinstall (`node --version`)
- [ ] Dependencies Python installed (`pip install pandas openpyxl`)
- [ ] File `tweets-data/tweet.xlsx` ada
- [ ] `TWITTER_AUTH_TOKEN` sudah di-set
- [ ] Script `run_scraper.sh` executable (`chmod +x run_scraper.sh`)

## 🎯 Expected Output

```
Account Name: indihome
Total Data: 12

Processing tweet 1/12
✓ Berhasil mengambil data untuk tweet ID: 1989677741894246514

...

✓ Scraping selesai!
✓ Total replies: 133
✓ Data tersimpan di: tweets-data/indihome_all_replies.csv
```

## 🆘 Troubleshooting Cepat

| Error | Solusi |
|-------|--------|
| `TWITTER_AUTH_TOKEN not found` | `export TWITTER_AUTH_TOKEN="your_token"` |
| `Node.js not installed` | Install Node.js dulu |
| `pandas not found` | `pip install pandas openpyxl` |
| `tweet.xlsx not found` | Pastikan file ada di `tweets-data/` |

## 📖 Dokumentasi Lengkap

Baca [SCRAPER_README.md](SCRAPER_README.md) untuk detail lebih lanjut.
