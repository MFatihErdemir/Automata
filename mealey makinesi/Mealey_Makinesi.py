

def dosya_oku(dosya_adi):
    try:
        with open(dosya_adi, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Hata: {dosya_adi} bulunamadı!")
        return None


def input_dosyasi_isle(icerik):
    satirlar = [s.strip() for s in icerik.split('\n') if s.strip()]

    durumlar = []
    giris_alfabesi = []
    cikis_alfabesi = []

    for satir in satirlar:
        if satir.startswith('Q:'):
            baslangic = satir.find('{')
            bitis = satir.find('}')
            durumlar = [d.strip() for d in satir[baslangic + 1:bitis].split(',')]

        elif satir.startswith('S='):
            baslangic = satir.find('{')
            bitis = satir.find('}')
            giris_alfabesi = [s.strip() for s in satir[baslangic + 1:bitis].split(',')]

        elif satir.startswith('Γ=') or satir.startswith('G='):
            baslangic = satir.find('{')
            bitis = satir.find('}')
            cikis_alfabesi = [c.strip() for c in satir[baslangic + 1:bitis].split(',')]

    return durumlar, giris_alfabesi, cikis_alfabesi


def gecis_tablosu_isle(icerik):
    satirlar = [s for s in icerik.split('\n') if s.strip()]

    basliklar = satirlar[0].split('\t')
    giris_sembolleri = [b.strip() for b in basliklar[1:] if b.strip()]

    gecis_tablosu = {}

    for i in range(1, len(satirlar)):
        hucre = satirlar[i].split('\t')
        mevcut_durum = hucre[0].strip()

        if not mevcut_durum:
            continue

        gecis_tablosu[mevcut_durum] = {}

        for j in range(1, len(hucre)):
            if j - 1 < len(giris_sembolleri):
                gecis = hucre[j].strip()
                if gecis and gecis != '-':
                    parcalar = gecis.split('/')
                    if len(parcalar) == 2:
                        sonraki_durum = parcalar[0].strip()
                        cikti = parcalar[1].strip()
                        gecis_tablosu[mevcut_durum][giris_sembolleri[j - 1]] = {
                            'sonraki_durum': sonraki_durum,
                            'cikti': cikti
                        }

    return gecis_tablosu


def makineyi_simule_et(durumlar, gecis_tablosu, giris_dizisi):
    mevcut_durum = durumlar[0]
    cikti_dizisi = ""

    print(f"Başlangıç Durumu: {mevcut_durum}")
    print()

    for i, giris_sembol in enumerate(giris_dizisi):
        if mevcut_durum not in gecis_tablosu:
            print(f"Hata: {mevcut_durum} durumu için geçiş tanımlı değil!")
            return None

        if giris_sembol not in gecis_tablosu[mevcut_durum]:
            print(f"Hata: {mevcut_durum} durumundan '{giris_sembol}' girdisi için geçiş tanımlı değil!")
            return None

        gecis = gecis_tablosu[mevcut_durum][giris_sembol]
        sonraki_durum = gecis['sonraki_durum']
        cikti = gecis['cikti']

        print(f"Adım {i + 1}:")
        print(f"  Mevcut Durum: {mevcut_durum}")
        print(f"  Giriş: {giris_sembol}")
        print(f"  Sonraki Durum: {sonraki_durum}")
        print(f"  Çıktı: {cikti}")
        print()

        cikti_dizisi += cikti
        mevcut_durum = sonraki_durum

    print(f"Son Durum: {mevcut_durum}")
    print(f"\nNİHAİ ÇIKTI: {cikti_dizisi} ")

    return cikti_dizisi


def main():

    input_icerik = dosya_oku("INPUT.TXT")
    if not input_icerik:
        return

    durumlar, giris_alfabesi, cikis_alfabesi = input_dosyasi_isle(input_icerik)

    print("Durumlar (Q):", durumlar)
    print("Giriş Alfabesi (Σ):", giris_alfabesi)
    print("Çıkış Alfabesi (Γ):", cikis_alfabesi)
    print()

    gecis_icerik = dosya_oku("GECISDIYAGRAMI.TXT")
    if not gecis_icerik:
        return

    gecis_tablosu = gecis_tablosu_isle(gecis_icerik)

    print("Geçiş Tablosu ")
    for durum in durumlar:
        if durum in gecis_tablosu:
            for giris_sembol, gecis in gecis_tablosu[durum].items():
                print(f"{durum} --{giris_sembol}/{gecis['cikti']}--> {gecis['sonraki_durum']}")
    print()

    giris_dizisi = input("Giriş dizisini girin: ")

    makineyi_simule_et(durumlar, gecis_tablosu, giris_dizisi)


if __name__ == "__main__":
    main()