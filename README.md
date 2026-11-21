# 🛡️ Detektor Phishing URL Berbasis Machine Learning

Proyek ini merupakan final project mata kuliah **Keamanan Informasi** yang bertujuan membangun aplikasi deteksi phishing URL menggunakan machine learning.

Aplikasi menerima input URL dari pengguna, mengekstraksi fitur dari URL tersebut, lalu melakukan klasifikasi apakah URL termasuk **phishing** atau **legitimate** menggunakan algoritme **Random Forest**.

## 👥 Anggota Kelompok

1. [Ismatul Ilmi] — [247006111137]
2. [Nabila Rohmatul Aulia] — [247006111143]
3. [Refa Adinda Putri] — [247006111197]

## 🎯 Tujuan Proyek

- Membangun model machine learning untuk mendeteksi URL phishing.
- Mengekstraksi fitur dari URL sebagai input model.
- Mengevaluasi performa model menggunakan accuracy, precision, recall, dan F1-score.
- Menganalisis false positive dan false negative.
- Membangun aplikasi web berbasis Streamlit untuk deteksi URL phishing.

## 🧠 Teknologi yang Digunakan

- Python 3.11
- Pandas
- NumPy
- Scikit-learn
- Joblib
- Streamlit

## 📁 Struktur Proyek

```text
phishing-detector/
├── data/
│   ├── phishing_dataset.csv
│   └── analisis_kesalahan_model.csv
├── model/
│   └── phishing_model.pkl
├── venv/
├── app.py
├── feature_extractor.py
├── train_model.py
├── analyze_errors.py
├── README.md
└── .gitignore
```

## 📊 Dataset

Dataset yang digunakan adalah **Phishing URL Dataset (URL and Label)** dari Kaggle.

Dataset memiliki kolom:

```text
URL, Domain, label, length
```

Label pada dataset:

| Label | Keterangan |
|---|---|
| benign | URL legitimate |
| phishing | URL phishing |

Setelah preprocessing, label diubah menjadi:

| Label Asli | Label Numerik |
|---|---|
| benign | 0 |
| phishing | 1 |

Total data yang digunakan setelah preprocessing:

| Kategori | Jumlah |
|---|---:|
| Legitimate | 134.850 |
| Phishing | 100.945 |
| Total | 235.795 |

## ⚙️ Fitur URL yang Digunakan

Model menggunakan fitur berikut:

- Panjang URL
- Panjang domain
- Jumlah titik
- Jumlah tanda hubung
- Jumlah garis bawah
- Jumlah tanda tanya
- Jumlah tanda sama dengan
- Jumlah garis miring
- Jumlah angka
- Keberadaan simbol `@`
- Penggunaan HTTPS
- Penggunaan alamat IP
- Keberadaan kata mencurigakan
- Panjang path URL
- Jumlah karakter khusus

Kata mencurigakan yang digunakan antara lain:

```text
login, verify, secure, account, update, confirm,
bank, paypal, signin, password
```

## 🤖 Model Machine Learning

Algoritme yang digunakan adalah **Random Forest Classifier**.

Parameter model:

| Parameter | Nilai |
|---|---|
| n_estimators | 200 |
| max_depth | 20 |
| random_state | 42 |

## 📈 Hasil Evaluasi Model

Model diuji menggunakan 47.159 data testing.

| Metrik | Nilai |
|---|---:|
| Accuracy | 99,57% |
| Precision | 99,88% |
| Recall | 99,12% |
| F1-Score | 99,50% |

Confusion matrix:

|  | Prediksi Legitimate | Prediksi Phishing |
|---|---:|---:|
| Actual Legitimate | 26.946 | 24 |
| Actual Phishing | 177 | 20.012 |

### Analisis Kesalahan

- **False Positive:** 24 URL legitimate diprediksi sebagai phishing.
- **False Negative:** 177 URL phishing diprediksi sebagai legitimate.

False negative lebih berisiko karena URL phishing yang tidak terdeteksi dapat mengarahkan pengguna ke halaman penipuan.

## 🚀 Cara Menjalankan Proyek

### 1. Clone repository

```bash
git clone [https://github.com/username/phishing-detector.git](https://github.com/username/phishing-detector.git)
cd phishing-detector
```

### 2. Buat virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install library

```bash
pip install pandas numpy scikit-learn joblib streamlit
```

### 4. Jalankan aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di:

```text
http://localhost:8501
```

## 🖥️ Cara Menggunakan Aplikasi

1. Masukkan URL pada kolom input.
2. Klik tombol **Periksa URL**.
3. Sistem akan menampilkan hasil prediksi.
4. Aplikasi menampilkan kategori URL dan probabilitas phishing atau legitimate.

Contoh URL untuk pengujian:

```text
[https://www.google.com](https://www.google.com)
```

```text
http://paypal-secure-login.verify-account.com
```

```text
http://192.168.1.1/login
```

## ⚠️ Catatan Etika

Proyek ini hanya digunakan untuk keperluan pembelajaran dan final project mata kuliah Keamanan Informasi. Aplikasi ini tidak menggantikan verifikasi keamanan dari sumber resmi.

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik.
