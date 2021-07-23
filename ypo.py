"""

yPoemas is an app that randomly collects words and phrases
from specific databases and organizes them
in different new poems or poetic texts.

It's a slightly different project from the data science, NLP
and ML works I see around.
I believe it can be one more example of Streamlit's possibilities.

All texts are unique and will only be repeated  
after they are sold out the thousands  
of combinations possible to each theme.

LYPO == Last YPOema created from curr_ypoema
TYPO == Translated Ypoema from LYPO
user_ip == the User IP for LYPO, TYPO

® © ± ½ ¿ Æ Ø æ ¤ œ ™ € "|\n"

[ToDo] ---> retomar TTS - version 0.1.2
[ToDo] ---> página Comments
[ToDo] ---> Download Text, convert to image.jpg
[ToDo] ---> package for android/buildozer: MyPy_docs

"""

import os
import io
import re
import random
import streamlit as st

from datetime import datetime

# Project Module
from lay_2_ypo import gera_poema

# TagCloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# user_ip: to create LYPO and TYPO for each hostname
import socket


st.set_page_config(
    page_title='yPoemas - a "machina" de fazer Poesia',
    page_icon=":star:",
    layout="centered",
    initial_sidebar_state="auto",
)


hostname = socket.gethostname()
user_ip = socket.gethostbyname(hostname)


# hide Streamlit Menu
st.markdown(
    """ <style>
MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """,
    unsafe_allow_html=True,
)


