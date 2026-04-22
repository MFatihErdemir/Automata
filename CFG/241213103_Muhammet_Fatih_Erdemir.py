def cfg_ayristir(girdi):
    kurallar = {}
    uretimler = girdi.split(',')

    for uretim in uretimler:
        parcalar = uretim.strip().split('-->')
        if len(parcalar) != 2:
            raise ValueError('Geçersiz CFG formatı. "-->" kullanın.')

        non_terminal = parcalar[0].strip()
        alternatifler = [alt.strip() for alt in parcalar[1].split('|')]
        kurallar[non_terminal] = alternatifler

    return kurallar


def terminal_mi(sembol):
    return sembol.islower() and len(sembol) == 1


def kelimeleri_uret(kurallar, baslangic_sembolu, max_derinlik=10):
    tum_kelimeler = []
    def genislet(mevcut, derinlik):
        if derinlik > max_derinlik:
            return

        tum_terminal = all(terminal_mi(c) for c in mevcut)

        if tum_terminal:
            tum_kelimeler.append(mevcut)
            return

        ilk_non_terminal = None
        konum = -1
        for i, c in enumerate(mevcut):
            if not terminal_mi(c):
                ilk_non_terminal = c
                konum = i
                break

        if ilk_non_terminal and ilk_non_terminal in kurallar:
            for uretim in kurallar[ilk_non_terminal]:
                yeni_string = mevcut[:konum] + uretim + mevcut[konum + 1:]
                genislet(yeni_string, derinlik + 1)

    genislet(baslangic_sembolu, 0)

    kelime_sayilari = {}
    for kelime in tum_kelimeler:
        kelime_sayilari[kelime] = kelime_sayilari.get(kelime, 0) + 1

    benzersiz_kelimeler = sorted(set(tum_kelimeler))
    tekrarli_kelimeler = sorted([k for k, v in kelime_sayilari.items() if v > 1])

    return benzersiz_kelimeler, tekrarli_kelimeler, kelime_sayilari

cfg_girdi = input("CFG kurallarını girin: ")
 
try:
    kurallar = cfg_ayristir(cfg_girdi)
    baslangic_sembolu = list(kurallar.keys())[0]

    kelimeler, tekrarli_kelimeler, kelime_sayilari = kelimeleri_uret(kurallar, baslangic_sembolu)

    print("\nÜretilen Kelimeler:")
    print(", ".join(kelimeler))

    if tekrarli_kelimeler:
        print("\nTekrarlanan Kelimeler:")
        for kelime in tekrarli_kelimeler:
            print(f"{kelime} (x{kelime_sayilari[kelime]})")
    else:
        print("\nTekrarlanan kelime yok.")

except Exception as e:
    print(f"Hata: {e}")