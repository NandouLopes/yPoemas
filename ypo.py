"""
yPoemas is an app that randomly collects words and phrases
from specific databases and organizes them
in different new poems or poetic texts.

It's a slightly different project from the data science, NLP
and ML works I see around.
I believe it can be one more example of Streamlit's possibilities.

All texts are unique and will only be repeated  
after they are sold out the thourekasands  
of combinations possible to each theme.

[ToDo] - write_ypoema == write_text
[ToDo] - st.subheader == write_ypoema(load_file(manual_))

VISY == New Visitor
NANY_VISY == Number of Visitors
LYPO == Last YPOema created from curr_ypoema
TYPO == Translated YPOema from LYPO
POLY == Poliglot Idiom == Changed on Catalán
"""

import os
import io
import re
import time
import random
import base64
import datetime
import streamlit as st

# Project Module
from lay_2_ypo import gera_poema

# user_id: to create LYPO and TYPO for each hostname
import socket

# text-to-speech
from gtts import gTTS

from collections import deque

st.set_page_config(
    page_title='yPoemas - a "machina" de fazer Poesia',
    page_icon=":star:",
    layout="centered",
    initial_sidebar_state="auto",
)


try:
    from deep_translator import GoogleTranslator
except ImportError as ex:
    st.warning("Google Translator não conectado. Traduções não disponíveis no momento.")


def internet(host="8.8.8.8", port=53, timeout=3):  # ckeck internet
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
        raise RuntimeError(
            "Internet não conectada. Traduções não disponíveis no momento."
        )
        return False


