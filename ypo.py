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

OVNY == Others Visitors Nos Ypoemas
VISY == New Visitor
NANY_VISY == Number of Visitors
LYPO == Last YPOema created from curr_ypoema
TYPO == Translated Ypoema from LYPO
POLY == Poliglot Idiom == Changed on Catalán
user_ip == the User IP for LYPO, TYPO

https://share.streamlit.io/nandoulopes/ypoemas/main/ypo.py
https://www.facebook.com/fernando.lopes.942/posts/3797156397062571?comment_id=3797297573715120&notif_id=1626293136581310&notif_t=feed_comment&ref=notif

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
if "poly_lang" not in st.session_state:
    st.session_state.poly_lang = "ca"
if "poly_name" not in st.session_state:
    st.session_state.poly_name = "català"
if "last_lang" not in st.session_state:
    st.session_state.last_lang = "pt"
if "visy" not in st.session_state:
    st.session_state.visy = True
if "nany_visy" not in st.session_state:
    st.session_state.nany_visy = 0


def update_visy():
    with open(os.path.join("./temp/visitors.txt"), "r", encoding="utf-8") as visitors:
        tots = int(visitors.read())
        tots = tots + 1
        st.session_state.nany_visy = tots
        
    with open(os.path.join("./temp/visitors.txt"), "w", encoding="utf-8") as visitors:
        visitors.write(str(tots))
    visitors.close()


if st.session_state.visy:
    update_visy()
    st.session_state.visy = False


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
        "comments": page_comments,
        "license": page_license,
    }
    page = st.sidebar.selectbox("Menu",tuple(pages.keys()))
    pages[page]()

    st.sidebar.info(load_file("PROJETO.md"))
    st.sidebar.button(" contatos: Face, Messenger, Whatsapp ", help="https://www.facebook.com/nandoulopes")
    st.sidebar.image("./img_coffee.jpg")
    st.sidebar.info(load_file("COFFEE.md"))
    st.sidebar.state = True


# human reading number functions for sorting
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


# bof: loaders
def load_readings():  # Lista de Temas + readings
    readers_list = []
    with open(os.path.join("./temp/readings.txt"), encoding="utf-8") as reader:
        for line in reader:
            readers_list.append(line)
    reader.close()
    return readers_list


def save_readings(this_read):
    with open(os.path.join("./temp/readings.txt"), "w", encoding="utf-8") as new_reader:
        for line in this_read:
            new_reader.write(line)
    new_reader.close()


def update_readings(tema):
    read_changes = []
    readings = load_readings()
    for line in readings:
        pipe_line = line.split("|")
        name = pipe_line[1]
        if name == tema:
            qtds = int(pipe_line[2]) + 1
            new_line = "|" + name + "|" + str(qtds) + "|\n"
            read_changes.append(new_line)
        else:
            read_changes.append(line)
    save_readings(read_changes)


def status_readings():
    totaliza = 0
    readonce = []
    tag_text = ""
    readings = load_readings()
    for line in readings:
        pipe_line = line.split("|")
        name = pipe_line[1]
        qtds = pipe_line[2]
        totaliza += int(qtds)
        if qtds != "0":
            new_line = str(qtds) + " - " + name + "\n"
            readonce.append(new_line)
            tag_text += name + " "
    readonce.sort(key=natural_keys, reverse=True)

    options = list(range(len(readonce)))
    opt_readings = st.selectbox(
        str(len(readonce)) + " temas, " + str(totaliza) + "/" + str(st.session_state.nany_visy) + " leituras",
        options,
        format_func=lambda x: readonce[x],
        key="box_readings",
    )
    tag_cloud(tag_text)


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



# @st.cache(allow_output_mutation=True)
def load_poly():  # Lista de Idiomas
    st.write("")
    poly_list = []
    # if not isfile()
    with open(os.path.join("./data/poly_en.txt"), encoding="utf-8") as poly:
        for line in poly:
            poly_list.append(line)
    poly.close()

    options = list(range(len(poly_list)))
    opt_poly = st.selectbox(
        str(len(poly_list)) + " idiomas",
        options,
        format_func=lambda x: poly_list[x],
        key="box_poly",
    )

    poly_name = poly_list[opt_poly].split("|")
    st.session_state.poly_name = poly_name[1]
    st.session_state.poly_lang = poly_name[2]
    
    old_lang = st.session_state.lang
    st.session_state.lang = st.session_state.poly_lang
    poly_news = []
    for line in poly_list:
        pipe_line = line.split("|")
        longo = translate(pipe_line[1])
        sigla = pipe_line[2]
        new_line = "|" + longo.lower() + "|" + sigla + "|\n"
        poly_news.append(new_line)
    
    save_poly(poly_news)
    st.session_state.lang = old_lang
    return poly_list


