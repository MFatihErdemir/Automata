class NFADurumu:
    def __init__(self, son_durum_mu=False):
        self.gecisler = {}
        self.epsilon_gecisleri = []
        self.son_durum_mu = son_durum_mu
class NFA:
    def __init__(self, baslangic, bitis):
        self.baslangic = baslangic
        self.bitis = bitis


class DuzenliIfadeAyristirici:
    def __init__(self, duzenli_ifade, alfabe):
        self.duzenli_ifade = duzenli_ifade
        self.alfabe = set(alfabe)
        self.konum = 0

    def ayristir(self):
        return self.birlesim_ayristir()

    def birlesim_ayristir(self):
        sol = self.ardisik_ayristir()
        while self.konum < len(self.duzenli_ifade) and self.duzenli_ifade[self.konum] == '+':
            self.konum += 1
            sag = self.ardisik_ayristir()
            baslangic = NFADurumu()
            bitis = NFADurumu(son_durum_mu=True)
            baslangic.epsilon_gecisleri.append(sol.baslangic)
            baslangic.epsilon_gecisleri.append(sag.baslangic)
            sol.bitis.epsilon_gecisleri.append(bitis)
            sag.bitis.epsilon_gecisleri.append(bitis)
            sol.bitis.son_durum_mu = False
            sag.bitis.son_durum_mu = False

            sol = NFA(baslangic, bitis)

        return sol

    def ardisik_ayristir(self):
        nfa_listesi = []

        while self.konum < len(self.duzenli_ifade):
            if self.duzenli_ifade[self.konum] in ['+', ')']:
                break
            nfa_listesi.append(self.yildiz_ayristir())

        if not nfa_listesi:
            baslangic = NFADurumu()
            bitis = NFADurumu(son_durum_mu=True)
            baslangic.epsilon_gecisleri.append(bitis)
            return NFA(baslangic, bitis)

        sonuc = nfa_listesi[0]
        for nfa in nfa_listesi[1:]:
            sonuc.bitis.epsilon_gecisleri.append(nfa.baslangic)
            sonuc.bitis.son_durum_mu = False
            sonuc.bitis = nfa.bitis

        return sonuc

    def yildiz_ayristir(self):
        temel = self.temel_ayristir()

        while self.konum < len(self.duzenli_ifade) and self.duzenli_ifade[self.konum] == '*':
            self.konum += 1

            baslangic = NFADurumu()
            bitis = NFADurumu(son_durum_mu=True)

            baslangic.epsilon_gecisleri.append(temel.baslangic)
            baslangic.epsilon_gecisleri.append(bitis)
            temel.bitis.epsilon_gecisleri.append(temel.baslangic)
            temel.bitis.epsilon_gecisleri.append(bitis)
            temel.bitis.son_durum_mu = False

            temel = NFA(baslangic, bitis)

        return temel

    def temel_ayristir(self):
        if self.konum >= len(self.duzenli_ifade):
            baslangic = NFADurumu()
            bitis = NFADurumu(son_durum_mu=True)
            baslangic.epsilon_gecisleri.append(bitis)
            return NFA(baslangic, bitis)

        karakter = self.duzenli_ifade[self.konum]

        if karakter == '(':
            self.konum += 1
            nfa = self.birlesim_ayristir()
            if self.konum < len(self.duzenli_ifade) and self.duzenli_ifade[self.konum] == ')':
                self.konum += 1
            return nfa

        elif karakter in self.alfabe:
            self.konum += 1
            baslangic = NFADurumu()
            bitis = NFADurumu(son_durum_mu=True)
            if karakter not in baslangic.gecisler:
                baslangic.gecisler[karakter] = []
            baslangic.gecisler[karakter].append(bitis)
            return NFA(baslangic, bitis)

        else:
            self.konum += 1
            baslangic = NFADurumu()
            bitis = NFADurumu(son_durum_mu=True)
            baslangic.epsilon_gecisleri.append(bitis)
            return NFA(baslangic, bitis)


class DuzenliIfade:

    def __init__(self, nfa):
        self.nfa = nfa

    def epsilon_kapanisi(self, durumlar):
        kapanis = set(durumlar)
        yigin = list(durumlar)

        while yigin:
            durum = yigin.pop()
            for sonraki_durum in durum.epsilon_gecisleri:
                if sonraki_durum not in kapanis:
                    kapanis.add(sonraki_durum)
                    yigin.append(sonraki_durum)

        return kapanis

    def kabul_ediyor_mu(self, kelime):
        mevcut_durumlar = self.epsilon_kapanisi([self.nfa.baslangic])

        for karakter in kelime:
            sonraki_durumlar = set()
            for durum in mevcut_durumlar:
                if karakter in durum.gecisler:
                    sonraki_durumlar.update(durum.gecisler[karakter])

            if not sonraki_durumlar:
                return False

            mevcut_durumlar = self.epsilon_kapanisi(sonraki_durumlar)

        return any(durum.son_durum_mu for durum in mevcut_durumlar)


