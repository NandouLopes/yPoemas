import os
import random
import datetime
import streamlit as st

from random import randrange


def gera_poema(nome_tema, seed_source):  # abrir um script.ypo e gerar um novo texto
    """
    :param = script, tema
         numero_linea = '01'  # linha
         ideia_numero = '01'  # ideia
         fonte_itimos = nome_tema + '_' + numero_linea + ideia_numero # fonte dos itimos. Pode haver re-uso !!!
         se_randomico = 'F'   # se_random
         total_itimos = N     # qtd_itimos
         itimos_atual = 1     # itimos_atual
         array_itimos = []    # array com todos os itimos da ideia na linha
    return: novo_poema

    ToDo:
       - UpDate_Numbers() = ler *.ypo da pasta e verbetes.append(cada_verbete_novo) = done in cata_pala()
       obs: the search for a seed acctualy only works in portuguese. Try to translate your search_seed into this language.
    """

    lista_header = []
    lista_linhas = []
    lista_finais = []
    lista_change = []
    lista_duplos = []
    lista_errata = []
    lista_unicos = []

    conta_palavra = 0

    this_seed = ""
    seed_coords = ""
    look_for_seed = False

    if seed_source != "":
        where = -1
        for letra in seed_source:
            where += 1
            if letra == "➪":
                minus = where
        maxis = where
        look_for_seed = True
        this_seed = seed_source[0 : minus - 1]
        seed_coords = seed_source[minus + 2 : maxis + 1]

    nome_tema = nome_tema.strip("\n")

    try:
        if nome_tema == "Babel":
            novo_poema = novo_babel(0)
            return novo_poema
        else:
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
    novo_verso = ""
    muda_linha = "00"
    pula_linha = "no"
    fonte_eureka = ""

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
            array_itimos = alinhas[7 : len(alinhas) - 1]
            
            fonte_eureka = nome_tema + '_' + numero_linea + ideia_numero

            if itimos_atual > len(array_itimos):
                itimos_atual = len(array_itimos)

            if total_itimos != len(array_itimos):  # just in case...
                total_itimos = len(array_itimos)  # real lenght...

            if total_itimos == 1:  # just in case...
                se_randomico = "F"

            tentativas = 0
            while True:  # Seleciona próximo ítimo (para não repetir...)
                if 1 != total_itimos:  # mais de hum itimo
                    if se_randomico == "F":
                        itimos_atual -= 1  # because matrix começa em zero
                        if itimos_atual < 0:
                            itimos_atual = (
                                total_itimos - 1
                            )  # because matrix começa em zero
                    else:
                        if total_itimos >= 1:
                            itimos_atual = randrange(0, total_itimos - 1)
                        else:
                            itimos_atual = 0
                else:
                    itimos_atual = 0

                if itimos_atual >= 0 and itimos_atual <= len(array_itimos):
                    itimo_escolhido = array_itimos[itimos_atual]
                else:
                    st.warning(
                        "Algo deu errado com o tema "
                        + nome_tema.upper() + ". Se puder, entre em contato com o Autor."
                        )
                    itimo_escolhido = "_Erro_"

                if fonte_eureka == seed_coords:  # eureka parameter
                # if fonte_itimos == seed_coords:  # eureka parameter
                    if look_for_seed:  # not changed yet...
                        for itimo in array_itimos:
                            if this_seed.lower() in itimo.lower():
                                itimo_escolhido = itimo
                                lista_unicos.append(
                                    itimo_escolhido.upper()
                                )  # cannot repeat words...
                                itimo_escolhido = itimo_escolhido.replace(
                                    this_seed, "<mark>" + this_seed + "</mark>"
                                )  # markdown text
                                look_for_seed = False

                temp_random = se_randomico
                if (
                    not itimo_escolhido.upper()  # Elimina duplicidaders óbvias...
                    in "_E_A_AS_O_OS_NO_NOS_NA_NAS_ME_DE_SE_QUE_NÃO_SO_SEM_NEM_EM_UM_UMA_POR_MEU_VE_TE_TÃO_DA_SER_TER_PRA_PARA_QUANDO_..._._,_:_!_?"
                ):
                    if (
                        itimo_escolhido.upper() not in lista_unicos
                    ):  # check if not yet used...
                        lista_unicos.append(itimo_escolhido.upper())
                        break
                    else:
                        tentativas += 1
                        if (
                            tentativas > total_itimos
                        ):  # tentativas > que total de ítimos: pega o próximo sequencial
                            if temp_random == "T":
                                tentativas = 0  # Da Capo
                                temp_random = "F"
                            else:
                                lista_unicos.append(itimo_escolhido.upper())
                                lista_duplos.append(itimo_escolhido.upper())
                                break

                        if itimo_escolhido in lista_duplos:
                            if len(itimo_escolhido) > 3:
                                continue

                        if tentativas > 50:
                            break
                else:
                    break

            if numero_linea != muda_linha:  # check if is a new line on script
                novo_poema.append(acerto_final(novo_verso, nome_tema))
                novo_verso = ""
                muda_linha = numero_linea

            novo_verso += itimo_escolhido + " "

            if "si" == pula_linha:
                novo_poema.append("\n")
                pula_linha = "no"

            new_line = (
                "|" + numero_linea + "|" + ideia_numero + "|" + fonte_itimos + "|"
            )

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

            for v in alinhas[7 : len(alinhas) - 1]:
                new_line += "|" + v
            new_line += "|\n"
            lista_change.append(new_line)
    # end for... lista_linhas

    novo_poema.append(acerto_final(novo_verso, nome_tema))

    if nome_tema == "Nós":
        novo_poema.append("\n")
        novo_poema.append(
            '<a href="https://thispersondoesnotexist.com/" target="_blank">... quem será essa pessoa que não existe?</a>'
        )

    if len(lista_errata) > 0:
        st.warning(
        "Algo deu errado com o tema "
        + nome_tema.upper() + ". Se puder, entre em contato com o Autor."
        )
    else:
        # rebuild script with new positions
        with open(
            os.path.join("./data/" + nome_tema + ".ypo"), "w", encoding="utf-8"
        ) as file:
            for linha in lista_header:
                file.write(linha)

            for linha in lista_change:
                file.write(linha)

            for linha in lista_finais:
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

    return texto


