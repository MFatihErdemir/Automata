"""
=============================================================================
  KAGGLE LAPTOP VERİ SETİ İNDİRME + ANALİZ
  Açıklama : Kaggle'dan laptop veri seti indirir, temizler ve
             hipotez testleri için hazırlar.
  Gereksinim: pip install kaggle pandas openpyxl scipy matplotlib seaborn
  Kullanım  :
    1) https://www.kaggle.com/settings/account → "Create New Token"
    2) İndirilen kaggle.json dosyasını ~/.kaggle/ klasörüne kopyalayın
    3) python kaggle_laptop_analiz.py
=============================================================================
"""

import os
import json
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.family"] = "DejaVu Sans"


# ─── 1. Kaggle'dan İndirme ──────────────────────────────────────────────────

def download_kaggle_dataset(dataset: str = "ionaskel/laptop-prices",
                            dest: str = "./kaggle_data/"):
    """
    Kaggle API ile belirtilen veri setini indirir.
    ~/.kaggle/kaggle.json dosyası gereklidir.
    """
    try:
        import kaggle
        os.makedirs(dest, exist_ok=True)
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(dataset, path=dest, unzip=True)
        print(f"İndirildi: {dest}")
    except ImportError:
        print("kaggle kütüphanesi bulunamadı. Lütfen: pip install kaggle")
    except Exception as e:
        print(f"Kaggle indirme hatası: {e}")
        print("Manuel indirme: https://www.kaggle.com/datasets/ionaskel/laptop-prices")


# ─── 2. Veri Yükleme ve Ön İşleme ──────────────────────────────────────────

