"""

yPoems is an app that randomly collects words and phrases
from specific databases and organizes them
in thousands of new poems or poetic texts.

It's a slightly different project from the data science
and ML works I see on the web.

I believe it can be a good example of Streamlit's possibilities.

LYPO == Last YPOema created from curr_ypoema
TYPO == Translated Ypoema from LYPO
user_IP == the owner of LYPO and TYPO

"""

import os
import io
import random
import streamlit as st

# Project Modules
import SessionState
from lay_2_ypo import gera_poema

# TagCloud
from wordcloud import WordCloud
import matplotlib as mtl
import matplotlib.pyplot as plt

# user_IP: to create LYPO and TYPO for each hostname
import socket
hostname = socket.gethostname()
user_IP = socket.gethostbyname(hostname)

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

if internet():
    # Translators
    from deep_translator import GoogleTranslator
else:
    st.warning("Internet não conectada. Traduções não disponíveis no momento.")


st.set_page_config(
    page_title = 'yPoemas - a "machina" de fazer Poesia',
    page_icon = ":star:",
    layout = "centered",
    initial_sidebar_state = "auto")


# hide Streamlit Menu
st.markdown(""" <style>
MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html = True)


# change padding between components
padding = 0  # all set to zero
st.markdown(
    f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {.5}rem;
        padding-right: {.5}rem;
        padding-left: {.5}rem;
        padding-bottom: {.5}rem;
    }} </style> """, unsafe_allow_html = True)


# Initialize SessionState
session_state = SessionState.get(
    take = 0, book = "livro vivo", lang = "pt")


def main():
    pages = {
        "yPoemas": page_home,
        "books": page_books,
        "about": page_abouts,
        "license": page_license,}
        
    page = st.sidebar.radio("", tuple(pages.keys()))
    pages[page]()
    st.sidebar.info(load_file("PROJETO.md"))
    st.sidebar.image('./img_coffee.jpg')
    st.sidebar.info(load_file("COFFEE.md"))
    st.sidebar.state = True


# bof: loaders
# @st.cache(allow_output_mutation = True)
def load_file(file):  # Open files for about's
    # if isfile(file)
    try:
        with open(file, encoding = "utf8") as f:
            file_text = f.read()

        if file != "index.md":  # and...don't want to translate original titles.
            if not ".rol" in file:
                file_text = translate(file_text)
    except:
        file_text = "ooops... arquivo ( " + file + " ) não pode ser aberto. Sorry."
        
    return file_text


@st.cache(allow_output_mutation = True)
def load_tems(book):  # List of yPoemas' themes inside a Book
    temas_list = []
    full_name = os.path.join("./data/", book) + ".rol"
    # with io.open(full_name, encoding="ansi") as file:
    with open(full_name, encoding = "utf-8") as file:
        for line in file:
            temas_list.append(line)
    return temas_list


@st.cache(allow_output_mutation = True)
def load_index():  # Load indexes for all themes
    index_list = []
    with open(os.path.join("./data/index.txt"), encoding = "utf-8") as lista:
        for line in lista:
            index_list.append(line)
    return index_list


def load_lypo():  # load last yPoema & clean translator returned text
    lypo_text = ""
    lypo_user = "LYPO_" + user_IP
    with open(os.path.join("./temp/" + lypo_user), encoding = "utf-8") as script:
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
    typo_user = "TYPO_" + user_IP
    with open(os.path.join("./temp/" + typo_user), encoding = "utf-8") as script:
        for line in script:
            line = line.strip()
            line = line.replace("< br>", "<br>")
            line = line.replace("<br >", "")
            line = line.replace(" br>", "")
            line = line.replace(" >", "")
            typo_text += line + "<br>"
    return typo_text


