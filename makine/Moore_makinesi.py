class MooreMakinesi:
    def __init__(self):
        self.durumlar = []
        self.giris_alfabesi = []
        self.cikis_alfabesi = []
        self.gecis_tablosu = {}
        self.cikis_tablosu = {}
        self.baslangic_durumu = None
        self.simdiki_durum = None

    def girdi_oku(self, dosya_adi="INPUT.TXT"):
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as dosya:
                satirlar = dosya.readlines()

            for satir in satirlar:
                satir = satir.strip()
                if not satir:
                    continue

                if satir.startswith('Q:') or satir.startswith('Q ='):
                    baslangic = satir.find('{')
                    bitis = satir.find('}')
                    if baslangic != -1 and bitis != -1:
                        durumlar_metni = satir[baslangic + 1:bitis]
                        self.durumlar = [durum.strip() for durum in durumlar_metni.split(',')]
                        self.baslangic_durumu = self.durumlar[0]
                        self.simdiki_durum = self.baslangic_durumu

                elif satir.startswith('S') and '=' in satir:
                    baslangic = satir.find('{')
                    bitis = satir.find('}')
                    if baslangic != -1 and bitis != -1:
                        alfabe_metni = satir[baslangic + 1:bitis]
                        self.giris_alfabesi = [harf.strip() for harf in alfabe_metni.split(',')]

                elif satir.startswith('Γ') or satir.startswith('G') or 'Γ' in satir or satir.startswith('Y'):
                    baslangic = satir.find('{')
                    bitis = satir.find('}')
                    if baslangic != -1 and bitis != -1:
                        alfabe_metni = satir[baslangic + 1:bitis]
                        self.cikis_alfabesi = [harf.strip() for harf in alfabe_metni.split(',')]

            print(f"Durumlar: {self.durumlar}")
            print(f"Giriş Alfabesi: {self.giris_alfabesi}")
            print(f"Çıkış Alfabesi: {self.cikis_alfabesi}")
            return True

        except FileNotFoundError:
            print(f"HATA: {dosya_adi} dosyası bulunamadı!")
            return False
        except Exception as hata:
            print(f"HATA: {hata}")
            return False

    def gecis_tablosu_oku(self, dosya_adi="GECISTABLOSU.TXT"):
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as dosya:
                satirlar = dosya.readlines()

            baslik = satirlar[0].strip().split('\t')
            giris_sembolleri = baslik[1:]

            for satir in satirlar[1:]:
                if not satir.strip():
                    continue

                parcalar = satir.strip().split('\t')
                simdiki_durum = parcalar[0]

                if simdiki_durum not in self.gecis_tablosu:
                    self.gecis_tablosu[simdiki_durum] = {}

                for indeks, hedef_durum in enumerate(parcalar[1:]):
                    if indeks < len(giris_sembolleri):
                        giris_sembol = giris_sembolleri[indeks]
                        self.gecis_tablosu[simdiki_durum][giris_sembol] = hedef_durum.strip()

            print(f" Geçiş tablosu yüklendi")
            return True

        except FileNotFoundError:
            print(f"HATA: {dosya_adi} dosyası bulunamadı!")
            return False
        except Exception as hata:
            print(f"HATA: {hata}")
            return False

    def cikis_tablosu_oku(self, dosya_adi="OUTPUT.TXT"):
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as dosya:
                satirlar = dosya.readlines()

            for satir in satirlar[1:]:
                if not satir.strip():
                    continue
                parcalar = satir.strip().split('\t')
                if len(parcalar) >= 2:
                    self.cikis_tablosu[parcalar[0]] = parcalar[1]

            print(f" Çıkış tablosu yüklendi")
            return True

        except FileNotFoundError:
            print(f"HATA: {dosya_adi} dosyası bulunamadı!")
            return False
        except Exception as hata:
            print(f"HATA: {hata}")
            return False

    def simule_et(self, giris_dizisi):
        print("MOORE MAKİNESİ")


        self.simdiki_durum = self.baslangic_durumu
        cikis_dizisi = []

        baslangic_cikis = self.cikis_tablosu.get(self.simdiki_durum, '?')
        print(f"\nBaşlangıç: {self.simdiki_durum} → Çıktı: {baslangic_cikis}")
        cikis_dizisi.append(baslangic_cikis)

        print(f"Giriş Dizisi: {giris_dizisi}\n")

        for adim_no, giris_sembol in enumerate(giris_dizisi, 1):
            onceki_durum = self.simdiki_durum

            if self.simdiki_durum in self.gecis_tablosu and giris_sembol in self.gecis_tablosu[self.simdiki_durum]:
                self.simdiki_durum = self.gecis_tablosu[self.simdiki_durum][giris_sembol]
            else:
                print(f"HATA: Geçiş tanımlı değil!")
                return None

            cikis = self.cikis_tablosu.get(self.simdiki_durum, '?')
            cikis_dizisi.append(cikis)

            print(f"Adım {adim_no}: ({onceki_durum}) --[{giris_sembol}]--> ({self.simdiki_durum}) → Çıktı: {cikis}")

        print(f"\nSon Durum: {self.simdiki_durum}")
        print(f"Çıkış Dizisi: {' '.join(cikis_dizisi)}")
        return cikis_dizisi

    def tablolari_goster(self):
        print("\n")
        print("GEÇİŞ TABLOSU")
        print(f"{'Durum':<10}", end="")
        for sembol in self.giris_alfabesi:
            print(f"{sembol:<10}", end="")
        print()

        for durum in self.durumlar:
            print(f"{durum:<10}", end="")
            for sembol in self.giris_alfabesi:
                hedef = self.gecis_tablosu.get(durum, {}).get(sembol, '-')
                print(f"{hedef:<10}", end="")
            print()
        print("ÇIKIŞ TABLOSU")
        print(f"{'Durum':<10}{'Çıktı':<10}")
        for durum in self.durumlar:
            cikis = self.cikis_tablosu.get(durum, '-')
            print(f"{durum:<10}{cikis:<10}")


def main():
    print("MOORE MAKİNESİ SİMÜLATÖRÜ")

    makine = MooreMakinesi()

    print("\nDosyalar okunuyor...")
    if not makine.girdi_oku() or not makine.gecis_tablosu_oku() or not makine.cikis_tablosu_oku():
        return

    makine.tablolari_goster()

    print("Giriş dizisini girin (örnek: aabba)")
    print("Çıkmak için 'q' yazın")

    while True:
        giris = input("\nGiriş dizisi: ").strip()

        if giris.lower() == 'q':
            print("Program sonlandırılıyor...")
            break

        if not giris:
            print("Lütfen geçerli bir giriş dizisi girin!")
            continue

        gecersiz = [k for k in giris if k not in makine.giris_alfabesi]
        if gecersiz:
            print(f"HATA: Geçersiz semboller: {set(gecersiz)}")
            continue

        makine.simule_et(list(giris))


if __name__ == "__main__":
    main()