def load_and_clean(filepath: str) -> pd.DataFrame:
    """CSV veya Excel dosyasını yükler ve temel temizlik yapar."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Desteklenmeyen dosya formatı: {ext}")

    print(f"\nHam veri: {df.shape[0]} satır × {df.shape[1]} sütun")
    print("Sütunlar:", df.columns.tolist())

    # ── Sütun adlarını standartlaştır ────────────────────────────────────
    rename_map = {
        "company"      : "Marka",
        "product"      : "Laptop_Adi",
        "typename"     : "Kategori",
        "inches"       : "Ekran_Boyutu_inc",
        "screenresolution": "Cozunurluk",
        "cpu"          : "Islemci",
        "ram"          : "RAM_Raw",
        "memory"       : "Depolama_Raw",
        "gpu"          : "GPU",
        "opsys"        : "Isletim_Sistemi",
        "weight"       : "Agirlik_Raw",
        "price_euros"  : "Fiyat_EUR",
        "price"        : "Fiyat",
    }
    df.columns = df.columns.str.lower().str.strip()
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns},
              inplace=True)

    # ── RAM → sayısal ────────────────────────────────────────────────────
    if "RAM_Raw" in df.columns:
        df["RAM_GB"] = pd.to_numeric(
            df["RAM_Raw"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
        )

    # ── Ağırlık → sayısal ────────────────────────────────────────────────
    if "Agirlik_Raw" in df.columns:
        df["Agirlik_kg"] = pd.to_numeric(
            df["Agirlik_Raw"].astype(str)
              .str.replace("kg", "", case=False)
              .str.strip(), errors="coerce"
        )

    # ── Fiyat → sayısal ──────────────────────────────────────────────────
    fiyat_col = "Fiyat_EUR" if "Fiyat_EUR" in df.columns else "Fiyat"
    if fiyat_col in df.columns:
        df["Fiyat"] = pd.to_numeric(df[fiyat_col], errors="coerce")

    # ── Binary değişkenler ────────────────────────────────────────────────
    if "GPU" in df.columns:
        df["Ayrik_GPU"] = df["GPU"].apply(
            lambda x: 0 if str(x).lower() in ("intel", "amd radeon", "") else 1
        )

    gaming_kw = ["gaming", "rog", "legion", "omen", "predator",
                 "nitro", "aorus", "strix", "raider"]
    if "Laptop_Adi" in df.columns:
        df["Gaming_Laptop"] = df["Laptop_Adi"].apply(
            lambda x: 1 if any(k in str(x).lower() for k in gaming_kw) else 0
        )

    # ── Eksik değerleri düşür ─────────────────────────────────────────────
    essential = [c for c in ["Fiyat", "RAM_GB", "Ekran_Boyutu_inc"] if c in df.columns]
    df.dropna(subset=essential, inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"Temizlendi: {df.shape[0]} satır × {df.shape[1]} sütun")
    return df


# ─── 3. Keşifsel Veri Analizi (EDA) ─────────────────────────────────────────

def run_eda(df: pd.DataFrame):
    """Temel istatistikleri ve görsel EDA çıkarır."""
    print("\n" + "=" * 50)
    print("KEŞIFSEL VERİ ANALİZİ")
    print("=" * 50)

    num_cols = df.select_dtypes(include="number").columns.tolist()
    print("\nTemel İstatistikler:")
    print(df[num_cols].describe().round(2))

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Laptop Veri Seti – EDA", fontsize=15, fontweight="bold")

    plot_cols = [c for c in ["Fiyat", "RAM_GB", "Ekran_Boyutu_inc",
                              "Agirlik_kg", "Batarya_Wh", "Kullanici_Puani"]
                 if c in df.columns]

    for ax, col in zip(axes.flat, plot_cols):
        ax.hist(df[col].dropna(), bins=25, color="#2E75B6", edgecolor="white", alpha=0.85)
        ax.set_title(col)
        ax.set_xlabel(col)
        ax.set_ylabel("Frekans")
        mean_val = df[col].mean()
        ax.axvline(mean_val, color="red", linestyle="--", linewidth=1.2,
                   label=f"Ort: {mean_val:.1f}")
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig("eda_histograms.png", bbox_inches="tight")
    plt.close()
    print("EDA grafiği kaydedildi: eda_histograms.png")


# ─── 4. Hipotez Testleri ─────────────────────────────────────────────────────

def run_hypothesis_tests(df: pd.DataFrame):
    print("\n" + "=" * 50)
    print("HİPOTEZ TESTLERİ")
    print("=" * 50)
    alpha = 0.05

    # ─── H1: RAM ↔ Fiyat Korelasyonu ────────────────────────────────────
    if "RAM_GB" in df.columns and "Fiyat" in df.columns:
        print("\n[H1] RAM_GB ↔ Fiyat Pearson Korelasyonu")
        x = df["RAM_GB"].dropna()
        y = df.loc[x.index, "Fiyat"].dropna()
        x, y = x.align(y, join="inner")
        r, p = stats.pearsonr(x, y)
        print(f"  r = {r:.4f},  p = {p:.4e}")
        print(f"  → {'H₀ REDDEDİLİR' if p < alpha else 'H₀ REDDEDİLEMEZ'} (α={alpha})")
        if p < alpha and r > 0:
            print("  ✓ Bulgu: RAM arttıkça fiyat anlamlı olarak artmaktadır.")

    # ─── H2: Ayrık GPU ↔ Fiyat t-Testi ─────────────────────────────────
    if "Ayrik_GPU" in df.columns and "Fiyat" in df.columns:
        print("\n[H2] Ayrık GPU ↔ Fiyat Bağımsız t-Testi")
        g0 = df[df["Ayrik_GPU"] == 0]["Fiyat"].dropna()
        g1 = df[df["Ayrik_GPU"] == 1]["Fiyat"].dropna()
        if len(g0) > 1 and len(g1) > 1:
            t, p = stats.ttest_ind(g0, g1, equal_var=False)
            print(f"  Entegre GPU ort.: {g0.mean():.2f}  |  Ayrık GPU ort.: {g1.mean():.2f}")
            print(f"  t = {t:.4f},  p = {p:.4e}")
            print(f"  → {'H₀ REDDEDİLİR' if p < alpha else 'H₀ REDDEDİLEMEZ'} (α={alpha})")

    # ─── H3: İşletim Sistemi ↔ Fiyat ANOVA ─────────────────────────────
    if "Isletim_Sistemi" in df.columns and "Fiyat" in df.columns:
        print("\n[H3] İşletim Sistemi ↔ Fiyat ANOVA")
        groups = [grp["Fiyat"].dropna().values
                  for _, grp in df.groupby("Isletim_Sistemi")
                  if len(grp) > 1]
        if len(groups) >= 2:
            f, p = stats.f_oneway(*groups)
            print(f"  F = {f:.4f},  p = {p:.4e}")
            print(f"  → {'H₀ REDDEDİLİR' if p < alpha else 'H₀ REDDEDİLEMEZ'} (α={alpha})")
            print("  Grup ortalamaları:")
            print(df.groupby("Isletim_Sistemi")["Fiyat"].mean().sort_values(ascending=False)
                    .apply(lambda v: f"  {v:,.2f}"))

    # ─── H4: Ağırlık ↔ Batarya Korelasyonu ──────────────────────────────
    if "Agirlik_kg" in df.columns and "Batarya_Wh" in df.columns:
        print("\n[H4] Ağırlık ↔ Batarya Pearson Korelasyonu")
        x = df["Agirlik_kg"].dropna()
        y = df.loc[x.index, "Batarya_Wh"].dropna()
        x, y = x.align(y, join="inner")
        if len(x) > 5:
            r, p = stats.pearsonr(x, y)
            print(f"  r = {r:.4f},  p = {p:.4e}")
            print(f"  → {'H₀ REDDEDİLİR' if p < alpha else 'H₀ REDDEDİLEMEZ'} (α={alpha})")

    # ─── H5: Gaming ↔ Ekran Boyutu t-Testi ──────────────────────────────
    if "Gaming_Laptop" in df.columns and "Ekran_Boyutu_inc" in df.columns:
        print("\n[H5] Gaming ↔ Ekran Boyutu t-Testi")
        g0 = df[df["Gaming_Laptop"] == 0]["Ekran_Boyutu_inc"].dropna()
        g1 = df[df["Gaming_Laptop"] == 1]["Ekran_Boyutu_inc"].dropna()
        if len(g0) > 1 and len(g1) > 1:
            t, p = stats.ttest_ind(g0, g1, equal_var=False)
            print(f"  Non-gaming ort.: {g0.mean():.2f}\"  |  Gaming ort.: {g1.mean():.2f}\"")
            print(f"  t = {t:.4f},  p = {p:.4e}")
            print(f"  → {'H₀ REDDEDİLİR' if p < alpha else 'H₀ REDDEDİLEMEZ'} (α={alpha})")


# ─── 5. Korelasyon Isı Haritası ──────────────────────────────────────────────

def plot_correlation_heatmap(df: pd.DataFrame):
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] < 2:
        return
    corr = num_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(12, 9))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlBu",
                center=0, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Sayısal Değişkenler Korelasyon Matrisi", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("korelasyon_matrisi.png", bbox_inches="tight")
    plt.close()
    print("Korelasyon matrisi kaydedildi: korelasyon_matrisi.png")


# ─── ANA AKIŞ ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # Kaggle veri seti indirme (opsiyonel)
    # download_kaggle_dataset()

    # Dosya yolu: komut satırından alınabilir ya da sabit tanımlanabilir
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Bu çalışmada hazır oluşturulan veri setini kullan
        filepath = "laptop_dataset.xlsx"

    if not os.path.exists(filepath):
        print(f"Dosya bulunamadı: {filepath}")
        print("Kullanım: python kaggle_laptop_analiz.py <dosya_yolu>")
        sys.exit(1)

    df = load_and_clean(filepath)
    run_eda(df)
    run_hypothesis_tests(df)
    plot_correlation_heatmap(df)

    print("\n✓ Tüm analizler tamamlandı.")