import os
import random
import datetime
from random import randrange

def gera_poema(nome_tema):  # abrir um script.ypo e gerar um novo texto
    """
    :param = script, tema
         numero_linea = '01'  # linha
         ideia_numero = '01'  # ideia
         fonte_itimos = 'NA'  # fonte
         se_randomico = 'F'   # se_random
         total_itimos = N     # qtd_itimos
         itimos_atual = 1     # itimos_atual
         array_itimos = []    # array com todos os itimos da ideia na linha
    return: novo_poema

    ToDo:
       - UpDate_Numbers() = ler *.ypo da pasta e verbetes.append(cada_verbete_novo) = done in cata_pala()
       - usar temas.rol - criar Livro_Vivo
       - get and hilight semente in zero.py
       - dialeto em ciuminho
    """

    lista_header = []
    lista_linhas = []
    lista_finais = []
    lista_change = []
    lista_duplos = []
    lista_errata = []
    lista_unicos = []

    conta_palavra = 0

    pega_semente = ""
    acha_semente = False
    qual_semente = ""
    # fonte_da_semente = AllTrim(Application:oMainForm:oCfg:fonte_semente)
    fonte_da_semente = "nonono"

    nome_tema = nome_tema.replace("\n", "")

    try:
        tema = abre(nome_tema)
        for line in tema:
            if line.startswith("*", 0, 1):  # observações e cabeçalho
                lista_header.append(line)
            elif line.startswith("|", 0, 1):  # ideias & itimos
                lista_linhas.append(line)
            else:  # <eof> + análise + build_date
                lista_finais.append(line)
    except UnicodeDecodeError:
        lista_errata.append(nome_tema)
        pass

    novo_poema = []
    # novo_poema.append(nome_tema + '\n')
    novo_verso = ""
    muda_linha = "00"
    pula_linha = "no"

    for line in lista_linhas:
        alinhas = line.split("|")

        if len(alinhas) == 0:
            continue

        if len(alinhas) < 2:
            lista_errata.append(nome_tema)
            continue

        if alinhas[2] == "00":
            pula_linha = "si"
            lista_change.append(line)
            continue

        if len(alinhas) >= 7:
            numero_linea = alinhas[1]
            ideia_numero = alinhas[2]
            fonte_itimos = alinhas[3]
            se_randomico = alinhas[4]
            total_itimos = int(alinhas[5])
            itimos_atual = int(alinhas[6])
            array_itimos = alinhas[7: len(alinhas) - 1]

            for itimo in array_itimos:
                if (
                        fonte_itimos == fonte_da_semente
                ):  # Linha escolhida em TFormDemo
                    if qual_semente.upper() in itimo.upper():
                        if not acha_semente:  # Pega apenas uma vez...
                            qual_semente = itimo
                            acha_semente = True

            # while True # para não repetir itimos
            tentativas = 0
            while True:  # Seleciona próximo ítimo...
                if (qual_semente != "") and (acha_semente):
                    pega_semente = qual_semente.replace(
                        qual_semente,
                        Chr(171) + " " + qual_semente + " " + Chr(187),
                    )  # Adiciona MARCA ao texto
                    lista_unicos.append(
                        qual_semente.upper()
                    )  # adiciona à lista SEM MARCA para não repetir...
                    acha_semente = True  # Substitui apenas uma vez...
                    novo_verso += pega_semente + " "
                    break  # Seleciona próximo ítimo...

                if 1 != total_itimos:  # mais de hum itimo
                    if se_randomico == "F":
                        itimos_atual -= 1  # because matrix começa em zero
                        if itimos_atual < 0:
                            itimos_atual = total_itimos - 1  # because matrix começa em zero
                    else:
                        if total_itimos >= 1:
                            itimos_atual = randrange(0, total_itimos - 1)
                        else:
                            itimos_atual = 0
                else:
                    itimos_atual = 0

                #  if itimos_atual >= 0 and itimos_atual <= len(array_itimos) - 1:
                if itimos_atual >= 0 and itimos_atual <= len(array_itimos):
                    itimo_escolhido = array_itimos[itimos_atual]
                else:
                    print(nome_tema, " - error: ", array_itimos, itimos_atual)
                    itimo_escolhido = "_Erro_"

                #   Elimina duplicidaders óbvias...
                temp_random = se_randomico
                if (
                        not itimo_escolhido.upper()
                            in "_E_A_AS_O_OS_NO_NOS_NA_NAS_ME_DE_SE_QUE_NÃO_SO_SEM_NEM_EM_UM_UMA_POR_MEU_VE_TE_TÃO_DA_SER_TER_PRA_PARA_QUANDO_..._._,_:_!_?"
                ):
                    if (
                            itimo_escolhido.upper() not in lista_unicos
                    ):  # verifica se Itimo ainda não foi usado...
                        lista_unicos.append(itimo_escolhido.upper())
                        break
                    else:  # Já foi usado... Busca Outro...
                        tentativas += 1
                        if (
                                tentativas > total_itimos
                        ):  # Tentativas > que total de ítimos: pega o próximo sequencial
                            if temp_random == "T":
                                tentativas = 0  # Da Capo
                                temp_random = "F"
                            else:
                                lista_unicos.append(itimo_escolhido.upper())
                                lista_duplos.append(itimo_escolhido.upper())
                                break

                        if itimo_escolhido in lista_duplos:
                            if len(itimo_escolhido) > 3:
                                # print(itimo_escolhido, " ---> repetido")
                                continue

                        if tentativas > 50:
                            break
                else:
                    break

            # verifica se é nova linha no script
            if numero_linea != muda_linha:  # mudou de linha
                novo_poema.append(acerto_final(novo_verso, nome_tema))
                novo_verso = ""
                muda_linha = numero_linea

            novo_verso += itimo_escolhido + " "

            if "si" == pula_linha:
                novo_poema.append("\n")
                pula_linha = "no"

            new_line = (
                    "|"
                    + numero_linea
                    + "|"
                    + ideia_numero
                    + "|"
                    + fonte_itimos
                    + "|"
            )

            if total_itimos != len(array_itimos):  # just in case...
                total_itimos = len(array_itimos)
            if itimos_atual < 1:  # sequencial = -1
                if total_itimos == 1:
                    itimos_atual = 1
                else:
                    itimos_atual = total_itimos
            if se_randomico == "T":
                new_line += "T"
            else:
                new_line += "F"
            new_line += "|" + str(total_itimos) + "|" + str(itimos_atual)

            for v in alinhas[7: len(alinhas) - 1]:
                new_line += "|" + v
            new_line += "|\n"
            lista_change.append(new_line)
    # end for... lista_linhas

    novo_poema.append(acerto_final(novo_verso, nome_tema))
    catapala = conta_palas(novo_poema)
    catapala = str(catapala)

    #    analise = get_numbers(nome_tema)
    #    analise.strip(' ')
    #    analise = analise.replace(nome_tema + ' = ', '')  # apenas os números da análise combinatória
    #    novo_poema.append(analise)

    if len(lista_errata) > 0:
        print(lista_errata)
    else:
        # reconstrói o script com novas posições
        with open(os.path.join("./data/" + nome_tema + ".ypo"), "w", encoding = "utf-8") as file:
            for linha in lista_header:
                file.write(linha)

            for linha in lista_change:
                file.write(linha)
        
            for linha in lista_finais:
                if 'CATAPALA' in str(linha):
                    del (linha)
        
            if "CATAPALA" not in str(lista_finais):  # se não gravou...
                lista_finais.insert(1, "CATAPALA = " + catapala + "\n")
        
            for linha in lista_finais:
                if "CATAPALA" in str(linha):
                    linha = "CATAPALA = " + catapala + "\n"
                file.write(linha)
        file.close()
        
    return novo_poema


