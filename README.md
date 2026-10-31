# 📊 Dashboard Analisis Penjualan Superstore

**Mata Kuliah:** Visualisasi Data — UTS Ganjil TA 2026/2027
**Nama / NIM:** Muhammad Alva Gustav Al-Fallah / 241041007
**Program Studi:** Manajemen Informatika — Universitas Dirgantara Marsekal Suryadarma

## 🔗 Tautan
- **Live Dashboard:** https://GANTI-DENGAN-URL-STREAMLIT-ANDA.streamlit.app
- **Dataset Kaggle:** https://www.kaggle.com/datasets/vivek468/superstore-dataset-final  *(Superstore Dataset oleh Vivek Chowdhury)*

## 🎯 Latar Belakang
Superstore adalah ritel yang menjual furnitur, perlengkapan kantor, dan teknologi ke tiga segmen pelanggan di empat wilayah AS.
Penjualan yang tinggi belum tentu berarti keuntungan yang tinggi. Dashboard ini membantu manajemen menjawab:
1. Produk dan wilayah mana yang paling menguntungkan?
2. Di mana profit "bocor"?
3. Bagaimana pengaruh diskon terhadap profit?

Dataset: ±9.994 baris, 21 kolom asli (kategorikal: Category, Sub-Category, Segment, Region, State; numerik: Sales, Quantity, Discount, Profit), periode 2014–2017.

## ✨ Fitur Dashboard
| Elemen | Implementasi |
|---|---|
| KPI Cards (6) | Total Penjualan, Total Profit, Margin, Jumlah Pesanan, Jumlah Pelanggan, Rata-rata Diskon |
| Jenis Chart (6) | Line (tren), Bar (komparasi), Donut (proporsi), Scatter/Bubble (korelasi), Heatmap (wilayah × kategori), Bar diverging (profit/rugi) |
| Filter (4) | Rentang tanggal, Wilayah, Kategori, Segmen — memengaruhi semua KPI & grafik |
| Desain | Palet warna konsisten (biru = utama, oranye = pembanding, hijau = profit, merah = rugi), layout lebar berbasis tab |
| Storytelling | Kotak *Insight Utama* yang dihitung otomatis mengikuti filter + anotasi pada grafik |

## 🔍 Key Insights
> ⚠️ **Wajib diverifikasi:** setelah dashboard berjalan, cocokkan setiap poin dengan angka di dashboard (tanpa filter) lalu isi bagian `XX`.

1. **Technology** menyumbang profit terbesar (≈ $XX), sedangkan **Furniture** punya margin terendah meski penjualannya besar.
2. **Tables, Bookcases, dan Supplies** (cek di tab Produk) mengalami **rugi** — laris tetapi menggerus profit.
3. Wilayah **West** unggul pada penjualan & margin; **Central** margin terendah (≈ XX%) karena diskon besar.
4. Transaksi dengan **diskon > 20%** hampir selalu rugi; korelasi diskon–profit **negatif** (≈ -0.XX).
5. Penjualan **memuncak di November–Desember** dan tumbuh dari tahun ke tahun → stok & promo perlu disiapkan sebelum kuartal 4.

## 🗂️ Struktur Repositori
```
├── app.py                  # dashboard Streamlit
├── clean_data.py           # skrip pembersihan data
├── requirements.txt
├── .streamlit/config.toml  # tema warna
└── data/
    ├── raw/                # data mentah dari Kaggle
    └── superstore_clean.csv  # data bersih
```

## 🧹 Pra-pemrosesan Data
Pembacaan dengan encoding `latin-1`, penghapusan spasi & duplikat, validasi nilai kosong, konversi tanggal (m/d/yyyy) dan tipe numerik, penambahan fitur `Year`, `Month`, `Shipping Days`, `Profit Margin (%)`, `Is Loss`.

## 🚀 Menjalankan Secara Lokal
```bash
git clone https://github.com/USERNAME/NAMA-REPO.git
cd NAMA-REPO
pip install -r requirements.txt
# (jika data/superstore_clean.csv belum ada) letakkan CSV Kaggle di data/raw/ lalu:
python clean_data.py
streamlit run app.py
```

## ☁️ Deploy ke Streamlit Community Cloud
1. Push repo ke GitHub (status **Public**).
2. Buka https://share.streamlit.io → **New app** → pilih repo, branch `main`, file `app.py`.
3. Klik **Deploy**, salin URL ke bagian *Tautan* di atas.