def load_cidade_fato():
    """
    :return: alguma cidade do arquivo fatos_cidades.txt
    """
    cidades = []
    with open(os.path.join("./base/fatos_cidades.txt"), encoding="utf8") as file:
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
    with open(os.path.join("./base/fatos_cidades.txt"), encoding="utf8") as file:
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


@st.cache(allow_output_mutation=True)
def load_babel():
    lista = []
    with open(os.path.join("./base/babel.txt"), "r") as babel:
        for line in babel:
            lista.append(line)
    return lista


def novo_babel(swap_pala):
    """
    :param swap_pala: quantas palavras por linhas no poema: 0 = rand; n = n-1 palavras
    :return: poema aleatório
    """

    lista_silabas = load_babel()
    sinais_ini = [".", ",", ":", "!", "?", "...", " "]
    sinais_end = [".", "!", "?", "..."]

    min_versos = 5
    max_versos = 15
    qtd_versos = random.randrange(min_versos, max_versos)

    sinal = "."
    novo_poema = []
    for nQtdLin in range(1, qtd_versos):
        novo_verso = ""
        if swap_pala == 0:
            qtd_palas = random.randrange(3, 7)
        else:
            qtd_palas = swap_pala

        for nova_frase in range(1, qtd_palas):
            nova_pala = ""
            qtd_silabas = random.randrange(2, 4)
            for palavra in range(1, qtd_silabas):
                njump = random.randrange(0, len(lista_silabas))
                nova_silaba = str(lista_silabas[njump])
                nova_pala += nova_silaba.strip()
            nova = nova_pala.replace("aa", "a")
            nova = nova.replace("ee", "e")
            nova = nova.replace("ii", "i")
            nova = nova.replace("uu", "u")
            novo_verso += nova.strip() + " "
            novo_verso.strip()

        if nQtdLin == 1:
            njump = random.randrange(0, len(sinais_ini))
            sinal = sinais_ini[njump]
            novo_poema.append("")
            novo_poema.append(novo_verso.strip() + sinal)
        else:
            nany = random.randrange(0, 99)
            if nany <= 50:
                njump = random.randrange(0, len(sinais_ini))
                sinal = sinais_ini[njump]
                novo_verso = novo_verso.rstrip() + sinal
            novo_poema.append(novo_verso.strip())
            if nany <= 50:  # put some ","
                if "," != sinal:
                    novo_poema.append("")

    last = novo_poema[-1]
    njump = random.randrange(0, len(sinais_end))
    sinal = sinais_end[njump]

    if len(last) > 1 and not last[-1] in sinais_ini:
        if "," == last or ":" == last:
            novo_poema[-1] += sinal
        else:
            novo_poema[-1] += "."

    return novo_poema