def acerto_final(texto, nome_tema):
    if " ." in texto:
        texto = texto.replace(" .", ".")
    if " ," in texto:
        texto = texto.replace(" ,", ",")
    if " ?" in texto:
        texto = texto.replace(" ?", "?")
    if " !" in texto:
        texto = texto.replace(" !", "!")
    if " :" in texto:
        texto = texto.replace(" :", ":")
    if " ..." in texto:
        texto = texto.replace(" ...", "...")
    if " -" in texto:
        texto = texto.replace(" -", "-")
    if "- " in texto:
        texto = texto.replace("- ", "-")
    if " #" in texto:  # apenas usado em Bula para concatenar 3 palavras
        texto = texto.replace(" #", "")
    if "#" in texto:
        texto = texto.replace("#", "")
    if "< pCity >" in texto:
        texto = texto.replace("< pCity >", load_cidade_fato())
    if "< pCidadeOficio >" in texto:
        texto = texto.replace("< pCidadeOficio >", fala_cidade())
    if "< gCelcius >" in texto:
        texto = texto.replace("< gCelcius >", fala_celsius())
    if "< pUmido >" in texto:
        texto = texto.replace("< pUmido >", fala_umidade())
    if "< dNormas >" in texto:
        texto = texto.replace("< dNormas >", fala_norma_abnp())
    if "< dPublic >" in texto:
        hoje = datetime.datetime.now().date()
        rand = randrange(0, hoje.year * 30)
        hoje = hoje - datetime.timedelta(days=rand)
        texto = texto.replace("< dPublic >", fala_data(hoje))
    if "< dOficio >" in texto:
        hoje = datetime.datetime.now().date()
        rand = randrange(0, hoje.year * 30)
        hoje = hoje + datetime.timedelta(days=rand)
        texto = texto.replace("< dOficio >", fala_data(hoje))
    if "< nAnalise >" in texto:
        anali = get_numbers(nome_tema)
        anali.strip()
        anali = anali.replace(
            nome_tema + " = ", ""
        )  # apenas os números da análise combinatória
        texto = texto.replace("< nAnalise >", anali)

    return texto