# change padding between components
padding = 0  # all set to zero
st.markdown(
    f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {.5}rem;
        padding-right: {.5}rem;
        padding-left: {.5}rem;
        padding-bottom: {.5}rem;
    }} </style> """,
    unsafe_allow_html=True,
)


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


# Initialize SessionState
if "take" not in st.session_state:
    st.session_state.take = 0  #  index for selected tema
if "book" not in st.session_state:
    st.session_state.book = "livro vivo"
if "lang" not in st.session_state:
    st.session_state.lang = "pt"
if "last_lang" not in st.session_state:
    st.session_state.last_lang = "pt"
if "seed" not in st.session_state:
    st.session_state.seed = "brandidas"
if "visi" not in st.session_state:
    st.session_state.visi = True
if "ovni" not in st.session_state:
    st.session_state.ovni = 0


def update_visita():
    date_string = f'{datetime.now():%Y-%m-%d}'
    time_string = f'{datetime.now():%H:%M:%S%z}'
    user_data = "|" + user_ip + "|" + date_string + "|" + time_string + "|\n"
    with open(os.path.join("./temp/user_data.txt"), "a", encoding="utf-8") as data:
        data.write(user_data)
    data.close()

    with open(os.path.join("./temp/visita.txt"), "r", encoding="utf-8") as visita:
        tots = int(visita.read())
        tots = tots + 1
        st.session_state.ovni = tots
        
    with open(os.path.join("./temp/visita.txt"), "w", encoding="utf-8") as visita:
        visita.write(str(tots))
    visita.close()


if st.session_state.visi:
    update_visita()
    st.session_state.visi = False


if internet():
    from deep_translator import GoogleTranslator
else:
    st.warning("Internet não conectada. Traduções não disponíveis no momento.")


def main():
    pages = {
        "yPoemas": page_ypoemas,
        "eureka": page_eureka,
        "about": page_abouts,
        "books": page_books,
        "license": page_license,
    }

    page = st.sidebar.radio("", tuple(pages.keys()))
    pages[page]()
    st.sidebar.info(load_file("PROJETO.md"))
    st.sidebar.image("./img_coffee.jpg")
    st.sidebar.info(load_file("COFFEE.md"))
    st.sidebar.state = True


# human reading number functions for sorting
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


# bof: loaders
def load_leituras():  # Lista de Temas + readings
    leitor_list = []
    with open(os.path.join("./temp/leitor.txt"), encoding="utf-8") as leitor:
        for line in leitor:
            leitor_list.append(line)
    leitor.close()
    return leitor_list


def save_leituras(escritas):
    with open(os.path.join("./temp/leitor.txt"), "w", encoding="utf-8") as new_leitor:
        for line in escritas:
            new_leitor.write(line)
    new_leitor.close()


def update_leituras(tema):
    escritas = []
    leituras = load_leituras()
    for line in leituras:
        alinhas = line.split("|")
        name = alinhas[1]
        if name == tema:
            qtds = int(alinhas[2]) + 1
            new_line = "|" + name + "|" + str(qtds) + "|\n"
            escritas.append(new_line)
        else:
            escritas.append(line)
    save_leituras(escritas)


def status_leituras():
    totaliza = 0
    escritas = []
    selected = []
    tag_text = ""
    leituras = load_leituras()
    for line in leituras:
        alinhas = line.split("|")
        name = alinhas[1]
        qtds = alinhas[2]
        totaliza += int(qtds)
        if qtds != "0":
            selected.append(name)
            new_line = str(qtds) + " - " + name + "\n"
            escritas.append(new_line)
            tag_text += name + " "
    escritas.sort(key=natural_keys, reverse=True)

    options = list(range(len(escritas)))
    opt_leituras = st.selectbox(
        str(len(escritas)) + " temas, " + str(totaliza) + "/" + str(st.session_state.ovni) + " leituras",
        options,
        format_func=lambda x: escritas[x],
        key="box_ovni",
        )
    tag_cloud(tag_text)
    return escritas


@st.cache(allow_output_mutation=True)
def load_file(file):  # Open files for about's
    try:
        with open(os.path.join("./" + file), encoding="utf-8") as f:
            file_text = f.read()

        if file != "index.md":  # don't want to translate original titles
            if not ".rol" in file:
                file_text = translate(file_text)
    except:
        file_text = "ooops... arquivo ( " + file + " ) não pode ser aberto. Sorry."

    return file_text


@st.cache(allow_output_mutation=True)
def load_lexico():  # Lexicon for eureka
    index_lexico = []
    with open(os.path.join("./data/lexico_pt.txt"), encoding="utf-8") as lista:
        # with open(os.path.join("./data/"+"lexico_"+st.session_state.lang+".txt"), encoding = "utf-8") as lista:
        for line in lista:
            index_lexico.append(line)
    return index_lexico


@st.cache(allow_output_mutation=True)
def load_tems(book):  # List of yPoemas themes inside a Book
    all_temas_list = []
    full_name = os.path.join("./data/", book) + ".rol"
    with open(full_name, encoding="utf-8") as file:
        for line in file:
            all_temas_list.append(line)
    return all_temas_list


@st.cache(allow_output_mutation=True)
def load_index():  # Load indexes numbers for all themes
    index_list = []
    with open(os.path.join("./data/index.txt"), encoding="utf-8") as lista:
        for line in lista:
            index_list.append(line)
    return index_list


def load_lypo():  # load last yPoema & clean translator returned text
    lypo_text = ""
    lypo_user = "LYPO_" + user_ip
    with open(os.path.join("./temp/" + lypo_user), encoding="utf-8") as script:
        for line in script:
            line = line.strip()
            line = line.replace("< br>", "<br>")
            line = line.replace("<br >", "")
            line = line.replace(" br>", "")
            line = line.replace(" >", "")
            lypo_text += line + "<br>"
    return lypo_text


def load_typo():  # load translated yPoema & clean translator returned text
    typo_text = ""
    typo_user = "TYPO_" + user_ip
    with open(os.path.join("./temp/" + typo_user), encoding="utf-8") as script:
        for line in script:
            line = line.strip()
            line = line.replace("< br>", "<br>")
            line = line.replace("<br >", "")
            line = line.replace(" br>", "")
            line = line.replace(" >", "")
            typo_text += line + "<br>"
    return typo_text


def load_poema(
    nome_tema, seed_eureka
):  # generate new yPoema & save a copy of last generated in LYPO
    script = gera_poema(nome_tema, seed_eureka)
    novo_ypoema = ""
    lypo_user = "LYPO_" + user_ip

    with open(os.path.join("./temp/" + lypo_user), "w", encoding="utf-8") as save_lypo:
        # save_lypo.write(nome_tema + '\n')  # include title of yPoema in first line
        for line in script:
            if line == "\n":
                save_lypo.write("\n")
                novo_ypoema += "<br>"
            else:
                save_lypo.write(line + "\n")
                novo_ypoema += line + "<br>"
    save_lypo.close()
    return novo_ypoema


# eof: loaders


# bof: functions
def last_next(updn):  # handle last, random and next theme
    last_tema = len(all_temas_list) - 1
    if updn == ">":
        st.session_state.take += 1
        if st.session_state.take > last_tema:
            st.session_state.take = 0
    elif updn == "<":
        st.session_state.take -= 1
        if st.session_state.take < 0:
            st.session_state.take = last_tema
    else:
        st.session_state.take = random.randrange(0, last_tema, 1)
    return st.session_state.take


def say_numbers(index):  # search index title in index.txt
    indexes = load_index()
    analise = "nonono ..."
    this = all_temas_list[index].strip()
    for item in indexes:
        if item.startswith(this, 0, len(this)):
            analise = "#️ " + item
    return analise


def say_numeros(tema):  # search index title for eureka
    indexes = load_index()
    analise = "nonono ..."
    for item in indexes:
        if item.startswith(tema, 0, len(tema)):
            analise = "#️ " + item
    return analise


def translate(input_text):
    if internet():
        try:
            output_text = GoogleTranslator(
                source="auto", target=st.session_state.lang
            ).translate(text=input_text)
        except IOError as exc:
            raise RuntimeError(
                "oops... Google Translator não está repondendo... Offline?"
            ) from exc
        return output_text
    else:
        return input_text


def tag_cloud(text):
    if text == None:
        if st.session_state.lang == "pt":
            curr_ypoema = load_lypo()
        else:
            curr_ypoema = load_typo()
        
        text = ""
        word = ""
        for line in curr_ypoema:
            if line == " ":
                word = word.replace("<br>", " ")
                if len(word) > 2:
                    text += word + " "
                word = ""
            else:
                word += line

    wordcloud = WordCloud(collocations=False, background_color="white").generate(text)
    st.set_option("deprecation.showPyplotGlobalUse", False)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.margins(x=0, y=0)

    clouds_expander = st.beta_expander("", True)
    with clouds_expander:
        plt.show()
        st.pyplot()


def get_seed_tema(this):  # extract theme title for eureka
    minus = 0
    where = -1
    for letra in this[0:-4]:
        where += 1
        if letra == "-":
            minus = where
    maxis = where
    return this[minus + 2 : maxis]


# eof: functions


# bof: pages
def page_eureka():
    st.write("")
    st.sidebar.image("./img_eureka.jpg")
    eureka_expander = st.beta_expander("", expanded=True)
    lexico_list = load_lexico()
    with eureka_expander:
        # busca = st.session_state.seed
        busca = st.text_input(
            "digite uma palavra (ou parte dela) para buscar...",
        )
        if len(busca) > 2:
            seeds_list = []
            words_list = []
            temas_list = []
            # st.session_state.seed = busca
            for line in lexico_list:
                alinhas = line.split("|")
                palas = alinhas[1]
                fonte = alinhas[2]
                if busca.lower() in palas.lower():
                    seeds_list.append(palas + " - " + fonte)
                    this_tema = get_seed_tema(palas + " - " + fonte)
                    if not this_tema in temas_list:
                        temas_list.append(this_tema)
                    if not palas.lower() in words_list:
                        words_list.append(palas.lower())

            if len(seeds_list) > 0:
                tt, vv, oo, btns = st.beta_columns([2.3, 2.7, 5, 0.8])
            
                with tt:
                    options = list(range(len(temas_list)))
                    opt_tema = st.selectbox(
                        str(len(temas_list)) + " temas",
                        options,
                        format_func=lambda x: temas_list[x],
                        key="box_tema",
                    )
            
                with vv:
                    options = list(range(len(words_list)))
                    opt_word = st.selectbox(
                        str(len(words_list)) + " verbetes",
                        options,
                        format_func=lambda x: words_list[x],
                        key="box_word",
                    )
            
                with oo:
                    options = list(range(len(seeds_list)))
                    opt_seed = st.selectbox(
                        str(len(seeds_list)) + " ocorrências",
                        options,
                        help="digite algo a ser buscado na lista",
                        format_func=lambda x: seeds_list[x],
                        key="box_seed",
                    )
            
                if opt_seed > len(seeds_list):
                    opt_seed = 0
                seed_tema = get_seed_tema(seeds_list[opt_seed])
            
                with btns:
                    aide = st.button("¿", help=say_numeros(seed_tema))
                    more = st.button("+")
            
                if aide:
                    st.subheader(load_file("EUREKA.md"))
                else:
                    curr_ypoema = load_poema(seed_tema, seeds_list[opt_seed])
                    curr_ypoema = load_lypo()
                    st.subheader(seed_tema)
                    st.markdown(
                        curr_ypoema, unsafe_allow_html=True
                    )  # finally... write it
                    update_leituras(seed_tema)
            else:
                st.warning("nenhum verbete encontrado com essas letras ---> " + busca)
                # st.session_state.seed = ""
        else:
            st.warning("digite pelo menos 3 letras...")


def page_abouts():
    st.write("")
    st.sidebar.image("./img_about.jpg")
    about_expander = st.beta_expander("", True)
    with about_expander:
        abouts_list = [
            "machina",
            "traduttore",
            "bibliografia",
            "outros",
            # "notes",
            "index",
        ]
        this = about_expander.radio("", abouts_list)

    show_expander = st.beta_expander("", True)
    with show_expander:
        # st.subheader(load_file(this.upper() + ".md"))
        if this == "machina":
            st.subheader(load_file("MACHINA.md"))
        if this == "traduttore":
            st.subheader(load_file("TRADUTTORE.md"))
        if this == "bibliografia":
            st.subheader(load_file("BIBLIOGRAFIA.md"))
        if this == "outros":
            st.subheader(load_file("OUTROS.md"))
        # if this == "notes":
        #     st.subheader(load_file("NOTES.md"))
        if this == "index":
            st.subheader(load_file("INDEX.md"))


def page_books():  # available books
    st.write("")
    st.sidebar.image("./img_books.jpg")
    books_expander = st.beta_expander("", True)
    with books_expander:
        books_list = [
            "livro vivo",
            "poemas",
            "ensaios",
            "jocosos",
            "variações",
            "metalingua",
            "outros autores",
            "todos os temas",
            "todos os signos",
            "signos_fem",
            "signos_mas",
        ]
        this = books_expander.radio("", books_list)
        st.session_state.take = 0
        st.session_state.book = this
        st.info(
            translate("escolha um livro e click em yPoemas para voltar à leitura...")
        )

    list_book = ""
    all_temas_list = load_tems(st.session_state.book)
    for line in all_temas_list:
        list_book += line
    show_expander = st.beta_expander("index", True)
    with show_expander:
        st.write(list_book)


def page_license():
    st.write("")
    st.sidebar.image("./img_license.jpg")
    licence_expander = st.beta_expander("", True)
    with licence_expander:
        st.subheader(load_file("LICENSE.md"))


st.session_state.last_lang = st.session_state.lang
all_temas_list = load_tems(st.session_state.book)


def page_ypoemas():
    st.write("")
    st.sidebar.image("./img_home.jpg")
    i0, i1, i2, i3, i4, i5, i6, i7, i8 = st.beta_columns(
        [1.5, 1, 1, 1, 1, 1, 1, 1, 1.5]
    )
    i1 = i1.button("pt", help="Português")
    i2 = i2.button("es", help="Español")
    i3 = i3.button("it", help="Italiano")
    i4 = i4.button("fr", help="Français")
    i5 = i5.button("en", help="English")
    i6 = i6.button("de", help="Deutsche")
    i7 = i7.button("ca", help="Català")

    if i1:
        st.session_state.lang = "pt"
    elif i2:
        st.session_state.lang = "es"
    elif i3:
        st.session_state.lang = "it"
    elif i4:
        st.session_state.lang = "fr"
    elif i5:
        st.session_state.lang = "en"
    elif i6:
        st.session_state.lang = "de"
    elif i7:
        st.session_state.lang = "ca"

    b0, last, rand, nest, numb, love, manu, b1 = st.beta_columns(
        [2, 1, 1, 1, 1, 1, 1, 2]
    )

    if st.session_state.lang == "pt":
        last = last.button("◀", help="anterior")
        rand = rand.button("✳", help="escolhe tema ao acaso")
        nest = nest.button("▶", help="próximo")
    elif st.session_state.lang == "es":
        last = last.button("◀", help="anterior")
        rand = rand.button("✳", help="elige un tema al azar")
        nest = nest.button("▶", help="próximo")
    elif st.session_state.lang == "it":
        last = last.button("◀", help="precedente")
        rand = rand.button("✳", help="scegliere un tema a caso")
        nest = nest.button("▶", help="prossimo")
    elif st.session_state.lang == "fr":
        last = last.button("◀", help="précédent")
        rand = rand.button("✳", help="choisir le thème au hasard")
        nest = nest.button("▶", help="prochain")
    elif st.session_state.lang == "en":
        last = last.button("◀", help="last")
        rand = rand.button("✳", help="pick theme at random")
        nest = nest.button("▶", help="next")
    elif st.session_state.lang == "ca":
        last = last.button("◀", help="anterior")
        rand = rand.button("✳", help="tria un tema a l'atzar")
        nest = nest.button("▶", help="següent")
    elif st.session_state.lang == "de":
        last = last.button("◀", help="letzte")
        rand = rand.button("✳", help="ändert das thema zufällig")
        nest = nest.button("▶", help="nächster")
    else:  # for new languages, just in case...
        last = last.button("◀", help="last")
        rand = rand.button("✳", help="pick theme at random")
        nest = nest.button("▶", help="next")

    if last:
        last_next("<")
    if rand:
        last_next("*")
    if nest:
        last_next(">")

    numb = numb.button("☁", help=say_numbers(st.session_state.take))
    love = love.button("❤", help="mais lidos...")
    manu = manu.button("?", help="help !!!")

    lnew = True
    if love:
        lnew = False
        status_leituras()

    if manu:
        lnew = False
        st.subheader(load_file("MANUAL.md"))

    if numb:
        lnew = False
        tag_cloud()

    if lnew:
        options = list(range(len(all_temas_list)))
        opt_ypoema = st.selectbox(
            "",
            options,
            index=int(st.session_state.take),
            format_func=lambda x: all_temas_list[x],
            key="box_ypoe",
        )
        if opt_ypoema != st.session_state.take:
            st.session_state.take=opt_ypoema

        info = (
            st.session_state.lang
            + " ( "
            + st.session_state.book
            + " ) ( "
            + str(st.session_state.take + 1)
            + "/"
            + str(len(all_temas_list))
            + " )"
        )

        ypoemas_expander = st.beta_expander(info, expanded=True)
        with ypoemas_expander:
            if st.session_state.lang != st.session_state.last_lang:
                curr_ypoema = load_lypo()
            else:
                if lnew:
                    curr_ypoema = load_poema(all_temas_list[st.session_state.take], "")
                    curr_ypoema = load_lypo()
                else:
                    curr_ypoema = load_lypo()

            if st.session_state.lang != "pt":  # translate if idioma <> pt
                curr_ypoema = translate(curr_ypoema)
                typo_user = "TYPO_" + user_ip
                with open(
                    os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
                ) as save_typo:
                    save_typo.write(curr_ypoema)
                    save_typo.close()
                curr_ypoema = load_typo()  # to normalize line breaks in text
            # st.subheader(all_temas_list[st.session_state.take])  # show nome_tema
            st.markdown(curr_ypoema, unsafe_allow_html=True)  # finally... write it
            update_leituras(all_temas_list[st.session_state.take].strip())


# eof: pages


if __name__ == "__main__":
    main()