def save_poly(this_poly):
    with open(os.path.join("./data/poly_"+st.session_state.lang+".txt"), "w", encoding="utf-8") as new_poly:
        for line in this_poly:
            new_poly.write(line)
    new_poly.close()


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
    st.session_state.take = random.randrange(0, len(all_temas_list), 1)
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
    curr_take = st.session_state.take
    if updn == ">":
        curr_take += 1
        if curr_take > last_tema:
            curr_take = 0
    elif updn == "<":
        curr_take -= 1
        if curr_take < 0:
            curr_take = last_tema
    elif updn == "*":
        curr_take = random.randrange(0, last_tema, 1)
    elif updn == "#":
        st.session_state.take = curr_take
    return curr_take


def say_numbers(index):  # search index title in index.txt
    indexes = load_index()
    analise = "nonono ..."
    if index <= len(indexes):
        tema_op = all_temas_list[index].strip()
        for item in indexes:
            if item.startswith(tema_op, 0, len(tema_op)):
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
    if text == "_ypo_":
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

def get_seed_tema(this_tema):  # extract theme title for eureka
    ini = 0
    end = -1
    for letra in this_tema[0:-4]:
        end += 1
        if letra == "-":
            ini = end
    return this_tema[ini + 2 : end]


# eof: functions


# bof: pages
def page_eureka():
    st.write("")
    st.sidebar.image("./img_eureka.jpg")
    eureka_expander = st.beta_expander("", expanded=True)
    lexico_list = load_lexico()
    with eureka_expander:
        bb, hh = st.beta_columns([9.3,.7])
        with bb:
            busca = st.text_input(
                "digite uma palavra (ou parte dela) para buscar...",
            )
        with hh:
            aide = st.button("¿", help="help !!!")

        if aide:
            st.subheader(load_file("EUREKA.md"))

        if len(busca) > 2:
            seeds_list = []
            words_list = []
            temas_list = []
            for line in lexico_list:
                pipe_line = line.split("|")
                palas = pipe_line[1]
                fonte = pipe_line[2]
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
                        help="use letras para filtrar a lista",
                        format_func=lambda x: seeds_list[x],
                        key="box_seed",
                    )
            
                if opt_seed > len(seeds_list):  # just in case
                    opt_seed = 0
                    
                seed_tema = get_seed_tema(seeds_list[opt_seed])
            
                with btns:
                    more = st.button("+", help=say_numeros(seed_tema))
            
                curr_ypoema = load_poema(seed_tema, seeds_list[opt_seed])
                curr_ypoema = load_lypo()
                st.subheader(seed_tema)
                st.markdown(
                    curr_ypoema, unsafe_allow_html=True
                )  # finally... write it
                update_readings(seed_tema)
            else:
                st.warning("nenhum verbete encontrado com essas letras ---> " + busca)
        else:
            st.warning("digite pelo menos 3 letras...")


def page_abouts():
    st.write("")
    st.sidebar.image("./img_about.jpg")
    abouts_list = [
        "prefácio",
        "machina",
        "traduttore",
        "bibliografia",
        "outros",
        # "notes",
        "index",
    ]

    options = list(range(len(abouts_list)))
    opt_abouts = st.selectbox(
        "",
        options,
        format_func=lambda x: abouts_list[x],
        key="box_abouts",
    )

    about_expander = st.beta_expander("", True)
    with about_expander:
        st.subheader(load_file(abouts_list[opt_abouts].upper() + ".md"))


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

        options = list(range(len(books_list)))
        opt_book = st.selectbox(
            "",
            options,
            format_func=lambda x: books_list[x],
            key="box_books",
        )

        st.session_state.take = 0
        st.session_state.book = books_list[opt_book]
        st.info(
            translate("escolha um livro e click em yPoemas para voltar à leitura...")
        )

    list_book = ""
    all_temas_list = load_tems(st.session_state.book)
    for line in all_temas_list:
        list_book += line
    show_books_expander = st.beta_expander("index", True)
    with show_books_expander:
        st.write(list_book)


