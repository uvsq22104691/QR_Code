from PIL import Image, ImageTk
import tkinter as tk
import tkinter.filedialog as fd
import os


# Fonction
def nbrLig(mat):
    ''' Retourne le nombre de ligne dans la matrice'''
    return len(mat)


def nbrCol(mat):
    ''' Retourne le nombre de colonne dans la matrice'''
    return len(mat[0])


def saving(matPix, filename):
    ''' sauvegarde l'image contenue dans matpix dans le fichier filename
        utiliser une extension png pour que la fonction fonctionne sans perte
        d'information
    '''
    toSave = Image.new(mode="1", size=(nbrCol(matPix), nbrLig(matPix)))
    for i in range(nbrLig(matPix)):
        for j in range(nbrCol(matPix)):
            toSave.putpixel((j, i), matPix[i][j])
    toSave.save(filename)


def loading(filename):
    ''' Charge l'image contenue dans le fichier filename et renvoie une
        matrice de pixels (0, 1)
    '''
    global L_image, img
    toLoad = Image.open(filename)

    mat = [[0] * toLoad.size[0] for _ in range(toLoad.size[1])]
    for i in range(toLoad.size[1]):
        for j in range(toLoad.size[0]):
            mat[i][j] = 0 if toLoad.getpixel((j, i)) == 0 else 1

    toLoad = toLoad.resize((500, 500))
    img = ImageTk.PhotoImage(toLoad)
    L_image['image'] = img

    return mat


def coin_QC():
    ''' sRetourne la matrice représentant les coins de la matrice du QR Code'''
    mat = [[0] * 7 for _ in range(7)]

    for i in range(7):
        for j in range(7):
            if (i in [1, 5] and 0 < j < 6) or (j in [1, 5] and 0 < i < 6):
                mat[i][j] = 1
    return mat


def rotation(sens, mat):
    ''' Retourne la matrice tournée dans le sens
        (
            0: horaire,
            1: anti-horaire,
            2: 180°
        )
    '''
    if sens == 0:
        return [
            [
                mat[-(i + 1)][j] for i in range(nbrLig(mat))
            ] for j in range(nbrCol(mat))
        ]
    elif sens == 1:
        return [
            [
                mat[i][-(j + 1)] for i in range(nbrLig(mat))
            ] for j in range(nbrCol(mat))
        ]

    return [
        [
            mat[-(i + 1)][-(j + 1)] for i in range(nbrLig(mat))
        ] for j in range(nbrCol(mat))
    ]


def verif_sens_QC(mat):
    ''' Retourne la matrice représentant le QR Code dans le bon sens'''
    coin = coin_QC()
    for i in range(7):
        for j in range(7):
            if coin[i][j] != mat[i][j]:
                mat = rotation(2, mat)
                return mat
            if coin[i][j] != mat[i][-(j + 1)]:
                mat = rotation(0, mat)
                return mat
            if coin[i][j] != mat[-(i + 1)][j]:
                mat = rotation(1, mat)
                return mat
    return mat


def verif_ligne(mat):
    ''' Vérifie que les lignes horizontales et verticales reliant les coins du
        QR Code sont bien présentes
    '''
    verif = True
    for i in range(11):
        if i % 2 == 0:
            if mat[6][7 + i] % 2 == 0:
                verif = False
            if mat[7 + i][6] % 2 == 0:
                verif = False
        else:
            if mat[6][7 + i] % 2 != 0:
                verif = False
            if mat[7 + i][6] % 2 != 0:
                verif = False

    return verif


def correction_hamming(liste):
    ''' Applique la correction de Hamming sur la liste de bits et retourne la
        liste des bits de message corrigée
    '''
    m1, m2, m3, m4, c1, c2, c3 = liste
    d_err = {
        1: 4,
        2: 5,
        3: 0,
        4: 6,
        5: 1,
        6: 2,
        7: 3,
    }
    err = 0
    err += 1 if int(c1 != (m1 + m2 + m4) % 2) else 0
    err += 2 if int(c2 != (m1 + m3 + m4) % 2) else 0
    err += 4 if int(c3 != (m2 + m3 + m4) % 2) else 0

    if err != 0:
        liste[d_err[err]] = 0 if liste[d_err[err]] == 1 else 1
    return liste[:4]


def extraire_donnee(mat):
    ''' Retourne la matrice des bits qui code les données'''
    return [ligne[-14:] for ligne in mat[-16:]]


def lire_nb_nbloc(mat):
    ''' Retourne le nombre de blocs de données dans le QR Code'''
    return int("".join([str(mat[i][0]) for i in range(13, 18)]), 2)


