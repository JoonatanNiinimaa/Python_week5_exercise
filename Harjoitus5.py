import tkinter as tk
from tkinter import PhotoImage
import random
import threading
import winsound
import numpy as np

root = tk.Tk()
root.title("Ernesti ja Kernesti autiolla saarella")
root.geometry("900x700")

# Kuvien lataaminen ja koon muokkaaminen
try:
    saari_img = PhotoImage(file="saari.png")
    manner_img = PhotoImage(file="mantere.png")
    shark_img = PhotoImage(file="shark.png").subsample(4, 4)
    ernesti_img = PhotoImage(file="erne.png").subsample(4, 4)
    kernesti_img = PhotoImage(file="kerne.png").subsample(4, 4)
    apina_img = PhotoImage(file="monkey.png").subsample(4, 4)
    pohteri_img = PhotoImage(file="pohteri.png").subsample(4, 4)
    eteteri_img = PhotoImage(file="eteteri.png").subsample(4, 4)
    laiva_img = PhotoImage(file="laiva.png").subsample(1, 1)
except Exception as e:
    print(f"Virhe kuvien lataamisessa: {e}")
    root.destroy()
    exit()

# Paikat ikkunassa
canvas = tk.Canvas(root, width=1000, height=500)
canvas.pack()
canvas.create_image(100, 200, image=saari_img)
canvas.create_image(750, 200, image=manner_img)
ernesti_pos = (170, 90)
kernesti_pos = (170, 340)
ernesti = canvas.create_image(*ernesti_pos, image=ernesti_img)
kernesti = canvas.create_image(*kernesti_pos, image=kernesti_img)

# Hätäviesti
hätäviesti = "Ernesti ja Kernesti tässä terve! Olemme autiolla saarella, voisiko joku tulla sieltä sivistyneestä maailmasta hakemaan meidät pois! Kiitos!"
ernesti_sanat = hätäviesti.split()
kernesti_sanat = hätäviesti.split()

apinat = {
    'ernesti': {'kulku': False, 'sana_index': 0, 'saapuneet_sanat': set()},
    'kernesti': {'kulku': False, 'sana_index': 0, 'saapuneet_sanat': set()}
}

ernesti_matka_label = tk.Label(root, text="Ernestin apinan uitu matka: 0 km")
ernesti_matka_label.pack(pady=2)
kernesti_matka_label = tk.Label(root, text="Kernestin apinan uitu matka: 0 km")
kernesti_matka_label.pack(pady=2)

# Pohteri ja Eteteri
pohteri_pos = (700, 90)
eteteri_pos = (700, 340)
pohteri = canvas.create_image(*pohteri_pos, image=pohteri_img)
eteteri = canvas.create_image(*eteteri_pos, image=eteteri_img)

evakuointilaiva_lahtenyt = False
saapuneet_apinat = 0  

# Pohteri ja Eteteri tarkkailee erikseen Ernestin ja Kernestin sanoja
def satamavahdit(apina_data, lahdettaja):
    global evakuointilaiva_lahtenyt

    while not evakuointilaiva_lahtenyt:  # Tarkkaillaan vain, jos laiva ei ole lähtenyt
        if len(apina_data['saapuneet_sanat']) >= 10:
            if not evakuointilaiva_lahtenyt:  
                if lahdettaja == 'ernesti':
                    print("Pohteri: Evakuointilaiva lähtee pohjoispäästä!")
                    laiva_uimaan('ernesti')
                else:
                    print("Eteteri: Evakuointilaiva lähtee eteläpäästä!")
                    laiva_uimaan('kernesti')
                evakuointilaiva_lahtenyt = True  # Merkitään, että laiva on lähtenyt
            break  # Lopetetaan tarkkailu, kun ensimmäinen laiva lähtee
        threading.Event().wait(1)  # Odotetaan ennen seuraavaa tarkistusta