def page_comments():  # available comments
    st.write("")
    st.sidebar.image("./img_comments.jpg")
    comments_expander = st.beta_expander("", True)
    with comments_expander:
        st.subheader(load_file("COMMENTS.md"))


def page_license():
    st.write("")
    st.sidebar.image("./img_license.jpg")
    licence_expander = st.beta_expander("", True)
    with licence_expander:
        st.subheader(load_file("LICENSE.md"))


st.session_state.last_lang = st.session_state.lang
all_temas_list = load_tems(st.session_state.book)
st.session_state.take=last_next("#")


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
    i7 = i7.button("ca", help="català")
    # i7 = i7.button("☀", help=st.session_state.poly_name)

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
        # st.session_state.lang = st.session_state.poly_lang

    b0, last, rand, nest, numb, love, manu, b1 = st.beta_columns(
        [2, 1, 1, 1, 1, 1, 1, 2]
    )

    if st.session_state.lang == "pt":
        last = last.button("◀", help="anterior")
        rand = rand.button("★", help="escolhe tema ao acaso")
        nest = nest.button("▶", help="próximo")
        love = love.button("❤", help="mais lidos...")
    elif st.session_state.lang == "es":
        last = last.button("◀", help="anterior")
        rand = rand.button("★", help="elige un tema al azar")
        nest = nest.button("▶", help="próximo")
        love = love.button("❤", help="mas leídos...")
    elif st.session_state.lang == "it":
        last = last.button("◀", help="precedente")
        rand = rand.button("★", help="scegliere un tema a caso")
        nest = nest.button("▶", help="prossimo")
        love = love.button("❤", help="più letti...")
    elif st.session_state.lang == "fr":
        last = last.button("◀", help="précédent")
        rand = rand.button("★", help="choisir le thème au hasard")
        nest = nest.button("▶", help="prochain")
        love = love.button("❤", help="plus lus...")
    elif st.session_state.lang == "en":
        last = last.button("◀", help="last")
        rand = rand.button("★", help="pick theme at random")
        nest = nest.button("▶", help="next")
        love = love.button("❤", help="most read...")
    elif st.session_state.lang == "de":
        last = last.button("◀", help="letzte")
        rand = rand.button("★", help="ändert das thema zufällig")
        nest = nest.button("▶", help="nächster")
        love = love.button("❤", help="meistgelesenen...")
    elif st.session_state.lang == "ca":
        last = last.button("◀", help="anterior")
        rand = rand.button("★", help="tria un tema a l'atzar")
        nest = nest.button("▶", help="següent")
        love = love.button("❤", help="més llegits...")
    else:
    # elif st.session_state.lang == st.session_state.poly_lang:  # for new languages
        last = last.button("◀", help="last")
        rand = rand.button("★", help="pick theme at random")
        nest = nest.button("▶", help="next")
        love = love.button("❤", help="most read...")

    if last:
        st.session_state.take=last_next("<")
    if rand:
        st.session_state.take=last_next("*")
    if nest:
        st.session_state.take=last_next(">")

    numb = numb.button("☁", help=say_numbers(st.session_state.take))
    manu = manu.button("?", help="help !!!")

    lnew = True
    if love:
        lnew = False
        status_readings()
        # load_poly()

    if manu:
        lnew = False
        st.subheader(load_file("MANUAL.md"))

    if numb:
        lnew = False
        tag_cloud("_ypo_")

    if lnew:
        options = list(range(len(all_temas_list)))
        opt_ypo = st.selectbox(
            "",
            options,
            index = st.session_state.take,
            format_func = lambda x: all_temas_list[x],
        )
        if opt_ypo != st.session_state.take:
            st.session_state.take = opt_ypo
            st.session_state.take=last_next("#")
        
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
            st.subheader(all_temas_list[st.session_state.take])  # show nome_tema
            st.markdown(curr_ypoema, unsafe_allow_html=True)  # finally... write it
            update_readings(all_temas_list[st.session_state.take].strip())


# eof: pages


if __name__ == "__main__":
    main()
