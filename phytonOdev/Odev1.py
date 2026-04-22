import random

OYUNCULAR = ["Oyuncu 1", "Oyuncu 2", "Oyuncu 3", "Oyuncu 4"]

def zar_at():
    return random.randint(1, 6)

def basamaklar_esit_mi(sayi):
    return 11 <= sayi <= 99 and (sayi // 10) == (sayi % 10)

while True:
    try:
        surpriz_kutu = int(input("Surpriz kutucugun numarasini girin (10-99): "))
        if 10 <= surpriz_kutu <= 99:
            break
        else:
            print("Lutfen 10 ile 99 arasinda bir sayi girin.")
    except ValueError:
        print("Gecersiz giris.")

ugurlu = {isim: random.randint(1, 6) for isim in OYUNCULAR}
print("\nUgurlu sayilar:")
for isim, sayi in ugurlu.items():
    print(f"  {isim}: {sayi}")

konum   = {isim: 0 for isim in OYUNCULAR}
surpriz = {isim: False for isim in OYUNCULAR}
kazandi = {isim: False for isim in OYUNCULAR}

tur = 1
while True:
    print(f"\n TUR {tur} ")
    for oyuncu in OYUNCULAR:
        if kazandi[oyuncu]:
            continue

        print(f"\n{oyuncu} (konum: {konum[oyuncu]})")

        hak = 2 if surpriz[oyuncu] else 1

        i = 0
        while i < hak:
            zar = zar_at()
            print(f"  Zar: {zar}", end="")

            if zar == ugurlu[oyuncu] and i == 0 and not surpriz[oyuncu]:
                print(" (Attığın zar uğurlu sayına denk geldi  ekstra zar hakki kazandiniz)", end="")
                hak = 2

            print()

            yeni = konum[oyuncu] + zar
            if yeni >= 100:
                konum[oyuncu] = 100
                kazandi[oyuncu] = True
                print(f"  {oyuncu} 100. kutuya ulasti ve KAZANDI!")
                break

            konum[oyuncu] = yeni
            print(f"  {konum[oyuncu]}. kutuya ilerledi.")

            if konum[oyuncu] == surpriz_kutu and not surpriz[oyuncu]:
                surpriz[oyuncu] = True
                print(f"  Sürpriz kutudasın  Artik her turda 2 kez zar atacaksın.")

            if basamaklar_esit_mi(konum[oyuncu]):
                cezali = konum[oyuncu] - 5
                print(f" Üzerinde bulunduğu kutucuğun Numarasının birinci ve ikinci basamağı aynı 5 adım geriye gidiyorsun  {cezali}. kutu.")
                konum[oyuncu] = cezali

            i += 1

        if kazandi[oyuncu]:
            break

    kazanan = None
    for oyuncu in OYUNCULAR:
        if kazandi[oyuncu]:
            kazanan = oyuncu
            break

    if kazanan:
        print(f"\n OYUN BITTI ")
        print(f"Kazanan: {kazanan}")
        break

    tur += 1