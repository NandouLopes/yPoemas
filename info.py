'''
    load info sobre o tema
'''

import os

def load_info(nome_tema):

    info = []
    with open(os.path.join("./base/" + "info.txt"), "r", encoding="utf-8") as novo:
        result = ""
        for line in novo:
            if line.startswith('|'):
                pipe = line.split("|")
                if pipe[1].upper() == nome_tema.upper():
                    tema = pipe[1]
                    genero = pipe[2]
                    imagem = pipe[3]
                    qtd_versos = pipe[4]
                    qtd_wordin = pipe[5]
                    qtd_lexico = pipe[6]
                    qtd_itimos = pipe[7]
                    qtd_analiz = pipe[8]
                    qtd_cienti = pipe[9]
                    result += 'Titulo: **' + tema + '**  ' + '\n'
                    result += 'Gênero: ' + genero + '  ' + '\n'
                    result += 'Imagem: ' + imagem + '  ' + '\n'
                    result += 'Versos: ' + qtd_versos + '  ' + '\n'
                    result += 'Ítimos: ' + qtd_itimos + '  ' + '\n'
                    result += 'Verbetes no texto: ' + qtd_wordin + '  ' + '\n'
                    result += 'Palavras do Tema: ' + qtd_lexico + '  ' + '\n'
                    result += 'Análise Combinatória: ' + qtd_analiz + '  ' + '\n'
                    result += 'Notação Científica: ' + qtd_cienti + '  ' + '\n'

        return(result)

# Driver Code:
if __name__ == "__main__":
    nome_tema = input("Info para o Tema: ")
    load_info(nome_tema.capitalize())

    
