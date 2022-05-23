'''
 Gera matriz 3D para o tema informado

, label='linhas'
, label='versos'
, label='ítimos'

 '''

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def load_number():  # load indexes numbers para os temas
    lista = []
    with open(os.path.join("./base/index.txt"), encoding="utf-8") as file:
        for line in file:
            lista.append(line)
    return lista


def load_parole():  # load qtd total de palavras por tema
    lista = []
    with open(os.path.join("./base/parole.txt"), encoding="utf-8") as file:
        for line in file:
            lista.append(line)
    return lista


def load_wordin():  # load qtd de palavras por tema
    lista = []
    with open(os.path.join("./base/wordin.txt"), encoding="utf-8") as file:
        for line in file:
            lista.append(line)
    return lista


def say_number(tema):  # search index title for analise combinatória do tema
    result = "nonono"
    indexes = load_number()
    for line in indexes:
        string = line.strip("\n")
        part_string = string.partition(' : ')
        if part_string[0].upper() == tema.upper():
            result = part_string[2]
            break
    return result


def say_parole(tema):  # search index title for total de palavras no tema
    result = "nonono"
    indexes = load_parole()
    for line in indexes:
        string = line.strip("\n")
        part_string = string.partition(' : ')
        if part_string[0].upper() == tema.upper():
            result = part_string[2]
            break
    return result


def say_wordin(tema):  # search index title for qtd de palavras no tema
    result = "nonono"
    indexes = load_wordin()
    for line in indexes:
        string = line.strip("\n")
        part_string = string.partition(' : ')
        if part_string[0].upper() == tema.upper():
            result = part_string[2]
            break
    return result


fg = plt.figure(figsize=(9,6))
ax = fg.add_subplot(111, projection = '3d')

def build_matrix(this_tema):

    linini = 1
    curlin = '01'  # obrigatoriamente começa com |01|
    itimos_acm = 0

    x_pos = np.array([])
    y_pos = np.array([])
    z_pos = np.array([])
    z_val = np.array([])
                                  
    file = os.path.join("./data/", this_tema + ".ypo")
    with open(file, encoding="utf-8") as matrix:  # iterate file line by line
        path = os.path.basename(file)
        os.path.splitext(path)
        tabela = os.path.splitext(path)[0]
        tabela = tabela.capitalize()
        
        for line in matrix:
            if line.startswith("|", 0, 1):
                linhas = line.split("|")
                newlin = int(linhas[1])
                newcol = int(linhas[2])

                if linhas[1] != curlin:
                    linini += 1
                    curlin = linhas[1]
        
                if newcol == 0:  # linha em branco
                    x_pos = np.append(x_pos,linini)
                    y_pos = np.append(y_pos,0)
                    z_pos = np.append(z_pos,0)
                    z_val = np.append(z_val,0)
                else:
                    itimos = int(linhas[5])
                    itimos_acm += itimos
                    delta = 1  # because linini começa com 1
                    x_pos = np.append(x_pos,linini-delta)
                    y_pos = np.append(y_pos,newcol-delta)
                    z_pos = np.append(z_pos,0)
                    z_val = np.append(z_val, itimos)

        x_val = np.ones(len(x_pos))
        y_val = np.ones(len(y_pos))
        z_pos = np.ones(len(z_pos))
        
        ax.set_xlabel('x ➪ linhas', fontsize=14)
        ax.set_ylabel('y ➪ versos', fontsize=14)
        ax.set_zlabel('z ➪ ítimos', fontsize=14)
        
        title_string = this_tema + ' ➪ ' + str(linini) + ' ➪ ' + str(itimos_acm) + ' ( ' + say_wordin(this_tema) + ' / '+ say_parole(this_tema) + ' )'
        subtitle_string = say_number(this_tema)
        
        plt.suptitle(title_string, fontsize=16)
        plt.title(subtitle_string, fontsize=12)

        ax.view_init(elev=30, azim=-30)
        ax.bar3d(x_pos, y_pos, z_pos, x_val, y_val, z_val, color='#00ccaa', alpha=.85, edgecolor='k')  #
        
        file_save = os.path.join("./images/matrix/" + this_tema + ".png")
        plt.savefig(file_save, dpi = 50)
        
        plt.show()

# Driver Code:
if __name__ == "__main__":
    filename = input("Tema para Matrix 3D: ")
    build_matrix(filename.capitalize())

