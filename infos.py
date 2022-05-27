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
                    result += '<br>'
                    result += '<br>'
                    result += '<br>'
                    result += 'Titulo: ' + tema + '<br>'
                    result += 'Gênero: ' + genero + '  ' + '<br>'
                    result += 'Imagem: ' + imagem + '  ' + '<br>'
                    result += 'Versos: ' + qtd_versos + '  ' + '<br>'
                    result += 'Verbetes no texto: ' + qtd_wordin + '  ' + '<br>'
                    result += 'Verbetes  do Tema: ' + qtd_lexico + '  ' + '<br>'
                    result += '• Banco de Ítimos: ' + qtd_itimos + '  ' + '<br>'
                    result += 'Análise : ' + qtd_analiz + '  ' + '<br>'
                    result += 'Notação Científica: ' + qtd_cienti + '  ' + '<br>'
                    result += '<br>'

        return(result)

# Driver Code:
if __name__ == "__main__":
    nome_tema = input("Info para o Tema: ")
    load_info(nome_tema.capitalize())

    
