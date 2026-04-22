TR_BUYUK = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
TR_KUCUK = "abcçdefgğhıijklmnoöprsştüuvyz"

class MetinTersleme:
    def __init__(self, metin):
        self.metin = metin

    def tersine_cevir(self):
        return self.metin[::-1]


class SezarSifreleme:
    def __init__(self, metin, anahtar):
        self.metin = metin
        self.anahtar = anahtar

    def sifrele(self):
        sonuc = ""
        for karakter in self.metin:
            if karakter in TR_BUYUK:
                index = TR_BUYUK.index(karakter)
                yeni_index = (index + self.anahtar) % len(TR_BUYUK)
                sonuc += TR_BUYUK[yeni_index]
            elif karakter in TR_KUCUK:
                index = TR_KUCUK.index(karakter)
                yeni_index = (index + self.anahtar) % len(TR_KUCUK)
                sonuc += TR_KUCUK[yeni_index]
            else:
                sonuc += karakter
        return sonuc


class SezarCozme:
    def __init__(self, sifreli_metin):
        self.sifreli_metin = sifreli_metin

    def coz(self, anahtar):
        ters_metin = ""
        for karakter in self.sifreli_metin:
            if karakter in TR_BUYUK:
                index = TR_BUYUK.index(karakter)
                yeni_index = (index - anahtar) % len(TR_BUYUK)
                ters_metin += TR_BUYUK[yeni_index]
            elif karakter in TR_KUCUK:
                index = TR_KUCUK.index(karakter)
                yeni_index = (index - anahtar) % len(TR_KUCUK)
                ters_metin += TR_KUCUK[yeni_index]
            else:
                ters_metin += karakter
        return ters_metin

    def tum_anahtarlari_dene(self):
        print(f"\nŞİFRE ÇÖZME SÜRECİ")
        print(f"Ele Geçirilen Şifreli Metin: {self.sifreli_metin}")
        print(f"\n{'Ters Metin':<35}{'Düz Metin'}")
        print("-" * 60)
        for anahtar in range(len(TR_KUCUK)): 
            ters_metin = self.coz(anahtar)
            duz_metin = ters_metin[::-1]
            print(f"Key {anahtar:<4}: {ters_metin:<27}: {duz_metin}")

print("ŞİFRELEME SÜRECİ")
metin = input("Lütfen bir metin giriniz: ")
anahtar = int(input("Lütfen öteleme sayısı giriniz: "))

tersleme = MetinTersleme(metin)
ters_metin = tersleme.tersine_cevir()
print(f"Ters Çevrilmiş hali: {ters_metin}")

sifreleme = SezarSifreleme(ters_metin, anahtar)
sifreli_metin = sifreleme.sifrele()
print(f"Sezar ile Şifrelenmiş hali: {sifreli_metin}")

cozme = SezarCozme(sifreli_metin)
cozme.tum_anahtarlari_dene()