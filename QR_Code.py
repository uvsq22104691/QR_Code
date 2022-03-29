from PIL import Image


# Fonctions
def nbrLig(mat):
    return len(mat)


def nbrCol(mat):
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
    """ 0 = droite 1 = gauche 2 = deux fois droite"""
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
    m1, m2, m3, m4, c1, c2, c3 = liste
    p_err = []
    if c1 == (m1 + m2 + m4) % 2:
        p_err.append(3)
    if c2 == (m1 + m3 + m4) % 2:
        p_err.append(2)
    if c3 == (m2 + m3 + m4) % 2:
        p_err.append(1)

    if len(p_err) == 0:
        return liste
    elif len(p_err) == 1:
        pass
    elif len(p_err) == 2:
        pass
    elif len(p_err) > 2:
        return False

    print(p_err)


# variables
matrice = loading("Exemples/qr_code_ssfiltre_ascii_rotation.png")
matrice = rotation(2, matrice)
print(*matrice, sep='\n', end="\n\n")
print(verif_ligne(matrice))
matrice = verif_sens_QC(matrice)
print(*matrice, sep='\n')
print(verif_ligne(matrice))
