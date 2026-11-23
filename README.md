# 🛡️ Detektor Phishing URL Berbasis Machine Learning

Aplikasi web untuk mendeteksi URL phishing secara real-time menggunakan model **Random Forest Classifier** dengan akurasi **99.57%**. Dilengkapi sistem autentikasi pengguna, audit trail global, rate limiter berbasis Redis, dan alur reset password lengkap.

> **Final Project — Mata Kuliah Keamanan Informasi**  
> Program Studi Teknik Informatika

---

## 👥 Anggota Kelompok

| Nama | NIM |
|---|---|
| Ismatul Ilmi | 247006111137 |
| Nabila Rohmatul Aulia | 247006111143 |
| Refa Adinda Putri | 247006111197 |

---

## 🌐 Demo Aplikasi

🔗 **[phishing-detector-uas-ki.streamlit.app](https://phishing-detector-uas-ki.streamlit.app)**

---

## 📌 Fitur Lengkap

| Fitur | Keterangan |
|---|---|
| 🔍 **Deteksi URL** | Klasifikasi phishing/legitimate secara real-time dengan probabilitas |
| 🔖 **Domain Whitelist** | 50+ domain terpercaya (Google, GitHub, bank Indonesia, dll) langsung terverifikasi tanpa lewat model |
| 📊 **Visualisasi Hasil** | Probabilitas persentase, progress bar tingkat kepercayaan, detail 15 fitur URL |
| 🕵️ **Audit Trail Global** | Riwayat scan real-time dari semua pengguna, tampil di semua akun |
| 🔐 **Register & Login** | Autentikasi via Supabase Auth dengan bcrypt password hashing |
| 🔒 **Rate Limiter Login** | Proteksi brute force — maks 5x gagal/60 detik per email (Upstash Redis) |
| 📧 **Lupa Password** | Kirim link reset via email dengan rate limit 2x/jam per email |
| 🔑 **Reset Password** | Halaman buat password baru dengan dukungan PKCE flow dan implicit flow |
| 🛡️ **XSS Prevention** | URL di-escape sebelum dirender ke HTML |

---

## 🏗️ Arsitektur Mikroservice

Proyek menggunakan pendekatan **separation of concerns** — setiap lapisan punya tanggung jawab tunggal.

```
phishing-detector/
│
├── app.py                      # Entry point — thin orchestrator (~60 baris)
│
├── config/
│   └── settings.py             # Semua env vars & konstanta (satu titik konfigurasi)
│
├── services/                   # Business logic — tidak ada UI di sini
│   ├── auth_service.py         # Login, register, logout, session, reset password
│   ├── detector_service.py     # Validasi URL, whitelist domain, prediksi ML
│   ├── audit_service.py        # Simpan & ambil riwayat scan ke/dari Supabase
│   └── rate_limiter.py         # Rate limit login & reset password via Upstash Redis
│
├── ui/                         # Presentasi — tidak ada business logic di sini
│   ├── styles.py               # CSS global (glassmorphism dark theme)
│   ├── components.py           # Sidebar, result card, audit trail table
│   ├── auth_page.py            # Halaman login, register, lupa password
│   └── reset_page.py           # Halaman buat password baru (dari link email)
│
├── docs/
│   └── index.html              # Redirect page reset password (GitHub Pages)
│                               # Tangkap token dari URL fragment → redirect ke Streamlit
│
├── feature_extractor.py        # Ekstraksi 15 fitur numerik dari URL
├── train_model.py              # Script training model (jalankan manual)
├── analyze_errors.py           # Analisis false positive & false negative
├── supabase_schema.sql         # SQL schema tabel audit_trail + RLS policies
│
├── model/
│   └── phishing_model.pkl      # Model terlatih — tidak di-push ke GitHub
│
├── data/                       # Tidak di-push ke GitHub
│   ├── phishing_dataset.csv    # Dataset training (dari Kaggle)
│   └── analisis_kesalahan_model.csv
│
├── vercel-redirect/            # Sisa folder (tidak dipakai, digantikan docs/)
├── .env                        # Credentials lokal — tidak di-push ke GitHub
├── .env.example                # Template env vars untuk onboarding
├── requirements.txt            # Dependensi Python
└── .gitignore
```

---

## 📊 Dataset

**Sumber:** [Phishing URL Dataset — Kaggle](https://www.kaggle.com/datasets/harisudhan411/phishing-and-legitimate-urls)

| Kategori | Jumlah |
|---|---:|
| Legitimate (benign) | 134.850 |
| Phishing | 100.945 |
| **Total** | **235.795** |

**Split data:** 80% training (188.636 sampel) / 20% testing (47.159 sampel) dengan `stratify=y` untuk menjaga proporsi kelas.

---

## ⚙️ Ekstraksi Fitur URL (15 Fitur)

Setiap URL diubah menjadi 15 nilai numerik oleh `feature_extractor.py`:

| No | Fitur | Tipe | Keterangan |
|---|---|---|---|
| 1 | `url_length` | Integer | Panjang total URL |
| 2 | `domain_length` | Integer | Panjang bagian domain |
| 3 | `num_dots` | Integer | Jumlah karakter `.` |
| 4 | `num_hyphens` | Integer | Jumlah karakter `-` |
| 5 | `num_underscores` | Integer | Jumlah karakter `_` |
| 6 | `num_question_marks` | Integer | Jumlah karakter `?` |
| 7 | `num_equal_signs` | Integer | Jumlah karakter `=` |
| 8 | `num_slashes` | Integer | Jumlah karakter `/` |
| 9 | `num_digits` | Integer | Jumlah karakter angka |
| 10 | `has_at_symbol` | Binary | Ada simbol `@` (0/1) |
| 11 | `has_https` | Binary | Menggunakan HTTPS (0/1) |
| 12 | `has_ip_address` | Binary | Domain berupa IP address (0/1) |
| 13 | `has_suspicious_word` | Binary | Ada kata mencurigakan (0/1) |
| 14 | `path_length` | Integer | Panjang path URL |
| 15 | `num_special_chars` | Integer | Jumlah karakter non-alfanumerik |

**Kata mencurigakan yang dideteksi:**
`login`, `verify`, `secure`, `account`, `update`, `confirm`, `bank`, `paypal`, `signin`, `password`

---

## 🤖 Model Machine Learning

**Algoritme:** `RandomForestClassifier` dari scikit-learn

| Parameter | Nilai | Alasan |
|---|---|---|
| `n_estimators` | 200 | Lebih banyak pohon = lebih stabil |
| `max_depth` | 20 | Cukup dalam untuk tangkap pola kompleks |
| `random_state` | 42 | Reprodusibilitas hasil |
| `n_jobs` | -1 | Gunakan semua core CPU saat training |

Random Forest dipilih karena tahan terhadap overfitting, tidak memerlukan normalisasi fitur, dan memberikan feature importance yang bisa diinterpretasi.

---

## 📈 Hasil Evaluasi Model

| Metrik | Nilai |
|---|---:|
| **Accuracy** | **99.57%** |
| **Precision** | **99.88%** |
| **Recall** | **99.12%** |
| **F1-Score** | **99.50%** |

**Confusion Matrix (data testing 47.159 sampel):**

```
                    Prediksi Legitimate    Prediksi Phishing
Actual Legitimate        26.946                  24
Actual Phishing             177               20.012
```

| Istilah | Jumlah | Dampak |
|---|---:|---|
| **True Positive** | 20.012 | Phishing terdeteksi dengan benar ✅ |
| **True Negative** | 26.946 | Legitimate terdeteksi dengan benar ✅ |
| **False Positive** | 24 | URL aman salah diklasifikasikan sebagai phishing ⚠️ |
| **False Negative** | 177 | URL phishing lolos tidak terdeteksi ❌ (lebih berisiko) |

False Negative lebih diperhatikan dalam konteks keamanan karena URL phishing yang lolos berpotensi merugikan pengguna.

---

## 🔖 Domain Whitelist

Untuk mengurangi false positive pada domain terkenal, `detector_service.py` mengimplementasikan whitelist dengan **exact match** (bukan suffix match) untuk mencegah serangan subdomain spoofing:

```python
# Contoh: google.com.evil.xyz TIDAK lolos whitelist
# Contoh: evil.google.com TIDAK lolos whitelist (tidak terdaftar)
# Contoh: translate.google.com LOLOS whitelist (terdaftar eksplisit)
```

Domain yang di-whitelist meliputi layanan Google, GitHub, YouTube, Microsoft, LinkedIn, Twitter/X, Instagram, Facebook, Wikipedia, platform developer, e-commerce Indonesia (Tokopedia, Shopee, Bukalapak, Lazada, Gojek, Grab), dan perbankan Indonesia (BCA, Mandiri, BNI, BRI).

URL dari domain terverifikasi mendapat badge **🔖 Domain Terverifikasi** dan tidak diproses oleh model ML.

---

## 🔐 Sistem Keamanan

### Autentikasi (Supabase Auth)
- Password di-hash dengan **bcrypt** secara otomatis oleh Supabase
- Session dikelola via **JWT** — token dikirim terenkripsi (HTTPS)
- JWT expired otomatis setelah 1 jam
- **Row Level Security (RLS)** aktif di Supabase — setiap query divalidasi via `auth.uid()` dari JWT

### Rate Limiter (Upstash Redis)

**Login:**
```
Maks 5 percobaan gagal dalam 60 detik → akun dikunci 60 detik
Per email — tidak bisa dibypass dengan buka tab baru atau VPN
```

**Reset Password:**
```
Maks 2 pengiriman email per jam per email
Mencegah spam email dan melindungi limit Supabase free tier (2 email/jam)
```

**Redis Keys yang digunakan:**
```
rl:attempts:{email}      # counter percobaan login gagal
rl:locked:{email}        # flag kunci login
rl:reset:attempts:{email} # counter pengiriman reset
rl:reset:locked:{email}   # flag kunci reset
```

### Proteksi XSS
URL di-escape sebelum dirender ke HTML:
```python
safe_url = row["url"].replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
```

---

## 🔄 Alur Reset Password

```
1. User klik "Lupa Password?" di halaman login
2. Isi email → klik "Kirim Link Reset"
3. Rate limiter cek: sudah 2x dalam 1 jam? → tolak
4. Supabase kirim email berisi link ke:
   https://great-abel.github.io/phishing-detector/?code=xxx
5. Browser buka GitHub Pages → index.html baca ?code=xxx
6. Redirect ke:
   https://phishing-detector-uas-ki.streamlit.app?code=xxx&type=recovery
7. app.py deteksi ?type=recovery → tampilkan halaman reset
8. exchange_pkce_code(code) → tukar jadi sesi aktif
9. User input password baru → konfirmasi → submit
10. update_password() → password diperbarui di Supabase
11. Redirect ke halaman login ✅
```

Mendukung dua flow Supabase:
- **PKCE flow** (`?code=xxx`) — Supabase versi terbaru
- **Implicit flow** (`#access_token=xxx`) — Supabase versi lama

---

## 🕵️ Audit Trail

Setiap scan URL yang valid tersimpan otomatis ke tabel `audit_trail` di Supabase PostgreSQL. Riwayat ditampilkan secara real-time dan bisa dilihat oleh semua pengguna yang login.

**Kolom tabel:**
| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK ke `auth.users` |
| `user_email` | Text | Email pengguna |
| `url` | Text | URL yang discan |
| `prediction` | Text | `phishing` atau `legitimate` |
| `phishing_pct` | Numeric | Persentase kemungkinan phishing |
| `legit_pct` | Numeric | Persentase kemungkinan legitimate |
| `scanned_at` | Timestamptz | Waktu scan (UTC, ditampilkan WIB) |

---

## 🚀 Cara Menjalankan Lokal

### 1. Clone repository

```bash
git clone https://github.com/ismatul724/phishing-detector.git
cd phishing-detector
```

### 2. Install dependensi

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi environment

```bash
cp .env.example .env
```

Edit `.env` dan isi credentials:

```env
# Supabase — dari: supabase.com → Project → Settings → API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key

# Upstash Redis — dari: console.upstash.com → Redis → REST API
UPSTASH_REDIS_REST_URL=https://your-redis-id.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token-here
```

### 4. Buat tabel di Supabase

Buka **Supabase → SQL Editor → New Query**, paste dan jalankan isi file `supabase_schema.sql`.

### 5. Siapkan model

Model tidak disertakan di repo karena ukurannya besar. Ada dua cara:

**A. Minta file `.pkl` ke anggota kelompok** *(paling cepat)*
```bash
mkdir -p model
# Taruh phishing_model.pkl di folder model/
```

**B. Training ulang dari dataset** *(butuh dataset dari Kaggle)*
```bash
mkdir -p data model
# Download dataset ke data/phishing_dataset.csv
python train_model.py
```

### 6. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka browser: **http://localhost:8501**

---

## 🌐 Cara Deploy ke Streamlit Cloud

1. Fork repo ini ke akun GitHub kamu
2. Buka [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Pilih repo fork kamu → branch `main` → main file `app.py`
4. Klik **Advanced settings → Secrets**, isi:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
UPSTASH_REDIS_REST_URL = "https://your-redis.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "your-token"
```

5. Klik **Deploy**

---

## 🧪 URL untuk Testing

| URL | Ekspektasi |
|---|---|
| `https://www.google.com` | ✅ Legitimate — 🔖 Domain Terverifikasi |
| `https://github.com/ismatul724` | ✅ Legitimate — 🔖 Domain Terverifikasi |
| `https://tokopedia.com` | ✅ Legitimate — 🔖 Domain Terverifikasi |
| `http://paypal-secure-login.verify-account.com` | ⚠️ Phishing |
| `http://192.168.1.1/login?verify=account` | ⚠️ Phishing |
| `https://secure-banking-update.com/signin` | ⚠️ Phishing |

---

## 🛠️ Stack Teknologi

| Kategori | Teknologi | Versi |
|---|---|---|
| **UI Framework** | Streamlit | 1.67.0 |
| **Machine Learning** | scikit-learn | 1.9.1 |
| **Data Processing** | pandas, numpy | Latest |
| **Model Persistence** | joblib | 1.6.0 |
| **Database & Auth** | Supabase (PostgreSQL + GoTrue) | 2.34.1 |
| **Rate Limiter** | Upstash Redis | 1.9.0 |
| **Deployment** | Streamlit Community Cloud | — |
| **Reset PW Redirect** | GitHub Pages (HTML statis) | — |
| **Language** | Python | 3.12+ |

---

## 📁 File Penting

| File | Fungsi |
|---|---|
| `app.py` | Entry point, routing, auth guard |
| `feature_extractor.py` | Ekstraksi 15 fitur dari URL |
| `train_model.py` | Training model (jalankan manual dengan dataset) |
| `analyze_errors.py` | Analisis false positive & false negative |
| `supabase_schema.sql` | DDL tabel audit_trail + RLS policies |
| `docs/index.html` | Halaman redirect token reset password |
| `.env.example` | Template konfigurasi environment |

---

## ⚠️ Catatan Penting

- Hasil prediksi bersifat **probabilistik**, bukan absolut — selalu verifikasi URL mencurigakan dengan sumber keamanan resmi
- Model dilatih dengan fitur berbasis struktur URL, **bukan konten halaman** — phishing yang menggunakan domain mirip tapi tidak ada kata mencurigakan bisa lolos
- Dataset dan file `.pkl` tidak disertakan di repo — lihat bagian "Cara Menjalankan Lokal"
- File `.env` **tidak boleh di-push ke GitHub** — gunakan Streamlit Cloud Secrets untuk deployment
- Proyek ini dibuat untuk keperluan akademik mata kuliah Keamanan Informasi

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik. Dataset berasal dari Kaggle dengan lisensi masing-masing.