def lire_donnee(mat, nbBloc=16):
    ''' Retourne la liste de liste des blocs de données de 14 bits'''
    liste = []
    for i in range(0, nbBloc, 2):
        m = mat[::-1][i:i + 2][::-1]
        m = [mat[-14:] for mat in m]

        if i % 4 == 0:
            m1 = [m[j % 2][-((j - 1) // 2 + 1)] for j in range(1, 15)]
            m2 = [m[j % 2][-((j - 1) // 2 + 8)] for j in range(1, 15)]
        else:
            m1 = [m[(j + 1) % 2][j // 2] for j in range(0, 14)]
            m2 = [m[(j + 1) % 2][j // 2 + 7] for j in range(0, 14)]

        liste.append(m1)
        liste.append(m2)
    return liste[:nbBloc]


def lire_type_donnee(mat):
    ''' Retourne le type de données'''
    type = mat[24][8]
    return type


def interpreter_ascii(data):
    ''' Affiche le message interprété en ASCII'''
    global L_info
    s = ""
    for bloc in [liste for liste in data]:
        tmp = ''.join(
            map(
                str,
                correction_hamming(bloc[:7]) + correction_hamming(bloc[7:])
            )
        )
        tmp = int(tmp, 2)
        s += chr(tmp)
    L_info['text'] = L_info['text'] + f"\nMessage:\t\t{s}"


def interpreter_num(data):
    ''' Affiche le message interprété en hexadécimal'''
    global L_info
    s = ""
    for bloc in [liste for liste in data]:
        tmp = ''.join(
            map(
                str,
                correction_hamming(bloc[:7]) + correction_hamming(bloc[7:])
            )
        )
        s += hex(int(tmp, 2))[2:].upper() + " "
    s = s[:-1]
    L_info['text'] = L_info['text'] + f"\nMessage:\t\t{s}"


def interpreter(data, dataType):
    '''Interprète le message en fonction du type de données'''
    global L_info
    if dataType == 1:
        L_info['text'] = L_info['text'] + "\nType:\t\tascii"
        interpreter_ascii(data)
    else:
        L_info['text'] = L_info['text'] + "\nType:\t\tnumérique"
        interpreter_num(data)


def lire_type_filtre(mat):
    '''Retourne le type de filtre'''
    filtre = str(mat[22][8]) + str(mat[23][8])
    return int(filtre, 2)


def applique_filtre(data, filtre):
    '''Applique le filtre a la matrice des données'''
    global L_info
    if filtre == 0:
        L_info['text'] = "Filtre:\t\taucun filtre"
        return data
    elif filtre == 1:
        L_info['text'] = "Filtre:\t\tdamier"
        for y in range(16):
            for x in range(14):
                data[y][x] = data[y][x] ^ (y + x) % 2
        return data
    elif filtre == 2:
        L_info['text'] = "Filtre:\t\tbandes horizontales"
        for y in range(16):
            for x in range(14):
                data[y][x] = data[y][x] ^ y % 2
        return data
    elif filtre == 3:
        L_info['text'] = "Filtre:\t\tbandes verticales"
        for y in range(16):
            for x in range(14):
                data[y][x] = data[y][x] ^ x % 2
        return data


def ouvrir_QR():
    '''Ouvre une fenêtre pour choisir un QR code à lire, l'affiche,
        l'interprète et affiche les informations
        (type de données, type de filtre, message)
    '''
    f = fd.askopenfile(
        initialdir=os.getcwd() + "/Exemples/",
        title="charger un QR Code",
        filetypes=(("fichier PNG", "*.png"),)
    )
    if f is None:
        return

    filename = f.name
    f.close()

    mat = loading(filename)
    mat = verif_sens_QC(mat)

    data = extraire_donnee(mat)
    filtre = lire_type_filtre(mat)
    dataType = lire_type_donnee(mat)
    nbBloc = lire_nb_nbloc(mat)

    data = applique_filtre(data, filtre)
    data = lire_donnee(data, nbBloc)
    interpreter(data, dataType)


####################
# Création QR Code #
####################


def to_hamming(string):
    ''' Retourne la liste des bits de la chaîne de caractères en utilisant le
        codage hamming
    '''
    m1, m2, m3, m4 = map(int, list(string))
    string += f"{(m1 + m2 + m4) % 2}"
    string += f"{(m1 + m3 + m4) % 2}"
    string += f"{(m2 + m3 + m4) % 2}"
    return list(map(int, list(string)))


def del_fen_QR():
    ''' Supprime la fenêtre de l'interface graphique'''
    global fen_QR
    fen_QR.destroy()
    del fen_QR


def creer_QR(save):
    ''' Crée un QR code à partir du message, du type de données et du type de
        filtre choisis
    '''
    global L_image, L_info, img, message, filtre, dataType
    dType = dataType.get()
    f = filtre.get()
    data = list(message.get()[:16])
    data = [bin(ord(d))[2:] for d in data]
    data = ["0" * (8 - len(d)) + d if len(d) != 8 else d for d in data]
    data = [d[::-1] for d in data]
    data = [to_hamming(d[:4]) + to_hamming(d[4:]) for d in data]

    n = len(data)
    nb_bloc = len(message.get()[:16])
    m = [[1] * 14 for _ in range(16)]

    for i in range(1, 2 * ((n + 1) // 2) + 1, 2):
        if i % 4 == 1:
            for j in range(14):
                m[-(i + j % 2)][-(j // 2 + 1)] = data[i - 1][j]
                if i < len(data):
                    m[-(i + j % 2)][-(j // 2 + 8)] = data[i][j]
        else:
            for j in range(14):
                m[-(i + j % 2)][j // 2] = data[i - 1][j]
                if i < len(data):
                    m[-(i + j % 2)][j // 2 + 7] = data[i][j]

    m = applique_filtre(m, f)

    mat = loading('Exemples/frame.png')
    for i in range(1, n % 2 + n + 1):
        for j in range(1, 15):
            mat[-i][-j] = m[-i][-j]

    nb_bloc_bin = bin(nb_bloc)[2:]
    nb_bloc_bin = "0" * (5 - len(nb_bloc_bin)) + nb_bloc_bin

    for i, e in enumerate(nb_bloc_bin[::-1]):
        mat[16 - i][0] = int(e)

    mat[22][8] = 0 if f in [0, 1] else 1
    mat[23][8] = 0 if f in [0, 2] else 1
    mat[24][8] = dType
    mat = [elem if elem == 0 else 255 for line in mat for elem in line]

    toLoad = Image.new("1", (25, 25))
    toLoad.putdata(mat)
    if save:
        filename = fd.asksaveasfilename(
            initialdir=os.getcwd() + "/Save/",
            title="Enregistrer le QR Code",
            filetypes=(("fichier PNG", "*.png"),),
            defaultextension=".png"
        )
        if filename is not None:
            toLoad.save(filename)
    toLoad = toLoad.resize((300, 300))
    img = ImageTk.PhotoImage(toLoad)
    L_image['image'] = img
    dType = "ascii" if dType else "numérique"
    L_info['text'] += f"\nType:\t\t{dType}\nMessage:\t\t{message.get()}"


def fen_creer_QR():
    ''' Crée une fenêtre pour créer un QR code'''
    global root, fen_QR, message, filtre, dataType
    if "fen_QR" in globals():
        fen_QR.focus_force()
        return

    fen_QR = tk.Toplevel(root)
    fen_QR.protocol("WM_DELETE_WINDOW", del_fen_QR)
    fen_QR.title()
    fen_QR.resizable(0, 0)

    dataType = tk.IntVar(fen_QR)
    dataType.set(1)
    filtre = tk.IntVar(fen_QR)
    message = tk.StringVar(fen_QR)

    R_ascii = tk.Radiobutton(
        fen_QR,
        font=("Ebrima", 12),
        variable=dataType,
        text="ASCII",
        value=1
    )

    R_num = tk.Radiobutton(
        fen_QR,
        font=("Ebrima", 12),
        variable=dataType,
        text="Numérique",
        value=0
    )

    R_pas_filtre = tk.Radiobutton(
        fen_QR,
        font=("Ebrima", 12),
        variable=filtre,
        text="Pas de filtre",
        value=0
    )

    R_damier = tk.Radiobutton(
        fen_QR,
        font=("Ebrima", 12),
        variable=filtre,
        text="Filtre damier",
        value=1
    )

    R_ligneH = tk.Radiobutton(
        fen_QR,
        font=("Ebrima", 12),
        variable=filtre,
        text="Lignes Horzontales",
        value=2
    )

    R_ligneV = tk.Radiobutton(
        fen_QR,
        font=("Ebrima", 12),
        variable=filtre,
        text="Lignes Verticales",
        value=3
    )

    L_message = tk.Label(fen_QR, text="Message: ")
    E_message = tk.Entry(fen_QR, textvariable=message)

    B_apercu = tk.Button(
        fen_QR,
        text="Aperçu du QR Code",
        command=lambda: creer_QR(False)
    )

    B_creer = tk.Button(
        fen_QR,
        text="Créer le QR Code",
        command=lambda: creer_QR(True)
    )

    L_image = tk.Label(fen_QR)

    R_ascii.grid(row=0, column=0, columnspan=2)
    R_num.grid(row=0, column=2, columnspan=2)

    R_pas_filtre.grid(row=1, column=0)
    R_damier.grid(row=1, column=1)
    R_ligneH.grid(row=1, column=2)
    R_ligneV.grid(row=1, column=3)

    L_message.grid(row=2, column=0, columnspan=2)
    E_message.grid(row=2, column=2, columnspan=2)

    B_apercu.grid(row=3, column=0, columnspan=2)
    B_creer.grid(row=3, column=2, columnspan=2)

    L_image.grid(row=4, column=0, columnspan=4)

    fen_QR.mainloop()


def main():
    ''' Fonction principale, crée la fenêtre principale'''
    global root, L_image, L_info
    root = tk.Tk()
    root.title("QR Code")

    B_open_QR = tk.Button(root, text="Lire un QR Code", command=ouvrir_QR)
    B_open_QR.grid(row=0)

    B_open_QR = tk.Button(root, text="Créer un QR Code", command=fen_creer_QR)
    B_open_QR.grid(row=0, column=1)

    L_image = tk.Label(root)
    L_image.grid(row=1, columnspan=2)

    L_infoT = tk.Label(root, text="Info", font=('arial', 15))
    L_infoT.grid(row=0, column=2)

    L_info = tk.Label(root, height=3, justify='left', font=('arial', 15))
    L_info.grid(row=1, column=2)

    root.mainloop()


main()