def load_poema():  # generate new yPoema & save a copy of last generated in LYPO
    nome_tema = temas_list[session_state.take]
    script = gera_poema(nome_tema)

    novo_ypoema = ""
    lypo_user = "LYPO_" + user_IP

    with open(os.path.join("./temp/" + lypo_user), "w", encoding = "utf-8") as save_lypo:
        # save_lypo.write(nome_tema + '\n')  ## include title of yPoema in first line
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
    last_tema = len(temas_list) - 1
    if updn == ">":
        session_state.take += 1
        if session_state.take > last_tema:
            session_state.take = 0
    elif updn == "<":
        session_state.take -= 1
        if session_state.take < 0:
            session_state.take = last_tema
    else:
        session_state.take = random.randrange(0, last_tema, 1)
    return session_state.take


def say_numbers(index):  # search index title in index.txt
    indexes = load_index()
    analise = "nonono ..."
    this = temas_list[index].strip()
    for item in indexes:
        if item.startswith(this, 0, len(this)):
            analise = "#️ " + item
    return analise


def translate(input_text):
    if internet():
        try:
            output_text = GoogleTranslator(source = "auto", target = session_state.lang).translate(
                text = input_text
            )
        except IOError as exc:
            raise RuntimeError(
                "oops... Google Translator não está repondendo... Offline?"
            ) from exc
        return output_text
    else:
        return input_text

    
def tag_cloud():
    if session_state.lang == "pt":
        curr_ypoema = load_lypo()
    else:
        curr_ypoema = load_typo()

    text = ""
    word = ""
    for pals in curr_ypoema:
        if pals == ' ':
            word = word.replace("<br>", " ")
            if len(word) > 2:
                text += word + " "
            word = ""
        else:
            word += pals
            
    wordcloud = WordCloud(collocations=False, background_color='white').generate(text)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.margins(x=0, y=0)
    
    tags_expander = st.beta_expander("", True)
    with tags_expander:
        plt.show()
        st.pyplot()
# eof: functions


# bof: pages
def page_books():  # available books
    st.write("")
    st.sidebar.image('./img_books.jpg')
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
        session_state.take = 0
        session_state.book = this
        st.info(translate("escolha um livro e click em yPoemas para voltar à leitura..."))
        
    list_book = ""
    temas_list = load_tems(session_state.book)
    for line in temas_list:
        list_book += line
    show_expander = st.beta_expander("index", True)
    with show_expander:
        st.write(list_book)


def page_abouts():
    st.write("")
    st.sidebar.image('./img_about.jpg')

    about_expander = st.beta_expander("", True)
    with about_expander:
        abouts_list = [
            "machina",
            "bibliografia",
            "traduttore",
            "index",
            "outros",
        ]
        this = about_expander.radio("", abouts_list)

    show_expander = st.beta_expander("", True)
    with show_expander:
        st.subheader(load_file(this + ".md"))


def page_license():
    st.write("")
    st.sidebar.image('./img_license.jpg')
    licence_expander = st.beta_expander("", True)
    with licence_expander:
        st.subheader(load_file("LICENSE.md"))


last_idioma = session_state.lang
temas_list = load_tems(session_state.book)