def get_numbers(nome_tema):
    """
    :return: análise combinatória do tema
    """
    ana_con = "not in list"
    numbers = []

    lista = []
    with open(os.path.join("./data/index.txt"), "r") as file:
        for line in file:
            lista.append(line)
        file.close()

    for line in lista:
        numbers.append(line.strip())
        if line.startswith(nome_tema):
            ana_con = line
    return ana_con


def load_cidade_fato():
    """
    :return: alguma cidade do arquivo fatos_cidades.txt
    """
    cidades = []
    with open(os.path.join("./data/fatos_cidades.txt"), encoding = "utf8") as file:
        for line in file:
            cidades.append(line)
        file.close()

    x = randrange(0, len(cidades))
    city = cidades[x]
    city = city.replace("\n", "")
    return city


def fala_cidade():
    """
    :return: alguma cidade do arquivo cidade_país.txt
    """
    cidades = []
    # cidade_pais.txt ## não conseguiu abrir o codec !!!
    with open(os.path.join("./data/fatos_cidades.txt"), encoding = "utf8") as file:
        for line in file:
            cidades.append(line)
        file.close()

    x = randrange(0, len(cidades))
    city = cidades[x]
    city = city.replace("\n", "")

    return city


def fala_celsius():
    """
    :return: temperatura randômica entre 1 e 50 graus celcius - Meteoro
    """
    ini = randrange(1, 50)
    fim = randrange(1, 50)
    if ini > fim:
        tmp = ini
        ini = fim
        fim = tmp
    else:
        ini -= 1
    return str(ini) + "º e " + str(fim) + "º"


def fala_umidade():
    """
    :return: umidade randômica entre 1 e 99% - Meteoro
    """
    ini = randrange(1, 99)
    return str(ini) + "%"


def fala_data(dref):
    """
    :param data de referência
    :return: data genérica: dia + mês_extenso + ano
    """
    meses = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    dia = dref.day
    mes = dref.month
    if mes > 0 and mes < 13:
        mes -= 1
    else:
        mes = 5

    mestxt = meses[mes]
    ano = dref.year
    return str(dia) + " de " + str(mestxt) + " de " + str(ano)


def fala_norma_abnp():
    """
    :return: data randômicamente 'anterior' à data atual
    """
    hoje = datetime.datetime.now().date()
    rand = randrange(0, hoje.year * 30)
    hoje = hoje - datetime.timedelta(days=rand)
    return str(hoje.day) + "/" + str(hoje.year)


def abre(nome_do_tema):
    """
    :param nome_do_tema
    :return: lista do arquivo
    """
    
    full_name = os.path.join("./data/", nome_do_tema) + ".ypo"
    lista = []
    with open(full_name, encoding="utf-8") as file:
        for line in file:
            lista.append(line)
        file.close()

    return lista


def conta_palas(frase):
    """
    :param frase
    :return: quantidade de palavras na "frase" = todas as linhas do poema gerado
    """

    # palavras = frase.split(" ")  # separa palavras
    texto = ""
    somas = 0
    for p in frase:
        texto += p

    for p in texto:
        if p == " ":
            somas += 1

    return somas