def alfabe_dogrula(duzenli_ifade, alfabe):
    alfabe_kumesi = set(alfabe)
    operatorler = {'*', '+', '(', ')', ' '}

    for karakter in duzenli_ifade:
        if karakter not in operatorler and karakter not in alfabe_kumesi:
            return False, karakter

    return True, None


def kelime_uret(motor, alfabe, maksimum_sayi, maksimum_uzunluk=15):
    kelimeler = []
    kuyruk = ['']
    ziyaret_edilenler = set([''])

    if motor.kabul_ediyor_mu(''):
        kelimeler.append('')

    while kuyruk and len(kelimeler) < maksimum_sayi:
        mevcut = kuyruk.pop(0)

        if len(mevcut) <= maksimum_uzunluk:
            for karakter in alfabe:
                yeni_kelime = mevcut + karakter

                if yeni_kelime not in ziyaret_edilenler:
                    ziyaret_edilenler.add(yeni_kelime)

                    if motor.kabul_ediyor_mu(yeni_kelime):
                        kelimeler.append(yeni_kelime)
                        if len(kelimeler) >= maksimum_sayi:
                            break

                    if len(yeni_kelime) < maksimum_uzunluk:
                        kuyruk.append(yeni_kelime)

    return kelimeler


def main():
    print("DÜZENLI İFADE DİL ÜRETECİ")
    print()

    alfabe_girisi = input("Alfabeyi giriniz S={ ")
    alfabe = [harf.strip() for harf in alfabe_girisi.split(',') if harf.strip()]

    if not alfabe:
        print("Hata: Geçerli bir alfabe giriniz!")
        return

    print(f"Alfabe: S = {{{', '.join(alfabe)}}}")
    print()

    duzenli_ifade = input("Düzenli ifadeyi giriniz: ").strip()

    if not duzenli_ifade:
        print("Hata: Geçerli bir düzenli ifade giriniz!")
        return

    print()

    gecerli_mi, gecersiz_karakter = alfabe_dogrula(duzenli_ifade, alfabe)

    if not gecerli_mi:
        print(f"HATA: '{gecersiz_karakter}' karakteri alfabede bulunmuyor!")
        print("Düzenli ifade S alfabesinden üretilemez.")
        return

    try:
        kelime_sayisi = int(input("L dilinin kaç kelimesini görmek istiyorsunuz? : "))
        if kelime_sayisi <= 0:
            print("Hata: Pozitif bir sayı giriniz!")
            return
    except ValueError:
        print("Hata: Geçerli bir sayı giriniz!")
        return

    print()
    print("Düzenli ifade S alfabesinden üretilebilir. Kelimeleriniz listeleniyor..")

    try:
        ayristirici = DuzenliIfadeAyristirici(duzenli_ifade, alfabe)
        nfa = ayristirici.ayristir()
        Düzenliifade = DuzenliIfade(nfa)

        kelimeler = kelime_uret(Düzenliifade, alfabe, kelime_sayisi)

        if not kelimeler:
            print("Bu düzenli ifade için kelime üretilemedi!")
            return

        print(f"L = {{{', '.join(kelimeler)}}}")

        print("Kelime Kontrolü")


        while True:
            test_kelimesi = input("\nKontrol edilecek kelimeyi giriniz (çıkmak için 'q'): ").strip()

            if test_kelimesi.lower() == 'q':
                break

            if test_kelimesi == '' or test_kelimesi == 'ε':
                test_edilecek_kelime = ''
                gosterilecek_kelime = 'ε'
            else:
                test_edilecek_kelime = test_kelimesi
                gosterilecek_kelime = test_kelimesi

            gecersiz_karakterler = [k for k in test_edilecek_kelime if k not in alfabe]
            if gecersiz_karakterler:
                print(f"Uyarı: '{', '.join(gecersiz_karakterler)}' karakterleri alfabede yok!")

            if Düzenliifade.kabul_ediyor_mu(test_edilecek_kelime):
                print(f" '{gosterilecek_kelime}' kelimesi L diline AİTTİR.")
            else:
                print(f" '{gosterilecek_kelime}' kelimesi L diline AİT DEĞİLDİR.")

    except Exception as hata:
        print(f"Hata oluştu: {hata}")
        return

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()