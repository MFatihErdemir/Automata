import pandas as pd
df = pd.read_csv("laptop_price_dataset.csv", encoding="utf-8")
print(f"Ham veri: {df.shape[0]} satır × {df.shape[1]} sütun")
df.drop(columns=["Image_URL", "Available_On"], inplace=True)

df.rename(columns={
    "Company"          : "Marka",
    "Product"          : "Laptop_Adi",
    "TypeName"         : "Laptop_Turu",
    "Inches"           : "Ekran_Boyutu_inc",
    "ScreenResolution" : "Cozunurluk",
    "CPU_Company"      : "Islemci_Markasi",
    "CPU_Type"         : "Islemci_Modeli",
    "RAM (GB)"         : "RAM_GB",
    "Memory"           : "Depolama",
    "GPU_Type"         : "GPU_Turu",
    "OpSys"            : "Isletim_Sistemi",
    "Weight (kg)"      : "Agirlik_kg",
    "Price (Euro)"     : "Fiyat_EUR",
}, inplace=True)

df["Fiyat_TRY"] = (df["Fiyat_EUR"] * 50).round(0).astype(int)

gaming_kw = ["rog", "legion", "omen", "predator",
             "nitro", "strix", "zephyrus", "raider"]
df["Gaming_Laptop"] = df["Islemci_Modeli"].apply(
    lambda x: 1 if any(k in str(x).lower() for k in gaming_kw) else 0
)

df.insert(0, "Laptop_ID",
          [f"LPT-{i:04d}" for i in range(1, len(df) + 1)])

df.dropna(subset=["Fiyat_EUR", "RAM_GB", "Ekran_Boyutu_inc"], inplace=True)
df.reset_index(drop=True, inplace=True)
df = df.groupby("Marka", group_keys=False).apply(
    lambda x: x.sample(frac=120 / len(df), random_state=42)
).sample(120, random_state=42).reset_index(drop=True)
print(f"Temizlenmiş veri: {df.shape[0]} satır × {df.shape[1]} sütun")
print(df[["Marka", "RAM_GB", "Fiyat_TRY", "Gaming_Laptop"]].head())
df.to_excel("laptop_dataset.xlsx", index=False)
print("Veri seti kaydedildi: laptop_dataset.xlsx")