def page_home():
    st.write("")
    st.sidebar.image('./img_home.jpg')
    # i1, i2, i3, i4, i5, i6, i7, last, rand, nest, numb, manu = st.beta_columns(
    #     [.9, .9, .85, .85, .9, .9, 1.4, .9, 1, 1.4, 0.9, 0.9]  # what a mess...
    i0, i1, i2, i3, i4, i5, i6, i7, i8 = st.beta_columns(
        [3, 1, 1, 1, 1, 1, 1, 1, 3]  # what a mess...
    )
    i1 = i1.button("pt", help = "Português")
    i2 = i2.button("es", help = "Español")
    i3 = i3.button("it", help = "Italiano")
    i4 = i4.button("fr", help = "Français")
    i5 = i5.button("en", help = "English")
    i6 = i6.button("de", help = "Deutsche")
    i7 = i7.button("ca", help = "Català")

    if i1:
        session_state.lang = "pt"
    elif i2:
        session_state.lang = "es"
    elif i3:
        session_state.lang = "it"
    elif i4:
        session_state.lang = "fr"
    elif i5:
        session_state.lang = "en"
    elif i6:
        session_state.lang = "de"
    elif i7:
        session_state.lang = "ca"

    b0, last, rand, nest, numb, manu, b1 = st.beta_columns(
        [4, 1, 1, 2, 1, 1, 4] ) # what a mess...

    if session_state.lang == "pt":
        last = last.button("◀", help = "anterior")
        rand = rand.button("✳", help = "escolhe tema ao acaso")
        nest = nest.button("▶", help = "próximo")
        bar_help = "barra de temas"
    elif session_state.lang == "es":
        last = last.button("◀", help = "anterior")
        rand = rand.button("✳", help = "elige un tema al azar")
        nest = nest.button("▶", help = "próximo")
        bar_help = "barra de temas"
    elif session_state.lang == "it":
        last = last.button("◀", help = "precedente")
        rand = rand.button("✳", help = "scegliere un tema a caso")
        nest = nest.button("▶", help = "prossimo")
        bar_help = "barra dei temi"
    elif session_state.lang == "fr":
        last = last.button("◀", help = "précédent")
        rand = rand.button("✳", help = "choisir le thème au hasard")
        nest = nest.button("▶", help = "prochain")
        bar_help = "barre à thèmes"
    elif session_state.lang == "en":
        last = last.button("◀", help = "last")
        rand = rand.button("✳", help = "pick theme at random")
        nest = nest.button("▶", help = "next")
        bar_help = "themes bar"
    elif session_state.lang == "ca":
        last = last.button("◀", help = "anterior")
        rand = rand.button("✳", help = "tria un tema a l'atzar")
        nest = nest.button("▶", help = "següent")
        bar_help = "barra de temes"
    elif session_state.lang == "de":
        last = last.button("◀", help = "letzte")
        rand = rand.button("✳", help = "ändert das thema zufällig")
        nest = nest.button("▶", help = "nächster")
        bar_help = "Themenleiste"
    else:  # for new languages...
        last = last.button("◀", help = "last")
        rand = rand.button("✳", help = "pick theme at random")
        nest = nest.button("▶", help = "next")
        bar_help = "barra de temas"

    if last:
        last_next("<")
    if rand:
        last_next("*")
    if nest:
        last_next(">")

    numb = numb.button("☁", help = say_numbers(session_state.take))
    manu = manu.button("?", help = "help !!!")
    
    lnew = True
    if manu:
        st.subheader(load_file("MANUAL.md"))
        lnew = False

    if numb:
        tag_cloud()
        lnew = False

    if lnew:
        info = (
            session_state.lang
            + " ( "
            + session_state.book
            + " ) ( "
            + str(session_state.take + 1)
            + "/"
            + str(len(temas_list))
            + " )"
        )

        options = list(range(len(temas_list)))
        session_state.take = st.selectbox(
            "",
            options,
            format_func = lambda x: temas_list[x],
            index=session_state.take,
            help = bar_help,
        )

        poemas_expander = st.beta_expander(
            info, expanded = True
        )
        with poemas_expander:
            if session_state.lang != last_idioma:
                curr_ypoema = load_lypo()
            else:
                if lnew:
                    curr_ypoema = load_poema()
                    curr_ypoema = load_lypo()
                else:
                    curr_ypoema = load_lypo()

            if session_state.lang != "pt":  # translate if idioma <> pt
                curr_ypoema = translate(curr_ypoema)
                typo_user = "TYPO_" + user_IP
                with open(
                    os.path.join("./temp/" + typo_user), "w", encoding = "utf-8"
                ) as save_typo:
                    save_typo.write(curr_ypoema)
                    save_typo.close()
                curr_ypoema = load_typo()  # to normalize line breaks in text

            st.markdown(curr_ypoema, unsafe_allow_html = True)  # finally... write it
# eof: pages


if __name__ == "__main__":
    main()
