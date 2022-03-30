from PIL import Image
import tkinter as tk
import tkinter.filedialog as fd
import os


# Fonction
def nbrLig(mat):
    '''TO DO'''
    return len(mat)


def nbrCol(mat):
    ''' TO DO'''
    return len(mat[0])


def saving(matPix, filename):
    ''' sauvegarde l'image contenue dans matpix dans le fichier filename
        utiliser une extension png pour que la fonction fonctionne sans perte d'information'''
    toSave = Image.new(mode="1", size=(nbrCol(matPix), nbrLig(matPix)))
    for i in range(nbrLig(matPix)):
        for j in range(nbrCol(matPix)):
            toSave.putpixel((j, i), matPix[i][j])
    toSave.save(filename)


def loading(filename):
    # charge le fichier image filename et renvoie une matrice de 0 et de 1 qui représente
    # l'image en noir et blanc
    toLoad = Image.open(filename)
    mat = [[0] * toLoad.size[0] for _ in range(toLoad.size[1])]
    for i in range(toLoad.size[1]):
        for j in range(toLoad.size[0]):
            mat[i][j] = 0 if toLoad.getpixel((j, i)) == 0 else 1
    return mat


def coin_QC():
    '''TO DO'''
    mat = [[0] * 7 for _ in range(7)]

    for i in range(7):
        for j in range(7):
            if (i in [1, 5] and 0 < j < 6) or (j in [1, 5] and 0 < i < 6):
                mat[i][j] = 1
    return mat


def rotation(sens, mat):
    """ 0 = droite
        1 = gauche
        2 = deux fois à droite
    """
    if sens == 0:
        # tourne la matrice dans le sens horaire une fois
        return [[mat[-(i + 1)][j] for i in range(nbrLig(mat))] for j in range(nbrCol(mat))]
    elif sens == 1:
        # tourne la matrice dans le sens anti-horaire une fois
        return [[mat[i][-(j + 1)] for i in range(nbrLig(mat))] for j in range(nbrCol(mat))]

    # tourne la matrice dans le sens horaire deux fois (ou symetrie horizontal et vertical)
    return [[mat[-(i + 1)][-(j + 1)] for i in range(nbrLig(mat))] for j in range(nbrCol(mat))]


def verif_sens_QC(mat):
    '''TO DO'''
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
    '''TO DO'''
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
    '''TO DO'''
    m1, m2, m3, m4, c1, c2, c3 = liste
    err = {
        1: 4,
        2: 5,
        3: 0,
        4: 6,
        5: 1,
        6: 2,
        7: 3,
    }
    p_err = 0
    if c1 != (m1 + m2 + m4) % 2:
        p_err += 1
    if c2 != (m1 + m3 + m4) % 2:
        p_err += 2
    if c3 != (m2 + m3 + m4) % 2:
        p_err += 4

    if p_err != 0:
        liste[err[p_err]] = 0 if liste[err[p_err]] == 1 else 1
    return liste[:4]


def lire_qr_code(mat):
    '''TO DO'''
    liste = []
    for i in range(0, 16, 2):
        m = mat[::-1][i:i + 2][::-1]
        m = [mat[-14:] for mat in m]

        if i % 4 == 0:
            m1 = [m[i % 2][-((i - 1) // 2 + 1)] for i in range(1, 15)]
            m2 = [m[i % 2][-((i - 1) // 2 + 8)] for i in range(1, 15)]
        else:
            m1 = [m[(i + 1) % 2][i // 2] for i in range(0, 14)]
            m2 = [m[(i + 1) % 2][i // 2 + 7] for i in range(0, 14)]
            pass

        liste.append(m1)
        liste.append(m2)
    return liste


def lire_type_donnee(mat):
    '''TO DO'''
    return mat[24][8]


def interpreter_ascii(mat):
    '''TO DO'''
    for bloc in [liste for liste in mat if sum(liste) != 14]:
        tmp = ''.join(map(str, correction_hamming(bloc[:7]) + correction_hamming(bloc[7:])))[::-1]
        tmp = int(tmp, 2)
        print(chr(tmp), end="")


def interpreter_num(mat):
    '''TO DO'''
    for bloc in [liste for liste in mat if sum(liste) != 14]:
        tmp = ''.join(map(str, correction_hamming(bloc[:7]) + correction_hamming(bloc[7:])))[::-1]
        print(hex(int(tmp[:4], 2))[2:3], hex(int(tmp[4:], 2))[2:3], sep="", end=" ")


def interpreter(mat, data):
    if lire_type_donnee(mat) == 1:
        interpreter_ascii(data)
    else:
        interpreter_num(data)


def lire_type_filtre(mat):
    '''TO DO'''
    filtre = ''.join([str(mat[22][8]), str(mat[23][8])])
    return int(filtre, 2)


def applique_filtre(matrice):
    '''TO DO'''
    filtre = lire_type_filtre(matrice)
    if filtre == 0:
        return matrice
    elif filtre == 1:
        for y in range(-16, 0, 1):
            for x in range(-14, 0, 1):
                matrice[y][x] = matrice[y][x] ^ (y + x) % 2
        return matrice
    elif filtre == 2:
        for y in range(-16, 0, 1):
            for x in range(-14, 0, 1):
                matrice[y][x] = matrice[y][x] ^ y % 2
        return matrice
    elif filtre == 3:
        for y in range(-16, 0, 1):
            for x in range(-14, 0, 1):
                matrice[y][x] = matrice[y][x] ^ x % 2
        return matrice


def ouvrir_fichier():
    f = fd.askopenfile(
        initialdir=os.getcwd() + "/Exemples/",
        title="charger un QR Code",
        filetypes=(("fichier PNG", "*.png"),)
    )
    if f is None:
        return ""
    return f.name


def main():
    root = tk.Tk()
    root.title("vives les damiers :wink:")
    file = ""
    while file == "":
        file = ouvrir_fichier()
    mat = loading(file)
    mat = verif_sens_QC(mat)
    mat = applique_filtre(mat)
    data = lire_qr_code(mat)
    interpreter(mat, data)


main()
