import sqlite3


def benzerlik(metin1, metin2):
    kume1 = set(metin1.lower().split())
    kume2 = set(metin2.lower().split())

    if len(kume1) == 0 and len(kume2) == 0:
        return 100.0

    ortak_kelime_sayisi = len(kume1.intersection(kume2))
    toplam_kelime_hacmi = len(kume1) + len(kume2)
    oran = (2 * ortak_kelime_sayisi) / toplam_kelime_hacmi

    return round(oran * 100, 2)


def veritabani_islemleri(m1, m2, benzerlik_orani):
    db_adi = "benzerlik_testi.db"

    conn = sqlite3.connect(db_adi)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MetinKarsilastirma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metin1 TEXT,
            metin2 TEXT,
            benzerlik_orani REAL
        )
    ''')

    cursor.execute('''
        INSERT INTO MetinKarsilastirma (metin1, metin2, benzerlik_orani)
        VALUES (?, ?, ?)
    ''', (m1, m2, benzerlik_orani))

    conn.commit()

    cursor.execute('''
        SELECT metin1, metin2, benzerlik_orani 
        FROM MetinKarsilastirma 
        ORDER BY id DESC LIMIT 1
    ''')

    sonuc = cursor.fetchone()

    conn.close()

    return sonuc


def main():
    metin1 = input("Lütfen 1. metni giriniz: ")
    metin2 = input("Lütfen 2. metni giriniz: ")

    oran = benzerlik(metin1, metin2)

    kaydedilen_veri = veritabani_islemleri(metin1, metin2, oran)

    print(f"1. Metin         : {kaydedilen_veri[0]}")
    print(f"2. Metin         : {kaydedilen_veri[1]}")
    print(f"Benzerlik Oranı  : %{kaydedilen_veri[2]}")


main()