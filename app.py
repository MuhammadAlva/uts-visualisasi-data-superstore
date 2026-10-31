"""
Dashboard Interaktif Analisis Penjualan Superstore
Mata Kuliah : Visualisasi Data (UTS Ganjil 2026/2027)
Pembuat     : Muhammad Alva Gustav Al-Fallah (NIM 241041007) - Manajemen Informatika
Dataset     : Superstore Sales Dataset (Kaggle) - lihat README.md
Jalankan    : streamlit run app.py
"""
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------- #
# Konfigurasi halaman & palet warna (konsisten di seluruh dashboard)
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Superstore Sales Dashboard", page_icon="📊", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "superstore_clean.csv"
C_PRIMARY, C_ACCENT, C_POS, C_NEG = "#1f4e79", "#f28e2b", "#2a9d8f", "#e63946"
CAT_COLORS = {"Furniture": "#1f4e79", "Office Supplies": "#f28e2b", "Technology": "#2a9d8f"}
TEMPLATE = "plotly_white"

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem;}
    .insight-box {background:#f4f8fc; border-left:5px solid #1f4e79; padding:.7rem 1rem;
                  border-radius:6px; margin-bottom:.45rem; color:#1b2a3a;}
    </style>
    """,
    unsafe_allow_html=True,
)


def usd(x: float) -> str:
    return f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}"


def style(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(template=TEMPLATE, height=height, margin=dict(l=10, r=10, t=50, b=10),
                      title_font_size=16, legend_title_text="")
    return fig


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Memuat data...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["Order Date", "Ship Date"])
    df["Order Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df


if not DATA_PATH.exists():
    st.error("File data/superstore_clean.csv belum ada. Jalankan `python clean_data.py` terlebih dahulu.")
    st.stop()

df = load_data()

# --------------------------------------------------------------------------- #
# Sidebar: filter interaktif (4 filter)
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("🎛️ Filter Data")
    min_d, max_d = df["Order Date"].min().date(), df["Order Date"].max().date()
    date_range = st.date_input("Rentang tanggal pesanan", value=(min_d, max_d),
                               min_value=min_d, max_value=max_d)
    regions = sorted(df["Region"].unique())
    sel_region = st.multiselect("Wilayah (Region)", regions, default=regions)
    cats = sorted(df["Category"].unique())
    sel_cat = st.multiselect("Kategori Produk", cats, default=cats)
    segs = sorted(df["Segment"].unique())
    sel_seg = st.multiselect("Segmen Pelanggan", segs, default=segs)
    st.caption("Semua grafik & KPI otomatis menyesuaikan filter.")
    st.divider()
    st.markdown("**Muhammad Alva Gustav Al-Fallah**  \nNIM 241041007  \nManajemen Informatika")

if not (isinstance(date_range, tuple) and len(date_range) == 2):
    st.info("Pilih tanggal akhir pada filter rentang tanggal.")
    st.stop()

start, end = date_range
f = df[
    (df["Order Date"].dt.date >= start) & (df["Order Date"].dt.date <= end)
    & df["Region"].isin(sel_region) & df["Category"].isin(sel_cat) & df["Segment"].isin(sel_seg)
]
if f.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Ubah filter di sidebar.")
    st.stop()

# --------------------------------------------------------------------------- #
# Header + KPI cards (6 kartu)
# --------------------------------------------------------------------------- #
st.title("📊 Dashboard Analisis Penjualan Superstore")
st.caption("Memahami produk, wilayah, dan diskon mana yang menggerakkan (atau menggerus) profit.")
st.caption("👤 Dibuat oleh **Muhammad Alva Gustav Al-Fallah** · NIM 241041007 · Prodi Manajemen Informatika · UTS Visualisasi Data 2026/2027")

total_sales, total_profit = f["Sales"].sum(), f["Profit"].sum()
kpis = [
    ("💰 Total Penjualan", usd(total_sales)),
    ("📈 Total Profit", usd(total_profit)),
    ("🎯 Margin Profit", f"{total_profit / total_sales * 100:.1f}%"),
    ("🧾 Jumlah Pesanan", f"{f['Order ID'].nunique():,}"),
    ("👥 Jumlah Pelanggan", f"{f['Customer ID'].nunique():,}"),
    ("🏷️ Rata-rata Diskon", f"{f['Discount'].mean() * 100:.1f}%"),
]
for col, (label, value) in zip(st.columns(len(kpis)), kpis):
    with col.container(border=True):
        st.metric(label, value)


# --------------------------------------------------------------------------- #
# Insight dinamis (storytelling) - dihitung ulang mengikuti filter
# --------------------------------------------------------------------------- #
def build_insights(d: pd.DataFrame) -> list[str]:
    out = []
    sub = d.groupby("Sub-Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    ts = sub["Sales"].idxmax()
    tp = sub["Profit"].idxmax()
    out.append(f"🏆 **{ts}** penjualan terbesar ({usd(sub.loc[ts, 'Sales'])}); "
               f"**{tp}** penyumbang profit terbesar ({usd(sub.loc[tp, 'Profit'])}).")
    losers = sub[sub["Profit"] < 0].sort_values("Profit")
    if len(losers):
        names = ", ".join(f"{i} ({usd(v)})" for i, v in losers["Profit"].items())
        out.append(f"⚠️ **{len(losers)} sub-kategori merugi:** {names}.")
    else:
        out.append("✅ Semua sub-kategori menghasilkan profit pada filter ini.")
    reg = d.groupby("Region").agg(S=("Sales", "sum"), P=("Profit", "sum"))
    reg["M"] = reg["P"] / reg["S"] * 100
    if len(reg) > 1:
        out.append(f"🗺️ Margin tertinggi di **{reg['M'].idxmax()}** ({reg['M'].max():.1f}%), "
                   f"terendah di **{reg['M'].idxmin()}** ({reg['M'].min():.1f}%).")
    mon = d.groupby("Order Month")["Sales"].sum()
    out.append(f"📅 Puncak penjualan bulanan: **{mon.idxmax():%B %Y}** ({usd(mon.max())}).")
    hi, lo = d[d["Discount"] > 0.2], d[d["Discount"] <= 0.2]
    if len(hi) and len(lo):
        out.append(f"🏷️ Transaksi diskon **>20%** merugi {(hi['Profit'] < 0).mean() * 100:.0f}% dari waktu, "
                   f"dibanding {(lo['Profit'] < 0).mean() * 100:.0f}% pada diskon ≤20%.")
    return out


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🏠 Ringkasan", "📦 Produk", "🗺️ Wilayah", "🏷️ Diskon vs Profit", "🗂️ Data"])

# ------------------------------- Tab 1: Ringkasan --------------------------- #
with tab1:
    st.subheader("💡 Insight Utama")
    for line in build_insights(f):
        html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        st.markdown(f"<div class='insight-box'>{html}</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        mon = f.groupby("Order Month").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mon["Order Month"], y=mon["Sales"], name="Penjualan",
                                 mode="lines+markers", line=dict(color=C_PRIMARY, width=3)))
        fig.add_trace(go.Scatter(x=mon["Order Month"], y=mon["Profit"], name="Profit",
                                 mode="lines+markers", line=dict(color=C_ACCENT, width=3)))
        peak = mon.loc[mon["Sales"].idxmax()]
        fig.add_annotation(x=peak["Order Month"], y=peak["Sales"], text="Puncak penjualan",
                           showarrow=True, arrowhead=2, ay=-40)
        fig.update_layout(title="Tren Penjualan & Profit Bulanan", xaxis_title="Bulan",
                          yaxis_title="USD", hovermode="x unified", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(style(fig), use_container_width=True)
    with c2:
        cat = f.groupby("Category", as_index=False)["Sales"].sum()
        fig = px.pie(cat, names="Category", values="Sales", hole=0.55, color="Category",
                     color_discrete_map=CAT_COLORS, title="Proporsi Penjualan per Kategori")
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False)
        st.plotly_chart(style(fig), use_container_width=True)

# ------------------------------- Tab 2: Produk ----------------------------- #
with tab2:
    sub = f.groupby(["Category", "Sub-Category"], as_index=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
    sub["Margin (%)"] = sub["Profit"] / sub["Sales"] * 100
    sub["Status"] = sub["Profit"].apply(lambda v: "Profit" if v >= 0 else "Rugi")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(sub, x="Sales", y="Sub-Category", orientation="h", color="Category",
                     color_discrete_map=CAT_COLORS, title="Penjualan per Sub-Kategori")
        fig.update_yaxes(categoryorder="total ascending", title="")
        fig.update_xaxes(title="Penjualan (USD)")
        st.plotly_chart(style(fig, 460), use_container_width=True)
    with c2:
        fig = px.bar(sub, x="Profit", y="Sub-Category", orientation="h", color="Status",
                     color_discrete_map={"Profit": C_POS, "Rugi": C_NEG}, title="Profit per Sub-Kategori")
        fig.update_yaxes(categoryorder="total ascending", title="")
        fig.update_xaxes(title="Profit (USD)")
        st.plotly_chart(style(fig, 460), use_container_width=True)

    fig = px.scatter(sub, x="Sales", y="Margin (%)", size="Quantity", color="Category",
                     color_discrete_map=CAT_COLORS, hover_name="Sub-Category", size_max=45,
                     title="Penjualan vs Margin Profit (ukuran gelembung = jumlah unit)")
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEG)
    fig.add_annotation(xref="paper", yref="y", x=1, y=0, text="Batas impas (margin 0%)",
                       showarrow=False, yshift=12, xanchor="right", font=dict(color=C_NEG))
    fig.update_xaxes(title="Penjualan (USD)")
    st.plotly_chart(style(fig, 420), use_container_width=True)
    st.caption("📌 Gelembung besar di bawah garis merah = produk laris tetapi merugi → prioritas evaluasi harga/diskon.")

# ------------------------------- Tab 3: Wilayah ---------------------------- #
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        g = f.groupby(["Region", "Category"]).agg(S=("Sales", "sum"), P=("Profit", "sum")).reset_index()
        g["Margin"] = g["P"] / g["S"] * 100
        pivot = g.pivot(index="Region", columns="Category", values="Margin")
        fig = px.imshow(pivot, text_auto=".1f", color_continuous_scale="RdYlGn",
                        color_continuous_midpoint=0, aspect="auto",
                        title="Heatmap Margin Profit (%) — Wilayah × Kategori")
        fig.update_layout(coloraxis_colorbar_title="Margin %")
        st.plotly_chart(style(fig, 420), use_container_width=True)
    with c2:
        st_ = f.groupby("State", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        top = st_.nlargest(10, "Sales")
        fig = px.bar(top, x="Sales", y="State", orientation="h", color="Profit",
                     color_continuous_scale="RdYlGn", color_continuous_midpoint=0,
                     title="10 State dengan Penjualan Tertinggi (warna = profit)")
        fig.update_yaxes(categoryorder="total ascending", title="")
        fig.update_xaxes(title="Penjualan (USD)")
        st.plotly_chart(style(fig, 420), use_container_width=True)

    worst = st_.nsmallest(5, "Profit")
    st.markdown("**🔻 5 State dengan profit terendah:** "
                + ", ".join(f"{r.State} ({usd(r.Profit).replace('$', chr(92) + '$')})" for r in worst.itertuples()))

# ------------------------------- Tab 4: Diskon ----------------------------- #
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        samp = f.sample(min(len(f), 3000), random_state=42)
        fig = px.scatter(samp, x="Discount", y="Profit", color="Category", opacity=0.6,
                         color_discrete_map=CAT_COLORS, title="Diskon vs Profit per Transaksi")
        fig.add_hline(y=0, line_dash="dash", line_color=C_NEG)
        fig.add_vline(x=0.2, line_dash="dot", line_color="gray")
        fig.add_annotation(x=0.2, y=1, yref="paper", text="Diskon 20%", showarrow=False, xanchor="left")
        fig.update_xaxes(tickformat=".0%", title="Diskon")
        fig.update_yaxes(title="Profit (USD)")
        st.plotly_chart(style(fig, 430), use_container_width=True)
    with c2:
        bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1]
        labels = ["0%", "1–10%", "11–20%", "21–30%", "31–50%", ">50%"]
        b = f.assign(Bin=pd.cut(f["Discount"], bins=bins, labels=labels))
        agg = b.groupby("Bin", observed=True, as_index=False)["Profit"].mean()
        agg["Status"] = agg["Profit"].apply(lambda v: "Profit" if v >= 0 else "Rugi")
        fig = px.bar(agg, x="Bin", y="Profit", color="Status",
                     color_discrete_map={"Profit": C_POS, "Rugi": C_NEG},
                     title="Rata-rata Profit per Transaksi menurut Level Diskon")
        fig.update_xaxes(title="Level diskon")
        fig.update_yaxes(title="Rata-rata profit (USD)")
        st.plotly_chart(style(fig, 430), use_container_width=True)
    corr = f["Discount"].corr(f["Profit"])
    st.info(f"📌 Korelasi diskon–profit: **{corr:.2f}** "
            f"({'negatif: makin besar diskon, profit cenderung turun' if corr < 0 else 'tidak negatif pada filter ini'}).")

# ------------------------------- Tab 5: Data ------------------------------- #
with tab5:
    st.write(f"Menampilkan **{len(f):,}** dari {len(df):,} baris sesuai filter.")
    cols = ["Order ID", "Order Date", "Customer Name", "Segment", "Region", "State",
            "Category", "Sub-Category", "Sales", "Quantity", "Discount", "Profit"]
    cols = [c for c in cols if c in f.columns]
    view = f[cols].copy()
    view["Order Date"] = view["Order Date"].dt.date
    view["Sales"], view["Profit"] = view["Sales"].round(2), view["Profit"].round(2)
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Unduh data terfilter (CSV)", f.to_csv(index=False).encode("utf-8"),
                       "superstore_filtered.csv", "text/csv")

st.divider()
st.caption("Sumber data: Superstore Dataset (Kaggle, vivek468). Dibuat dengan Streamlit & Plotly oleh Muhammad Alva Gustav Al-Fallah (NIM 241041007), Manajemen Informatika.")
