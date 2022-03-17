import PIL as pil
from PIL import Image
# from PIL import ImageTk


# Fonctions
def nbrLig(mat):
    return len(mat)


def nbrCol(mat):
    return len(mat[0])


def saving(matPix, filename):
    # sauvegarde l'image contenue dans matpix dans le fichier filename
    # utiliser une extension png pour que la fonction fonctionne sans perte d'information
    toSave = pil.Image.new(mode="1", size=(nbrCol(matPix), nbrLig(matPix)))
    for i in range(nbrLig(matPix)):
        for j in range(nbrCol(matPix)):
            toSave.putpixel((j, i), matPix[i][j])
    toSave.save(filename)


def loading(filename):
    # charge le fichier image filename et renvoie une matrice de 0 et de 1 qui représente
    # l'image en noir et blanc
    toLoad = pil.Image.open(filename)
    mat = [[0] * toLoad.size[0] for _ in range(toLoad.size[1])]
    for i in range(toLoad.size[1]):
        for j in range(toLoad.size[0]):
            mat[i][j] = 0 if toLoad.getpixel((j, i)) == 0 else 1
    return mat


def coin_QC():
    mat = [[0] * 7 for _ in range(7)]

    for i in range(7):
        for j in range(7):
            if (i in [1, 5] and 0 < j < 6) or (j in [1, 5] and 0 < i < 6):
                mat[i][j] = 1
    return mat


def rotation(sens, mat):
    if sens == 0:
        return [[mat[-(i + 1)][j] for i in range(nbrLig(mat))] for j in range(nbrCol(mat))]
    elif sens == 1:
        return [[mat[i][-(j + 1)] for i in range(nbrLig(mat))] for j in range(nbrCol(mat))]

    return [[mat[-(i + 1)][-(j + 1)] for i in range(nbrLig(mat))] for j in range(nbrCol(mat))]


def verif_sens_QC(mat):
    coin = coin_QC()
    for i in range(7):
        for j in range(7):
            if coin[i][j] != mat[i][j]:
                mat = rotation(2, mat)
                return mat
            if coin[i][j - 1] != mat[i][j - 1]:
                mat = rotation(0, mat)
                return mat
            if coin[i - 1][j] != mat[i - 1][j]:
                mat = rotation(1, mat)
                return mat
    return mat


# variables
matrice = loading("Exemples/qr_code_ssfiltre_ascii_rotation.png")
matrice = rotation(2, matrice)
print(*matrice, sep='\n', end="\n\n")
matrice = verif_sens_QC(matrice)
print(*matrice, sep='\n')