# the User IP for LYPO, TYPO
hostname = socket.gethostname()
user_id = socket.gethostbyname(hostname)

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
        padding-top: {0}rem;
        padding-right: {0}rem;
        padding-left: {0}rem;
        padding-bottom: {0}rem;
    }} </style> """,
    unsafe_allow_html=True,
)

# change sidebar width
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 310px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 310px;
        margin-left: -320px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# change text area font
# <meta charset="UTF-8">
st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        /* padding-top: 10px !important; */
        font-weight: 700;
        font-size: 18px;
        font-family: 'IBM Plex Sans';
        color: #000000;
        padding-left: 15px;
    }
    .logo-img {
        float:right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize SessionState
if "lang" not in st.session_state:
    st.session_state.lang = "pt"
if "last_lang" not in st.session_state:
    st.session_state.last_lang = "pt"

if "book" not in st.session_state:  #  index for books_list
    st.session_state.book = "livro vivo"
if "take" not in st.session_state:  #  index for selected tema in books_list
    st.session_state.take = 0

if "off_book" not in st.session_state:  #  index for off_books_list
    st.session_state.off_book = 0
if "off_take" not in st.session_state:  #  index for selected book in off_books_list
    st.session_state.off_take = 0

if "poly_lang" not in st.session_state:
    st.session_state.poly_lang = "ca"
if "poly_name" not in st.session_state:
    st.session_state.poly_name = "català"
if "poly_take" not in st.session_state:
    st.session_state.poly_take = 12
if "poly_file" not in st.session_state:
    st.session_state.poly_file = "poly_pt.txt"

if "visy" not in st.session_state:
    st.session_state.visy = True
if "nany_visy" not in st.session_state:
    st.session_state.nany_visy = 0

if "find_word" not in st.session_state:
    st.session_state.find_word = "amor"

if "draw" not in st.session_state:
    st.session_state.draw = False
if "talk" not in st.session_state:
    st.session_state.talk = False

if "fila" not in st.session_state:
    st.session_state.fila = deque([])


def main():
    pages = {
        "mini": page_mini,
        "yPoemas": page_ypoemas,
        "eureka": page_eureka,
        "off-machina": page_off_machina,
        "poly": page_polys,
        "books": page_books,
        "comments": page_comments,
        "about": page_abouts,
    }

    page = st.sidebar.selectbox("", tuple(pages.keys()))
    pages[page]()
    show_icons()
    st.sidebar.state = True
    st.write("")


### bof: tools
# social media icons
def show_icons():
    st.sidebar.markdown(
        f"""
        <a href="https://www.facebook.com/nandoulopes" target="_blank"><button>facebook</button></a>
        <a href="mailto:lopes.fernando@hotmail.com" target="_blank"><button>email</button></a>
        <a href="https://www.instagram.com/fernando.lopes.942/" target="_blank"><button>insta</button></a>
        <a href="https://api.whatsapp.com/send?phone=+5512991368181" target="_blank"><button>whatsapp</button></a>
        """,
        unsafe_allow_html=True,
    )


# define idioma
def pick_lang():
    btn_pt, btn_es, btn_it, btn_fr, btn_en, btn_xy = st.sidebar.columns(
        [1.1, 1.13, 1.04, 1.04, 1.17, 1.25]
    )
    btn_pt = btn_pt.button("pt", help="Português")
    btn_es = btn_es.button("es", help="Español")
    btn_it = btn_it.button("it", help="Italiano")
    btn_fr = btn_fr.button("fr", help="Français")
    btn_en = btn_en.button("en", help="English")
    btn_xy = btn_xy.button("⚒️", help=st.session_state.poly_name)

    if btn_pt:
        st.session_state.lang = "pt"
        st.session_state.poly_file = "poly_pt.txt"
    elif btn_es:
        st.session_state.lang = "es"
        st.session_state.poly_file = "poly_es.txt"
    elif btn_it:
        st.session_state.lang = "it"
        st.session_state.poly_file = "poly_it.txt"
    elif btn_fr:
        st.session_state.lang = "fr"
        st.session_state.poly_file = "poly_fr.txt"
    elif btn_en:
        st.session_state.lang = "en"
        st.session_state.poly_file = "poly_en.txt"
    elif btn_xy:
        st.session_state.last_lang = st.session_state.lang
        st.session_state.lang = st.session_state.poly_lang


@st.cache(allow_output_mutation=True)
def load_help_tips():
    help_list = []
    with open(os.path.join("./base/helpers.txt"), encoding="utf-8") as file:
        for line in file:
            help_list.append(line)
    file.close()
    return help_list


# define help_tips
def load_help(idiom):
    returns = []
    if idiom in "_pt_es_it_fr_en":
        helpers = load_help_tips()
        for line in helpers:
            pipe_line = line.split("|")
            if pipe_line[1].startswith(idiom + "_"):
                text = pipe_line[2]
                returns.append(text)
    else:
        returns.append(translate("anterior"))
        returns.append(translate("escolhe tema ao acaso"))
        returns.append(translate("próximo"))
        returns.append(translate("mais lidos..."))
        returns.append(translate("gera novo yPoema"))
        returns.append(translate("imagens"))
        returns.append(translate("leituras"))
    return returns


# define draw & talk
def pick_draw():
    draw_text, talk_text = st.sidebar.columns([6.2, 3.8])
    help_me = load_help(st.session_state.lang)
    help_draw = help_me[5]
    help_talk = help_me[6]
    st.session_state.draw = draw_text.checkbox(help_draw, key="draw_machina")
    st.session_state.talk = talk_text.checkbox(help_talk, key="talk_machina")


# count one more visitor
def update_visy():
    with open(os.path.join("./temp/visitors.txt"), "r", encoding="utf-8") as visitors:
        tots = int(visitors.read())
        tots = tots + 1
        st.session_state.nany_visy = tots

    with open(os.path.join("./temp/visitors.txt"), "w", encoding="utf-8") as visitors:
        visitors.write(str(tots))
    visitors.close()


# check visitor once
if st.session_state.visy:  # used to random first text on yPoemas them, set to False
    update_visy()
    # st.session_state.visy = False  # checked later, on random first yPoema


# download files
def get_binary_file_downloader_html(bin_file, file_label="File"):
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">download {file_label}</a>'
    return href


# human reading number functions for sorting
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


### eof: tools
### bof: update themes readings


def load_readings():
    readers_list = []
    with open(os.path.join("./temp/read_list.txt"), encoding="utf-8") as reader:
        for line in reader:
            readers_list.append(line)
    reader.close()
    return readers_list


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

    with open(
        os.path.join("./temp/read_list.txt"), "w", encoding="utf-8"
    ) as new_reader:
        for line in read_changes:
            new_reader.write(line)
    new_reader.close()


def status_readings():
    sum_all_days = 0
    read_days = []  # days
    tag_text = ""
    readings = load_readings()
    for line in readings:
        pipe_line = line.split("|")
        name = pipe_line[1]
        qtds = pipe_line[2]
        sum_all_days += int(qtds)
        if qtds != "0":
            new_line = str(qtds) + " - " + name + "\n"
            if not "=" in name:  # out esoteric
                tag_text += name + " "
            read_days.append(new_line)

    read_days.sort(key=natural_keys, reverse=True)

    total_viewes = st.session_state.nany_visy
    currrent_day = datetime.date.today()
    begining_day = datetime.date(2021, 7, 6)
    days_of_runs = begining_day - currrent_day
    days_of_runs = abs(days_of_runs.days)
    views_by_day = total_viewes / days_of_runs
    reads_by_day = sum_all_days / total_viewes

    options = list(range(len(read_days)))
    opt_readings = st.selectbox(
        str(len(read_days)) + " temas, " + str(sum_all_days)
        + " leituras por "
        + str(total_viewes)
        + " visitantes ( "
        + str(int(views_by_day))
        + " / "
        + f"{reads_by_day:.2}"
        + " )",
        options,
        format_func=lambda x: read_days[x],
        key="opt_readings",
    )


### eof: update themes readings
### bof: loaders


@st.cache(allow_output_mutation=True)
def load_file(file):  # Open files for about's
    try:
        with open(os.path.join("./md_files/" + file), encoding="utf-8") as f:
            file_text = f.read()

        if not ".rol" in file:
            file_text = translate(file_text)
    except:
        file_text = "ooops... arquivo ( " + file + " ) não pode ser aberto. Sorry."
        st.session_state.lang = "pt"
    return file_text


@st.cache(allow_output_mutation=True)
def load_eureka(part_of_word):  # Lexicon
    index_eureka = []
    with open(os.path.join("./base/lexico_pt.txt"), encoding="utf-8") as lista:
        for line in lista:
            pipe_line = line.split("|")
            palas = pipe_line[1]
            fonte = pipe_line[2]
            if part_of_word.lower() in palas.lower():
                index_eureka.append(line)

    return index_eureka


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_temas(book):  # List of yPoemas themes inside a Book
    curr_temas_list = []
    with open(os.path.join("./base/" + book + ".rol"), "r", encoding="utf-8") as file:
        for line in file:
            curr_temas_list.append(line.strip("\n"))
    return curr_temas_list


@st.cache(allow_output_mutation=True)
def load_index():  # Load indexes numbers for all themes
    index_list = []
    with open(os.path.join("./base/index.txt"), encoding="utf-8") as lista:
        for line in lista:
            index_list.append(line)
    return index_list


def load_lypo():  # load last yPoema & replace "\n" with "<br>" for translator returned text
    lypo_text = ""
    lypo_user = "LYPO_" + user_id
    with open(os.path.join("./temp/" + lypo_user), encoding="utf-8") as script:
        for line in script:
            line = line.strip()
            lypo_text += line + "<br>"
    return lypo_text


def load_typo():  # load translated yPoema & clean translator returned bugs in text
    typo_text = ""
    typo_user = "TYPO_" + user_id
    with open(os.path.join("./temp/" + typo_user), encoding="utf-8") as script:
        for line in script:  # just 1 line
            line = line.strip()
            line = line.replace("< br>", "\n")
            line = line.replace("<br >", "\n")
            line = line.replace("<br ", "\n")
            line = line.replace(" br>", "\n")
            line = line.replace("> >", ">")
            typo_text += line + "<br>"
    return typo_text


@st.cache(allow_output_mutation=True)
def load_all_offs():
    all_books_off = [
        "a_torre_de_papel",
        "linguafiada",
        "quase_que_eu_Poesia",
    ]
    return all_books_off


@st.cache(allow_output_mutation=True)
def load_off_book(book):  # Load selected Book
    book_full = []
    full_name = os.path.join("./off_machina/", book) + ".Pip"
    with open(full_name, encoding="utf-8") as file:
        for line in file:
            book_full.append(line)
    return book_full


def load_book_pages(book):  # Load Book pages
    page = 0
    book_pages = []
    for line in book:
        if line.startswith("<EOF>"):
            break

        if line.startswith("|"):  # only valid lines in PIP
            page += 1
            pipe_line = line.split("|")
            # book_pages.append(pipe_line[1]+" ( " + str(page) + " )")
            book_pages.append(pipe_line[1])
    return book_pages


def load_poema(nome_tema, seed_eureka):  # generate new yPoema
    script = gera_poema(nome_tema, seed_eureka)
    novo_ypoema = ""
    lypo_user = "LYPO_" + user_id

    with open(os.path.join("./temp/" + lypo_user), "w", encoding="utf-8") as save_lypo:
        save_lypo.write(
            nome_tema
        )  # include title of yPoema in first line for translations
        save_lypo.write("\n")
        for line in script:
            if line == "\n":
                save_lypo.write("\n")
                novo_ypoema += "<br>"
            else:
                save_lypo.write(line + "\n")
                novo_ypoema += line + "<br>"
    save_lypo.close()  # save a copy of last generated in LYPO
    return novo_ypoema


def pick_arts(nome_tema):  # Select one image for arts
    animas = "_Atido_Avevida_Biaba_Cartaz_Ciuminho_Clandestino_Destinos_Escriba_Essa_Feiras_Frases_Fugaz_Indolor_Inhos_Lato_Manusgrite_Meteoro_Ocio_Oficio_Oco_Prefácil_Reger_Remedeio_Rever_Ser_Silente_Sinais_Sonoro_Sopros_Veio_Victor"
    esoteric = "_Astros_Distintos_Finalmentes_Rito_Zodiacaos"
    personas = "_Amaré_Amores_Buscas_Clarice_Cuores_Distintos_Dolores_Elogio_Enfrente_Gula_Isso_MachBeth_MachBrait_Mirante_Oca_Ogiva_Olhares_Papilio_Saudades_Sua_Zelo_Zoia"
    if (nome_tema in animas) or (
        nome_tema == "off_machina"
    ):  # primavera = teocrático = essa é a verdade.
        path = "./images/anima/"
    elif ("=" in nome_tema) or (nome_tema in esoteric):  # outono = aristocrático = a verdade pertence à...
        path = "./images/esoteric/"
    elif nome_tema in personas:  # verão = democrático = todos são donos da verdade!
        path = "./images/persona/"
    else:  # inverno = caótico == onde está a verdade? volta-se ao teocrático
        path = "./images/machina/"

    arts_list = []
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            arts_list.append(file)

    item = random.randrange(0, len(arts_list))
    image = arts_list[item]
    if image in st.session_state.fila:  # insert new image in last 24
        while not image in st.session_state.fila:
            item = random.randrange(0, len(arts_list))
            image = arts_list[item]

    st.session_state.fila.append(image)
    if len(st.session_state.fila) > 24:  # remove first
        st.session_state.fila.popleft()

    logo = path + image
    # print(image)
    return logo


def get_seed_tema(tema):  # extract theme title for eureka
    ini = 0
    end = -1
    for letra in tema[0:-4]:
        end += 1
        if letra == "-":
            ini = end
    return tema[ini + 2 : end]


def get_poly_name(poly):  # extract language name for poly
    pipe_line = poly.split("|")
    st.session_state.poly_name = translate(pipe_line[1])
    st.session_state.poly_lang = pipe_line[2]
    return True


### eof: loaders
### bof: functions


def write_ypoema(LOGO_TEXT, LOGO_IMAGE):  # ver save_img.py
    if LOGO_IMAGE == "none":
        st.markdown(
            f"""
            <div class="container">
                <p class="logo-text">{LOGO_TEXT}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="container">
                <img class="logo-img" src="data:image/jpg;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
                <p class="logo-text">{LOGO_TEXT}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def talk(text):  # text to speech(text in session_state.lang)
    text = text.replace("<br>", "\n")
    text = text.replace("< br>", "")
    text = text.replace("<br >", "")

    tts = gTTS(text=text, lang=st.session_state.lang, slow=False)
    nany_file = random.randint(1, 20000000)
    file_name = os.path.join("./temp/" + "audio" + str(nany_file) + ".mp3")
    tts.save(file_name)
    audio_file = open(file_name, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/ogg")
    audio_file.close()
    os.remove(file_name)


def say_numeros(tema):  # search index title for eureka
    analise = "#️ nonono"
    indexes = load_index()
    number = None
    for line in indexes:
        if line.startswith(tema):
            number = line.strip("\n")
            break

    if number is not None:
        analise = "#️ " + number
        if st.session_state.lang == "en":
            analise = analise.replace(".", ",")
        elif st.session_state.lang == "de":
            analise = analise.replace(".", " ")
    return analise


def translate(input_text):
    if st.session_state.lang == "pt":  # no need
        return input_text

    if internet():
        # try:
        output_text = GoogleTranslator(
            source="pt", target=st.session_state.lang
        ).translate(text=input_text)

        output_text = output_text.replace("<br>>", "<br>")
        output_text = output_text.replace("< br>", "<br>")
        output_text = output_text.replace("<br >", "<br>")
        output_text = output_text.replace("<br ", "<br>")
        output_text = output_text.replace(" br>", "<br>")
        return output_text
    else:
        st.session_state.lang = "pt"  # if no Internet then...
        return input_text


### eof: functions
### bof: pages


def page_polys():  # available languages
    st.sidebar.image("./images/img_poly.jpg")
    pick_lang()
    st.sidebar.info(load_file("INFO_POLY.md"))

    poly_expander = st.expander("", True)
    with poly_expander:
        pp, ok = st.columns([9.3, 0.7])
        with pp:
            poly_list = []
            poly_show = []
            with open(
                os.path.join("./base/" + st.session_state.poly_file), encoding="utf-8"
            ) as poly:
                for line in poly:
                    poly_list.append(line)
                    pipe_line = line.split("|")
                    poly_show.append(pipe_line[1] + " : " + pipe_line[2])
            poly.close()

            options = list(range(len(poly_show)))
            opt_poly = st.selectbox(
                str(len(poly_list)) + " idiomas",
                options,
                index=st.session_state.poly_take,
                format_func=lambda x: poly_show[x],
                key="opt_poly",
            )

        with ok:
            doit = st.button("✔", help="confirm ?")

        st.subheader(load_file("MANUAL_POLY.md"))

        if doit:
            get_poly_name(poly_list[opt_poly])
            st.session_state.poly_take = opt_poly
            st.session_state.last_lang = st.session_state.lang
            st.session_state.lang = st.session_state.poly_lang


def page_books():  # available books
    st.sidebar.image("./images/img_books.jpg")
    pick_lang()
    st.sidebar.info(load_file("INFO_BOOKS.md"))

    books_expander = st.expander("", True)
    with books_expander:
        bb, ok = st.columns([9.3, 0.7])
        with bb:
            books_list = [
                "livro vivo",
                "poemas",
                "jocosos",
                "ensaios",
                "variações",
                "metalingua",
                "todos os temas",
                "outros autores",
                "signos_fem",
                "signos_mas",
                "todos os signos",
            ]

            options = list(range(len(books_list)))
            opt_book = st.selectbox(
                "",
                options,
                index=books_list.index(st.session_state.book),
                format_func=lambda x: books_list[x],
                key="opt_book",
            )

            list_book = ""
            temas_list = load_temas(books_list[opt_book])
            for line in temas_list:
                list_book += line.strip() + ", "
            st.write(list_book[:-2])

        with ok:
            doit = st.button("✔", help="confirm ?")

        st.subheader(load_file("MANUAL_BOOKS.md"))

        if doit:
            st.session_state.take = 0
            st.session_state.book = books_list[opt_book]
            return None


def page_comments():  # available comments
    st.sidebar.image("./images/img_comments.jpg")
    pick_lang()
    st.sidebar.info(load_file("INFO_COMMENTS.md"))

    comments_expander = st.expander("", True)
    with comments_expander:
        st.subheader(load_file("MANUAL_COMMENTS.md"))


def page_abouts():
    st.sidebar.image("./images/img_about.jpg")
    pick_lang()
    st.sidebar.info(load_file("INFO_ABOUT.md"))

    abouts_list = [
        "machina",
        "prefácio",
        "off-machina",
        "outros",
        "imagens",
        "traduttore",
        "bibliografia",
        "samizdát",
        "pensares",
        "license",
        "notes",
        "index",
    ]

    options = list(range(len(abouts_list)))
    opt_abouts = st.selectbox(
        "",
        options,
        format_func=lambda x: abouts_list[x],
        key="opt_abouts",
    )

    about_expander = st.expander("", True)
    with about_expander:
        st.subheader(load_file("ABOUT_" + abouts_list[opt_abouts].upper() + ".md"))


st.session_state.last_lang = st.session_state.lang
temas_list = load_temas(st.session_state.book)
maxy = len(temas_list) - 1

if st.session_state.take > maxy:  # just in case
    st.session_state.take = 0

if st.session_state.visy:  # random text at first entry
    st.session_state.take = random.randrange(0, maxy, 1)
    st.session_state.visy = False


def page_mini():
    st.sidebar.image("./images/img_mini.jpg")
    pick_lang()
    pick_draw()
    st.sidebar.info(load_file("INFO_MINI.md"))

    temas_list = load_temas(st.session_state.book)
    maxy = len(temas_list) - 1

    mini_expander = st.expander("", expanded=True)
    with mini_expander:

        foo1, more, rand, foo2 = st.columns([3.5, 1, 1, 3.5])
        rand = rand.button("✴")
        
        if rand:
            st.session_state.take = random.randrange(0, maxy, 1)
        
        curr_tema = temas_list[st.session_state.take]
        analise = say_numeros(curr_tema)
        more = more.button("✔", help=analise)

        if st.session_state.lang != st.session_state.last_lang:
            curr_ypoema = load_lypo()  # changes in lang, keep LYPO
        else:
            curr_ypoema = load_poema(curr_tema, "")
            curr_ypoema = load_lypo()
        
        if st.session_state.lang != "pt":  # translate if idioma <> pt
            curr_ypoema = translate(curr_ypoema)
            typo_user = "TYPO_" + user_id
            with open(
                os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
            ) as save_typo:
                save_typo.write(curr_ypoema)
                save_typo.close()
            curr_ypoema = load_typo()  # to normalize line breaks in text
        
        update_readings(curr_tema)
        LOGO_TEXT = curr_ypoema
        LOGO_IMAGE = "none"
        
        if st.session_state.draw:
            LOGO_IMAGE = pick_arts(curr_tema)
        
        write_ypoema(LOGO_TEXT, LOGO_IMAGE)
        
        if st.session_state.talk:
            talk(curr_ypoema)


def page_ypoemas():
    st.sidebar.image("./images/img_ypoemas.jpg")
    pick_lang()
    pick_draw()
    st.sidebar.info(load_file("INFO_YPOEMAS.md"))

    buttons_expander = st.expander("", expanded=True)
    with buttons_expander:
        foo1, more, last, rand, nest, manu, foo2 = st.columns(
            [2, 1, 1, 1, 1, 1, 2]
        )
        
        help_me = load_help(st.session_state.lang)
        help_last = help_me[0]
        help_rand = help_me[1]
        help_nest = help_me[2]
        help_more = help_me[4]

        more = more.button("✔", help=help_more)
        last = last.button("◀", help=help_last)
        rand = rand.button("✴", help=help_rand)
        nest = nest.button("▶", help=help_nest)
        
        if last:
            st.session_state.take -= 1
            if st.session_state.take < 0:
                st.session_state.take = maxy
        
        if rand:
            st.session_state.take = random.randrange(0, maxy, 1)
        
        if nest:
            st.session_state.take += 1
            if st.session_state.take > maxy:
                st.session_state.take = 0
        
        options = list(range(len(temas_list)))
        opt_take = st.selectbox(
            "",
            options,
            index=st.session_state.take,
            format_func=lambda z: temas_list[z],
            key="opt_take",
        )

    if opt_take != st.session_state.take:
        st.session_state.take = opt_take

    curr_tema = temas_list[st.session_state.take]
    analise = say_numeros(curr_tema)
    manu = manu.button("?", help=analise)

    lnew = True
    if manu:
        lnew = False
        st.subheader(load_file("MANUAL_YPOEMAS.md"))

    if lnew:
        info = (
            "⚫  "
            + st.session_state.lang
            + " ( "
            + st.session_state.book
            + " ) ( "
            + str(st.session_state.take + 1)
            + " / "
            + str(len(temas_list))
            + " )"
        )

        ypoemas_expander = st.expander(info, expanded=True)
        with ypoemas_expander:
            if st.session_state.lang != st.session_state.last_lang:
                curr_ypoema = load_lypo()  # changes in lang, keep LYPO
            else:
                curr_ypoema = load_poema(curr_tema, "")
                curr_ypoema = load_lypo()

            if st.session_state.lang != "pt":  # translate if idioma <> pt
                curr_ypoema = translate(curr_ypoema)
                typo_user = "TYPO_" + user_id
                with open(
                    os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
                ) as save_typo:
                    save_typo.write(curr_ypoema)
                    save_typo.close()
                curr_ypoema = load_typo()  # to normalize line breaks in text

            update_readings(curr_tema)
            LOGO_TEXT = curr_ypoema
            LOGO_IMAGE = "none"
            if st.session_state.draw:
                LOGO_IMAGE = pick_arts(curr_tema)

            write_ypoema(LOGO_TEXT, LOGO_IMAGE)

        if st.session_state.talk:
            talk(curr_ypoema)
        # st.markdown(get_binary_file_downloader_html('./temp/'+"LYPO_" + user_id, curr_tema), unsafe_allow_html=True)
        # bin_file = base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()+LOGO_TEXT
        # st.markdown(get_binary_file_downloader_html(bin_file, curr_tema), unsafe_allow_html=True)



def page_eureka():
    st.sidebar.image("./images/img_eureka.jpg")
    pick_lang()
    pick_draw()
    st.sidebar.info(load_file("INFO_EUREKA.md"))

    help_me = load_help(st.session_state.lang)
    help_more = help_me[4]

    seed, more, aide, occurrences = st.columns([2.8, 1.6, 0.6, 4.5])

    with seed:
        find_what = st.text_input(
            label=translate("digite algo para buscar..."),
            value=st.session_state.find_word,
        )

    with more:
        more = more.button("✔", help=help_more)

    if len(find_what) < 3:
        st.warning("digite pelo menos 3 letras...")
    else:
        seed_list = []
        eureka_list = load_eureka(find_what)

        for line in eureka_list:
            pipe_line = line.split("|")
            palas = pipe_line[1]
            fonte = pipe_line[2]
            if palas is None or fonte is None:
                continue
            else:
                seed_list.append(palas + " - " + fonte)

        if len(seed_list) > 0:
            st.session_state.find_word = find_what
            eureka_expander = st.expander("", expanded=True)
            with eureka_expander:
                seed_list.sort()
                if len(seed_list) == 1:
                    info_find = "ocorrência"
                else:
                    info_find = "ocorrências"

                with occurrences:
                    opt_ocur = st.selectbox(
                        str(len(seed_list)) + " " + translate(info_find),
                        list(range(len(seed_list))),
                        format_func=lambda y: seed_list[y],
                        key="opt_ocur",
                    )

                if (opt_ocur < 0) or (opt_ocur > len(seed_list)):
                    opt_ocur = 0

                seed_tema = get_seed_tema(seed_list[opt_ocur])
                this_seed = seed_list[opt_ocur]
                analise = say_numeros(seed_tema)
                with aide:
                    aide = st.button("?", help=analise)

                if st.session_state.lang != st.session_state.last_lang:
                    curr_ypoema = load_lypo()  # changes in lang, keep LYPO
                else:
                    curr_ypoema = load_poema(seed_tema, this_seed)
                    curr_ypoema = load_lypo()

                if st.session_state.lang != "pt":  # translate if idioma <> pt
                    curr_ypoema = translate(curr_ypoema)
                    typo_user = "TYPO_" + user_id
                    with open(
                        os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
                    ) as save_typo:
                        save_typo.write(curr_ypoema)
                        save_typo.close()
                    curr_ypoema = load_typo()  # to normalize line breaks in text

                LOGO_TEXT = curr_ypoema
                LOGO_IMAGE = "none"
                if st.session_state.draw:
                    LOGO_IMAGE = pick_arts(seed_tema)

                write_ypoema(LOGO_TEXT, LOGO_IMAGE)
                update_readings(seed_tema)

            if aide:
                lnew = False
                st.subheader(load_file("MANUAL_EUREKA.md"))

            if st.session_state.talk:
                talk(curr_ypoema)
        else:
            st.warning("nenhum verbete encontrado com essas letras ---> " + find_what)


def page_off_machina():  # available off_books
    st.sidebar.image("./images/img_off_machina.jpg")
    pick_lang()
    pick_draw()
    st.sidebar.info(load_file("INFO_OFF-MACHINA.md"))

    off_books_list = load_all_offs()
    options = list(range(len(off_books_list)))
    opt_off_book = st.selectbox(
        "",
        options,
        index=st.session_state.off_book,
        format_func=lambda x: off_books_list[x],
        help="books",
        key="opt_off_book",
    )

    if opt_off_book != st.session_state.off_book:
        st.session_state.off_book = opt_off_book
        st.session_state.off_take = 0
    off_book_name = off_books_list[st.session_state.off_book]

    help_me = load_help(st.session_state.lang)
    help_last = help_me[0]
    help_rand = help_me[1]
    help_nest = help_me[2]
    help_love = help_me[3]

    foo1, last, rand, nest, love, manu, foo2 = st.columns([2.5, 1, 1, 1, 1, 1, 2.5])
    last = last.button("◀", help=help_last)
    rand = rand.button("✴", help=help_rand)
    nest = nest.button("▶", help=help_nest)
    love = love.button("✈", help=help_love)
    manu = manu.button("?", help="help !!!")

    this_off_book = load_off_book(off_book_name)
    off_book_pagys = load_book_pages(this_off_book)

    maxy_off = len(off_book_pagys) - 1
    if last:
        st.session_state.off_take -= 1
        if st.session_state.off_take < 0:
            st.session_state.off_take = maxy_off

    if rand:
        st.session_state.off_take = random.randrange(0, maxy_off, 1)

    if nest:
        st.session_state.off_take += 1
        if st.session_state.off_take > maxy_off:
            st.session_state.off_take = 0

    if st.session_state.off_take > maxy_off:  # just in case...
        st.session_state.off_take = 0

    options = list(range(len(off_book_pagys)))
    opt_off_take = st.selectbox(
        "",
        options,
        index=st.session_state.off_take,
        format_func=lambda x: off_book_pagys[x],
        key="opt_off_take",
    )

    if opt_off_take != st.session_state.off_take:
        st.session_state.off_take = opt_off_take

    lnew = True
    if manu:
        lnew = False
        st.subheader(load_file("MANUAL_OFF-MACHINA.md"))

    if love:
        lnew = False
        status_readings()
        st.markdown(
            get_binary_file_downloader_html("./temp/read_list.txt", "views"),
            unsafe_allow_html=True,
        )

    if lnew:
        info = (
            "⚫  "
            + st.session_state.lang
            + " ( "
            + str(st.session_state.off_take + 1)
            + "/"
            + str(len(off_book_pagys))
            + " )"
        )

        off_machina_expander = st.expander(info, True)
        with off_machina_expander:
            off_book_text = ""
            pipe_line = this_off_book[st.session_state.off_take].split("|")
            if "@ " in pipe_line[1]:
                if st.session_state.lang != st.session_state.last_lang:
                    off_book_text = load_lypo()  # changes in lang, keep LYPO
                else:
                    nome_tema = pipe_line[1].replace("@ ", "")
                    off_book_text = load_poema(nome_tema, "")  # no seed_eureka
                    off_book_text = "<br>" + load_lypo()
            else:
                for text in pipe_line:
                    off_book_text += text + "<br>"

            capo = st.session_state.off_take == 0

            if capo:
                capa, isbn = st.columns([2.5, 7.5])
                with capa:
                    st.image(
                        "./off_machina/capa_" + off_book_name + ".jpg",
                        use_column_width=True,
                    )
                with isbn:
                    st.markdown(
                        off_book_text, unsafe_allow_html=True
                    )  # finally... write it
            else:
                if st.session_state.lang != "pt":
                    off_book_text = translate(off_book_text)

                # st.markdown(off_book_text, unsafe_allow_html=True)  # finally... write it
                LOGO_TEXT = off_book_text
                LOGO_IMAGE = "none"
                if st.session_state.draw:
                    LOGO_IMAGE = pick_arts("off_machina")

                write_ypoema(LOGO_TEXT, LOGO_IMAGE)
                update_readings(off_book_name)

        if st.session_state.talk:
            talk(off_book_text)


### eof: pages


if __name__ == "__main__":
    main()
