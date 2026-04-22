def polish_hesapla(ifade):
    parcalar = ifade.split()
    indeks = [0]

    def hesapla():
        token = parcalar[indeks[0]]
        indeks[0] += 1
        if token in ['+', '-', '*', '/']:
            sol = hesapla()
            sag = hesapla()

            if token == '+':
                return sol + sag
            elif token == '-':
                return sol - sag
            elif token == '*':
                return sol * sag
            elif token == '/':
                return sol / sag
        else:
            return float(token) if '.' in token else int(token)

    return hesapla()



if __name__ == "__main__":

    print("ifadeyi giriniz :")
    kullanici_ifade = input().strip()
    if kullanici_ifade:
        try:
            sonuc = polish_hesapla(kullanici_ifade)
            print(f"Sonuç: {sonuc}")
        except Exception as e:
            print(f"Hata: {e}")