# Apinan lähettäminen uimaan
def laheta_apina_uimaan(lahdettaja, matka_label):
    global ernesti_sanat, kernesti_sanat

    apina_data = apinat[lahdettaja]
    sanat = ernesti_sanat if lahdettaja == 'ernesti' else kernesti_sanat

    if not sanat:
        return

    apina_ref = canvas.create_image(*canvas.coords(ernesti if lahdettaja == 'ernesti' else kernesti), image=apina_img)

    askeleet = 100
    apina_x, apina_y = canvas.coords(apina_ref)
    maali_x = 650

    def ui_askel(askel):
        nonlocal apina_x
        if askel < askeleet:
            # Testataan hain hyökkäys jokaiselta askeleelta
            if np.random.random() < 0.01:  # Hain hyökkäysprosentti
                canvas.coords(apina_ref, -100, -100)
                canvas.create_image(apina_x, apina_y, image=shark_img)
                winsound.PlaySound("shark_sound.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                matka_label.config(text=f"{matka_label.cget('text').split(':')[0]}: Kuollut haialle!")
                apinat[lahdettaja]['kulku'] = False
                return

            apina_x += (maali_x - apina_x) / (askeleet - askel)
            canvas.coords(apina_ref, apina_x, apina_y)
            uitu_matka = askel + 1
            matka_label.config(text=f"{matka_label.cget('text').split(':')[0]}: {uitu_matka} km")

            if askel % 5 == 0:
                winsound.PlaySound("swim_sound.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

            root.after(200, ui_askel, askel + 1)
        else:
            matka_label.config(text=f"{matka_label.cget('text').split(':')[0]}: Perillä!")
            winsound.PlaySound("mantereella.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)  # Apina on perillä
            sana = random.choice(sanat)  # Valitaan satunnainen sana
            apina_data['saapuneet_sanat'].add(sana)
            sanat.remove(sana)  # Poistetaan valittu sana käytettävistä sanoista
            print(f"{lahdettaja}: {sana}")

            # Käynnistetään satamavahdit tarkkailemaan tämän apinan sanoja
            threading.Thread(target=satamavahdit, args=(apina_data, lahdettaja)).start()

    ui_askel(0)

# Laivan luonti mantereelle ja liike saarelle
def laiva_uimaan(lahdettaja):
    laiva_ref = canvas.create_image(750, 150 if lahdettaja == 'ernesti' else 300, image=laiva_img)  # Eri korkeudet
    laiva_x = 750
    laiva_y = 150 if lahdettaja == 'ernesti' else 300
    maali_x = 200
    askeleet = 100

    def ui_askel(askel):
        nonlocal laiva_x
        if askel < askeleet:
            laiva_x -= (laiva_x - maali_x) / (askeleet - askel)
            canvas.coords(laiva_ref, laiva_x, laiva_y)
            root.after(200, ui_askel, askel + 1)
        else:
            canvas.coords(laiva_ref, -100, -100)
            print("Laiva on saapunut autiolle saarelle!")
            winsound.PlaySound("hurraa.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)  # Soita hurraa ääni
            if lahdettaja == 'ernesti':
                print("Ernesti: Vihdoin! Hätäviestini tavoitettiin!")
                print("Kernesti: Hienoa! Minäkin pääsen pakoon tästä saaresta!")
            elif lahdettaja == 'kernesti':
                print("Kernesti: Mahtavaa! Apina viestini toimi!")
                print("Ernesti: Hienoa! Minäkin pääsen pakoon tästä saaresta!")

    ui_askel(0)

def laske_juhlat():
    #Tässä osiossa lasketaan apinoiden määrä molemmilta ja sillä lasketaan keittoon käytetty mustapippurin määrä ja juhlien vierailijoitten määrä
    ernesti_apinoita = len(apinat['ernesti']['saapuneet_sanat'])
    kernesti_apinoita = len(apinat['kernesti']['saapuneet_sanat'])

    ernesti_vieraita = ernesti_apinoita * 4
    kernesti_vieraita = kernesti_apinoita * 4
    ernesti_mustapippuri = ernesti_apinoita * 2  
    kernesti_mustapippuri = kernesti_apinoita * 2 

    if ernesti_vieraita > kernesti_vieraita:
        print(f"Ernestin juhlissa oli suurempi väki! Vieraita oli ernestin juhlissa: {ernesti_vieraita}")
    elif kernesti_vieraita > ernesti_vieraita:
        print(f"Kernestin juhlissa oli suurempi väki! Vieraita oli kernestin juhlissa yhteensä: {kernesti_vieraita}")
    else:
        print(f"Juhlat olivat yhtä suuret molemmissa päissä! Vieraita yhteensä: {ernesti_vieraita} kummassakin.")

    print(f"Ernestin juhlissa kului mustapippuria: {ernesti_mustapippuri} tl")
    print(f"Kernestin juhlissa kului mustapippuria: {kernesti_mustapippuri} tl")
    print(f"Yhteensä mustapippuria oli käytetty {ernesti_mustapippuri + kernesti_mustapippuri} tl juhlissa")

    print(f"Yhteensä juhlissa oli: {ernesti_vieraita + kernesti_vieraita} vierasta.")

def laheta_10_apinaa(lahdettaja):
    def seuraava_apina(jaljella):
        if jaljella > 0:
            laheta_apina_uimaan(lahdettaja, ernesti_matka_label if lahdettaja == 'ernesti' else kernesti_matka_label)
            root.after(1000, seuraava_apina, jaljella - 1)

    apinat[lahdettaja]['kulku'] = True
    seuraava_apina(10)

# Ernestin napit
ernesti_frame = tk.Frame(root)
ernesti_frame.pack(side=tk.LEFT, padx=20)
ernesti_1_apina_button = tk.Button(ernesti_frame, text="Ernesti lähettää 1 apinan uimaan", command=lambda: laheta_apina_uimaan('ernesti', ernesti_matka_label))
ernesti_1_apina_button.pack(pady=5)
ernesti_10_apinaa_button = tk.Button(ernesti_frame, text="Ernesti lähettää 10 apinaa uimaan", command=lambda: laheta_10_apinaa('ernesti'))
ernesti_10_apinaa_button.pack(pady=5)

# Kernestin napit
kernesti_frame = tk.Frame(root)
kernesti_frame.pack(side=tk.RIGHT, padx=20)
kernesti_1_apina_button = tk.Button(kernesti_frame, text="Kernesti lähettää 1 apinan uimaan", command=lambda: laheta_apina_uimaan('kernesti', kernesti_matka_label))
kernesti_1_apina_button.pack(pady=5)
kernesti_10_apinaa_button = tk.Button(kernesti_frame, text="Kernesti lähettää 10 apinaa uimaan", command=lambda: laheta_10_apinaa('kernesti'))
kernesti_10_apinaa_button.pack(pady=5)

# Juhlien laskenta nappi
laske_juhlat_button = tk.Button(text="Laske juhlat", command=laske_juhlat)
laske_juhlat_button.pack(pady=5)

root.mainloop()

# Koodin kanssa ollaan apuna käytetty ChatGPT, varsinkin säikeitten optimoimisessa että ohjelma pyörii oikein.