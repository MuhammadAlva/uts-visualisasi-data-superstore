"""
Pra-pemrosesan data (data cleaning) - Superstore Sales Dataset (Kaggle).

Cara pakai:
1. Unduh dataset dari Kaggle, letakkan file CSV di: data/raw/Sample - Superstore.csv
2. Jalankan:  python clean_data.py
3. Hasil bersih tersimpan di: data/superstore_clean.csv
"""
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/Sample - Superstore.csv")
OUT = Path("data/superstore_clean.csv")

REQUIRED = ["Order ID", "Order Date", "Ship Date", "Customer ID", "Segment", "Region",
            "State", "Category", "Sub-Category", "Sales", "Quantity", "Discount", "Profit"]


def parse_dates(series: pd.Series) -> pd.Series:
    """Format Kaggle: m/d/yyyy. Jika banyak gagal, coba parser otomatis."""
    parsed = pd.to_datetime(series, format="%m/%d/%Y", errors="coerce")
    if parsed.isna().mean() > 0.05:
        parsed = pd.to_datetime(series, errors="coerce")
    return parsed


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"File tidak ditemukan: {RAW}\nUnduh dataset dari Kaggle dulu (lihat README).")

    # File asli memakai encoding Windows, bukan UTF-8
    df = pd.read_csv(RAW, encoding="latin-1")
    print(f"[1] Data mentah      : {df.shape[0]:,} baris x {df.shape[1]} kolom")

    df.columns = df.columns.str.strip()
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        raise SystemExit(f"Kolom wajib tidak ada: {missing_cols}\nKolom tersedia: {list(df.columns)}")

    # Teks: hapus spasi berlebih
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Duplikat & nilai kosong
    n_dup = df.duplicated().sum()
    df = df.drop_duplicates()
    n_before = len(df)
    df = df.dropna(subset=["Order ID", "Order Date", "Sales", "Profit"])
    print(f"[2] Duplikat dibuang : {n_dup} | baris dgn nilai kosong penting dibuang: {n_before - len(df)}")

    # Tipe data
    df["Order Date"] = parse_dates(df["Order Date"])
    df["Ship Date"] = parse_dates(df["Ship Date"])
    df = df.dropna(subset=["Order Date"])
    if "Postal Code" in df.columns:
        df["Postal Code"] = df["Postal Code"].astype(str).str.replace(r"\.0$", "", regex=True)
    for col in ["Sales", "Quantity", "Discount", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Sales", "Quantity", "Discount", "Profit"])

    # Fitur turunan
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Profit Margin (%)"] = (df["Profit"] / df["Sales"] * 100).round(2)
    df["Is Loss"] = df["Profit"] < 0

    df = df.sort_values("Order Date").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    print(f"[3] Data bersih      : {df.shape[0]:,} baris x {df.shape[1]} kolom -> {OUT}")
    print(f"    Rentang tanggal  : {df['Order Date'].min():%d %b %Y} s/d {df['Order Date'].max():%d %b %Y}")
    print(f"    Kolom kategori   : Category, Sub-Category, Segment, Region, State, ...")
    print(f"    Kolom angka      : Sales, Quantity, Discount, Profit, Profit Margin (%)")


if __name__ == "__main__":
    main()
