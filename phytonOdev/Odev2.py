
#enumerate fonksiyonunu yapay zekayla ekledim.
class Kitap:
    def __init__(self, ad, yazar, tur):
        self.ad = ad
        self.yazar = yazar
        self.tur = tur


class Kitaplar(Kitap):
    def __init__(self, ad, yazar, adet):
        super().__init__(ad, yazar, tur="Basılı Kitap")
        self.adet = adet

    def odunc_al(self):
        if self.adet > 0:
            self.adet -= 1
            print(f"'{self.ad}' ödünç alındı. Kalan adet: {self.adet}")
        else:
            print("Bu kitap şu an mevcut değil.")

    def iade_et(self):
        self.adet += 1
        print(f"'{self.ad}' iade edildi. Güncel adet: {self.adet}")


class EKitap(Kitap):
    def __init__(self, ad, yazar, boyut_mb):
        super().__init__(ad, yazar, tur="E-Kitap")
        self.boyut_mb = boyut_mb


kutuphane = []

while True:
    print("\n1- Kitap Ekle")
    print("2- Kitapları Listele")
    print("3- Kitap Ödünç Al")
    print("4- Kitap İade Et")
    print("5- Çıkış")

    secim = input("\nSeçim: ")

    if secim == "1":
        ad = input("Kitap adı: ")
        yazar = input("Yazar: ")
        tur = input("Tür (Basılı Kitap / E-Kitap): ")
        if tur == "Basılı Kitap":
            adet = int(input("Adet: "))
            kutuphane.append(Kitaplar(ad, yazar, adet))
        else:
            boyut = float(input("Boyut (MB): "))
            kutuphane.append(EKitap(ad, yazar, boyut))
        print("\nKitap eklendi.")

    elif secim == "2":
        if not kutuphane:
            print("Kütüphane boş.")
        for i, k in enumerate(kutuphane, 1):
            print(f"\n{i}. {k.ad} - {k.yazar} ({k.tur})")
            if isinstance(k, Kitaplar):
                print(f"   Adet: {k.adet}")
            elif isinstance(k, EKitap):
                print(f"   Boyut: {k.boyut_mb} MB")

    elif secim == "3":
        basili = [k for k in kutuphane if isinstance(k,Kitaplar)]
        for i, k in enumerate(basili, 1):
            print(f"{i}. {k.ad} (Adet: {k.adet})")
        sec = int(input("Kitap numarası: ")) - 1
        basili[sec].odunc_al()

    elif secim == "4":
        basili = [k for k in kutuphane if isinstance(k, Kitaplar)]
        for i, k in enumerate(basili, 1):
            print(f"{i}. {k.ad} (Adet: {k.adet})")
        sec = int(input("Kitap numarası: ")) - 1
        basili[sec].iade_et()

    elif secim == "5":
        print("Çıkış yapılıyor.")
        break