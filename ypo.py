r"""
st.session_state.seed
yPoemas is an app that randomly collects words and phrases
from specific databases and organizes them
in different new poems or poetic texts.

All texts are unique and will only be repeated  
after they are sold out the thourekasands  
of combinations possible to each theme.

[Epitaph]
Passei boa parte da minha vida escrevendo a "machina".
A leitura fica para os amanhãs.
Não vivo no meu tempo.

share : https://share.streamlit.io/
deploy: https://share.streamlit.io/nandoulopes/ypoemas/main/ypo.py
config: chrome://settings/content/siteDetails?site=https%3A%2F%2Fauth.streamlit.io
transl: https://translate.google.com/

users_id changed to IPAddr

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
import socket  # Internet
import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime

# Project Modules
from lay_2_ypo import gera_poema

### bof: settings

# from PIL import Image
# img=Image.open('logo_ypo.png')
#     page_icon=img,
st.set_page_config(
    page_title='a máquina de fazer Poesia - yPoemas',
    page_icon=":star:",
    layout="centered",
    initial_sidebar_state="auto",
)


try:
    from deep_translator import GoogleTranslator
except ImportError as ex:
    st.warning("Google Translator não conectado. Traduções não disponíveis no momento.")


try:
    from gtts import gTTS
except ImportError as ex:
    st.warning("Google TTS não conectado. Leituras não disponíveis no momento.")

def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        st.warning("Internet não conectada. Traduções não disponíveis no momento.")
        return False


# the User IPAddres for LYPO, TYPO
hostname = socket.gethostname()
IPAddres = socket.gethostbyname(hostname)


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
#       background-color:rgba(255, 99, 71, 0.1);
#       opacity: .9;
st.markdown(
    """
    <style>
    mark {
      background-color: lightblue;
      color: black;
    }
    .container {
        display: flex;
    }
    .logo-text {
        /* padding-top: 10px !important; */
        font-weight: 900;
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
    st.session_state.book = "todos os temas"
if "take" not in st.session_state:  #  index for selected tema in books_list
    st.session_state.take = 0
if "mini" not in st.session_state:  #  index for selected tema in page_mini
    st.session_state.mini = 0
if "tema" not in st.session_state:  #  selected tema for all pages
    st.session_state.tema = 'Fatos'
    
if "off_book" not in st.session_state:   #  index for off_books_list
    st.session_state.off_book = 0
if "off_take" not in st.session_state:   #  index for selected book in off_books_list
    st.session_state.off_take = 0

if "eureka" not in st.session_state:     #  index for random tema in page_eureka
    st.session_state.eureka = 0
if "find_word" not in st.session_state:  #  palavra para buscar em eureka
    st.session_state.find_word = "amar"

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

if "draw" not in st.session_state:
    st.session_state.draw = False
if "talk" not in st.session_state:
    st.session_state.talk = False
if "vide" not in st.session_state:
    st.session_state.vide = False

if "arts" not in st.session_state:
    st.session_state.arts = []

### eof: settings
### bof: tools

def show_icons():  # https://api.whatsapp.com/
    st.sidebar.markdown(
        f"""
        <nav>
        <a href="https://www.facebook.com/nandoulopes" target="_blank">facebook</a> |
        <a href="mailto:lopes.fernando@hotmail.com" target="_blank">e-mail</a> |
        <a href="https://www.instagram.com/fernando.lopes.942/" target="_blank">instagram</a> |
        <a href="https://web.whatsapp.com/send?phone=+5512991368181" target="_blank">whatsapp</a>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def pick_lang():  # define idioma
    btn_pt, btn_es, btn_it, btn_fr, btn_en, btn_xy = st.sidebar.columns(
        [1.1, 1.13, 1.04, 1.04, 1.17, 1.25]
    )
    btn_pt = btn_pt.button("pt", key=1, help="Português")
    btn_es = btn_es.button("es", key=2, help="Español")
    btn_it = btn_it.button("it", key=3, help="Italiano")
    btn_fr = btn_fr.button("fr", key=4, help="Français")
    btn_en = btn_en.button("en", key=5, help="English")
    btn_xy = btn_xy.button("⚒️",  key=6, help=st.session_state.poly_name)
    
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
        
    if st.session_state.lang != st.session_state.last_lang:
        st.success('idioma atual ➪ '+st.session_state.lang)


@st.cache(allow_output_mutation=True)
def load_help_tips():
    help_list = []
    with open(os.path.join("./base/helpers.txt"), encoding="utf-8") as file:
        for line in file:
            help_list.append(line)
    file.close()
    return help_list


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
        returns.append(translate("imagem"))
        returns.append(translate("áudio"))
        returns.append(translate("vídeo"))
    return returns


def pick_draw():
    draw_text, talk_text, vyde_text = st.sidebar.columns([3.8, 3.2, 3])
    help_me = load_help(st.session_state.lang)
    help_draw = help_me[5]
    help_talk = help_me[6]
    help_vyde = help_me[7]
    st.session_state.draw = draw_text.checkbox(help_draw, st.session_state.draw, key="draw_machina")
    st.session_state.talk = talk_text.checkbox(help_talk, st.session_state.talk, key="talk_machina")
    st.session_state.vide = vyde_text.checkbox(help_vyde, st.session_state.vide, key="vyde_machina")


def get_binary_file_downloader_html(bin_file, file_label="File"):
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">download {file_label}</a>'
    return href


def atoi(text):  # human reading number functions for sorting
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


### eof: tools
### bof: update themes readings


def update_visy():  # count one more visitor
    with open(os.path.join("./temp/visitors.txt"), "r", encoding="utf-8") as visitors:
        tots = int(visitors.read())
        tots = tots + 1
        st.session_state.nany_visy = tots

    with open(os.path.join("./temp/visitors.txt"), "w", encoding="utf-8") as visitors:
        visitors.write(str(tots))
    visitors.close()


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


def list_readings():
    sum_all_days = 0
    read_days = []  # days
    readings = load_readings()
    for line in readings:
        pipe_line = line.split("|")
        name = pipe_line[1]
        qtds = pipe_line[2]
        sum_all_days += int(qtds)
        if qtds != "0":
            new_line = str(qtds) + " - " + name + "\n"
            read_days.append(new_line)

    read_days.sort(key=natural_keys, reverse=True)

    total_viewes = st.session_state.nany_visy
    currrent_day = datetime.now()
    begining_day = datetime(2021, 7, 6)
    days_of_runs = begining_day - currrent_day
    days_of_runs = abs(days_of_runs.days)
    views_by_day = total_viewes / days_of_runs
    reads_by_day = sum_all_days / total_viewes

    options = list(range(len(read_days)))  # ↓  '⚫  ' '↓'
    opt_readings = st.selectbox(
        '↓  ' + str(len(read_days)) + " temas, " + str(sum_all_days)
        + " leituras por "
        + str(total_viewes)
        + " visitantes ( "
        + str(int(views_by_day))
        + " / "
        + f"{reads_by_day:.2}"
        + " ) ( "
        + IPAddres + ' )',
        options,
        format_func=lambda x: read_days[x],
        key="opt_readings",
    )


### eof: update themes readings
### bof: loaders


@st.cache(allow_output_mutation=True)
def load_md_file(file):  # Open files for about's
    try:
        with open(os.path.join("./md_files/" + file), encoding="utf-8") as file_to_open:
            file_text = file_to_open.read()

        if not ".rol" in file:
            file_text = translate(file_text)
    except:
        file_text = translate('ooops... arquivo ( ' + file + ' ) não pode ser aberto.')
        st.session_state.lang = "pt"
    return file_text


@st.cache(allow_output_mutation=True)
def load_eureka(part_of_word):  # Lexicon
    lexico_list = []
    with open(os.path.join("./base/lexico_pt.txt"), encoding="utf-8") as lista:
        for line in lista:
            palas_fonte = line.strip("\n")
            part_string = palas_fonte.partition(' : ')
            palas = part_string[0]
            fonte = part_string[2]
            if part_of_word.lower() in palas.lower():
                lexico_list.append(line)
    return lexico_list


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_temas(book):  # List of yPoemas themes inside a Book
    book_list = []
    with open(os.path.join("./base/" + book + ".rol"), "r", encoding="utf-8") as file:
        for line in file:
            book_list.append(line.strip("\n"))
    return book_list


@st.cache(allow_output_mutation=True)
def load_info(nome_tema):
    with open(os.path.join("./base/" + "info.txt"), "r", encoding="utf-8") as file:
        result = ""
        for line in file:
            if line.startswith("|"):
                pipe = line.split("|")
                if pipe[1].upper() == nome_tema.upper():
                    genero = pipe[2]
                    imagem = pipe[3]
                    qtd_versos = pipe[4]
                    qtd_wordin = pipe[5]
                    qtd_lexico = pipe[6]
                    qtd_itimos = pipe[7]
                    qtd_analiz = pipe[8]
                    qtd_cienti = pipe[9]
                    result += "<br>"
                    result += "<br>"
                    result += "<br>"
                    result += "Titulo: " + nome_tema + "<br>"
                    result += "Gênero: " + genero + "  " + "<br>"
                    result += "Imagem: " + imagem + "  " + "<br>"
                    result += "Versos: " + qtd_versos + "  " + "<br>"
                    result += "Verbetes no texto: " + qtd_wordin + "  " + "<br>"
                    result += "Verbetes  do Tema: " + qtd_lexico + "  " + "<br>"
                    result += "• Banco de Ítimos: " + qtd_itimos + "  " + "<br>"
                    result += "Análise : " + qtd_analiz + "  " + "<br>"
                    result += "Notação Científica: " + qtd_cienti + "  " + "<br>"
                    result += "<br>"

        return result


@st.cache(allow_output_mutation=True)
def load_index():  # Load indexes numbers for all themes
    index_list = []
    with open(os.path.join("./md_files/ABOUT_INDEX.md"), encoding="utf-8") as lista:
        for line in lista:
            index_list.append(line)
    return index_list


def load_lypo():  # Load last yPoema & replace "\n" with "<br>" for translator returned text
    lypo_text = ""
    lypo_user = "LYPO_" + IPAddres
    with open(os.path.join("./temp/" + lypo_user), encoding="utf-8") as script:
        for line in script:
            line = line.strip()
            lypo_text += line + "<br>"
    return lypo_text


def load_typo():  # Load translated yPoema & clean translator returned bugs in text
    typo_text = ""
    typo_user = "TYPO_" + IPAddres
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
        "livro_vivo",
        "faz_de_conto",
        "um_romance",
        "quase_que_eu_Poesia",
    ]
    return all_books_off


@st.cache(allow_output_mutation=True)
def load_off_book(book):  # Load selected off_book
    book_full = []
    full_name = os.path.join("./off_machina/", book) + ".Pip"
    with open(full_name, encoding="utf-8") as file:
        for line in file:
            book_full.append(line)
    return book_full


def load_book_pages(book):  # Load Book pages for off_book
    page_numer = 0
    book_pages = []
    for line in book:
        if line.startswith("<EOF>"):
            break

        if line.startswith("|"):  # only valid lines in PIP
            page_numer += 1
            pipe_line = line.split("|")
            # book_pages.append(pipe_line[1]+" ( " + str(page_numer) + " )")
            book_pages.append(pipe_line[1])
    return book_pages


def load_poema(nome_tema, seed_eureka):  # generate new yPoema
    script = gera_poema(nome_tema, seed_eureka)
    novo_ypoema = ""
    lypo_user = "LYPO_" + IPAddres

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


@st.cache(allow_output_mutation=True)
def load_images():
    images_list = []
    with open(os.path.join("./base/images.txt"), encoding="utf-8") as lista:
        for line in lista:
            images_list.append(line)
    return images_list
    

def load_arts(nome_tema):  # Select image for arts
    path = "./images/machina/"
    path_list = load_images()
    for line in path_list:
        if line.startswith(nome_tema):
            string = line.strip("\n")
            part_string = string.partition(' : ')
            if nome_tema == part_string[0]:
                path = "./images/" + part_string[2] + "/"
                break

    arts_list = []
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            arts_list.append(file)

    item = random.randrange(0, len(arts_list))
    image = arts_list[item]

    if image in st.session_state.arts:  # insert new image
        while image in st.session_state.arts:
            item = random.randrange(0, len(arts_list))
            image = arts_list[item]
        st.session_state.arts.append(image)
        image = st.session_state.arts[-1]
    else:
        st.session_state.arts.append(image)

    if len(st.session_state.arts) > 36:  # remove first
        del st.session_state.arts[0]

    # print(image)  # debug time check
    logo = path + image
    return logo


def get_seed_tema(tema):  # extract theme title for eureka
    ini = 0
    end = -1
    for letra in tema[0:-4]:
        end += 1
        if letra == "➪":
            ini = end
    return tema[ini + 2 : end]


### eof: loaders
### bof: functions


def write_ypoema(LOGO_TEXT, LOGO_IMAGE):  # ver save_img.py
    if LOGO_IMAGE == None:
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


def talk(text):  # text to speech( in session_state.lang )
    text = text.replace("<br>", "\n")
    text = text.replace("< br>", "")
    text = text.replace("<br >", "")

    tts = gTTS(text=text, lang=st.session_state.lang, slow=False)
    nany_file = random.randint(1, 20000000)
    file_name = os.path.join("./temp/" + "audio" + str(nany_file) + ".mp3")
    tts.save(file_name)
    audio_file = open(file_name, "rb")
    audio_byts = audio_file.read()
    st.audio(audio_byts, format="audio/ogg")
    audio_file.close()
    os.remove(file_name)


def show_video(pagina):  # vídeo-tutorial da página
    st.sidebar.info(load_md_file("INFO_VYDE.md"))
    video_name = os.path.join("./base/" + "video_" + pagina + ".webm")
    video_file = open(video_name, "rb")
    video_byts = video_file.read()
    st.video(video_byts, format="webm")
    video_file.close()


def say_number(tema):  # search index title for eureka
    analise = "nonono"
    indexes = load_index()
    for line in indexes:
        if line.startswith(tema):
            string = line.strip("\n")
            part_string = string.partition(' : ')
            analise = part_string[2]
            break
            
    if st.session_state.lang != "pt" and analise != "nonono":
        if st.session_state.lang == "en":  # change to english number notation
            analise = analise.replace(".", ",")
        elif st.session_state.lang == "de":  # change to german number notation
            analise = analise.replace(".", " ")
    return analise


def translate(input_text):
    if st.session_state.lang == "pt":  # don't need translations here
        return input_text

    if not internet:
        st.session_state.lang = "pt"  # if no Internet then...
        return input_text

    try:
        output_text = GoogleTranslator(
            source="pt", target=st.session_state.lang
        ).translate(text=input_text)
    
        output_text = output_text.replace("<br>>", "<br>")
        output_text = output_text.replace("< br>", "<br>")
        output_text = output_text.replace("<br >", "<br>")
        output_text = output_text.replace("<br ", "<br>")
        output_text = output_text.replace(" br>", "<br>")
        return output_text
    except:
        return translate("Arquivo muito grande para ser traduzido.")


### eof: functions
### bof: pages


if st.session_state.visy:  # check visitor once
    update_visy()

    temas_list = load_temas("temas_mini")
    maxy = len(temas_list) - 1
    st.session_state.take = random.randrange(0, maxy, 1)
    temas_list = load_temas("todos os temas")
    maxy = len(temas_list) - 1
    st.session_state.mini = random.randrange(0, maxy, 1)

    st.success('bem vindo à **máquina de fazer Poesia...**')
    st.session_state.visy = False


def main():
    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="mini",    description=""),
        stx.TabBarItemData(id=2, title="yPoemas", description=""),
        stx.TabBarItemData(id=3, title="eureka",  description=""),
        stx.TabBarItemData(id=4, title="off-machina", description=""),
        stx.TabBarItemData(id=5, title="books",   description=""),
        stx.TabBarItemData(id=6, title="poly",    description=""),
        stx.TabBarItemData(id=7, title="about",   description=""),
    ], default=1)
    
    pick_lang()
    pick_draw()

    if chosen_id == '1':
        st.sidebar.info(load_md_file("INFO_MINI.md"))
        st.sidebar.info(load_md_file("INFO_BEST.md"))
        page_mini()
    elif chosen_id == '2':
        st.sidebar.info(load_md_file("INFO_YPOEMAS.md"))
        page_ypoemas()
    elif chosen_id == '3':
        st.sidebar.info(load_md_file("INFO_EUREKA.md"))
        page_eureka()
    elif chosen_id == '4':
        st.sidebar.info(load_md_file("INFO_OFF-MACHINA.md"))
        page_off_machina()
    elif chosen_id == '5':
        st.sidebar.info(load_md_file("INFO_BOOKS.md"))
        page_books()
    elif chosen_id == '6':
        st.sidebar.info(load_md_file("INFO_POLY.md"))
        page_polys()
    elif chosen_id == '7':
        st.sidebar.info(load_md_file("INFO_ABOUT.md"))
        page_abouts()

    show_icons()
    st.sidebar.state = True


st.session_state.last_lang = st.session_state.lang
def page_mini():
    temas_list = load_temas("temas_mini")
    maxy = len(temas_list) - 1
    if st.session_state.mini > maxy:  # just in case
        st.session_state.mini = 0

    foo1, more, rand, foo2 = st.columns([4, 1, 1, 4])

    help_me = load_help(st.session_state.lang)
    help_rand = help_me[1]
    help_more = help_me[4]
    rand = rand.button("✻", help=help_rand)
    
    if rand:
        st.session_state.mini = random.randrange(0, maxy, 1)
    
    st.session_state.tema = temas_list[st.session_state.mini]
    analise = say_number(st.session_state.tema)
    more = more.button("✚", help=help_more+' • '+analise)

    lnew = True
    if st.session_state.vide:
        lnew = False
        show_video("mini")
        update_readings("video_mini")
        st.session_state.vide = False

    if lnew:
        mini_expander = st.expander("", expanded=True)
        with mini_expander:
                
            if st.session_state.lang != st.session_state.last_lang:
                curr_ypoema = load_lypo()  # changes in lang, keep LYPO
            else:
                curr_ypoema = load_poema(st.session_state.tema, "")
                curr_ypoema = load_lypo()
            
            if st.session_state.lang != "pt":  # translate if idioma <> pt
                curr_ypoema = translate(curr_ypoema)
                typo_user = "TYPO_" + IPAddres
                with open(
                    os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
                ) as save_typo:
                    save_typo.write(curr_ypoema)
                    save_typo.close()
                curr_ypoema = load_typo()  # to normalize line breaks in text
            
            update_readings(st.session_state.tema)
            LOGO_TEXT = curr_ypoema
            LOGO_IMAGE = None
            
            if st.session_state.draw:
                LOGO_IMAGE = load_arts(st.session_state.tema)
            
            write_ypoema(LOGO_TEXT, LOGO_IMAGE)
            
            if st.session_state.talk:
                talk(curr_ypoema)


def page_ypoemas():
    temas_list = load_temas(st.session_state.book)
    maxy = len(temas_list) - 1
    if st.session_state.take > maxy or st.session_state.take < 0:  # just in case
        st.session_state.take = random.randrange(0, maxy, 1)

    foo1, more, last, rand, nest, manu, foo2 = st.columns(
        [3, 1, 1, 1, 1, 1, 3]
    )
    
    help_me = load_help(st.session_state.lang)
    help_last = help_me[0]
    help_rand = help_me[1]
    help_nest = help_me[2]
    help_more = help_me[4]

    more = more.button("✚", help=help_more)
    last = last.button("◀", help=help_last)
    rand = rand.button("✻", help=help_rand)
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
        "↓  lista de temas",
        options,
        index=st.session_state.take,
        format_func=lambda z: temas_list[z],
        key="opt_take",
    )

    if opt_take != st.session_state.take:
        st.session_state.take = opt_take

    st.session_state.tema = temas_list[st.session_state.take]
    analise = say_number(st.session_state.tema)
    manu = manu.button("?", help=analise)

    lnew = True
    if manu:
        lnew = False
        st.subheader(load_md_file("MANUAL_YPOEMAS.md"))

        LOGO_TEXT = load_info(st.session_state.tema)
        if st.session_state.lang != "pt":  # translate if idioma <> pt
            LOGO_TEXT = translate(LOGO_TEXT)
            
        LOGO_IMAGE = "./images/matrix/" + st.session_state.tema.capitalize() + ".jpg"
        write_ypoema(LOGO_TEXT, LOGO_IMAGE)

    if st.session_state.vide:
        lnew = False
        show_video("ypoemas")
        update_readings("video_ypoemas")
        st.session_state.vide = False

    if lnew:
        what_book = (
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

        ypoemas_expander = st.expander(what_book, expanded=True)
        with ypoemas_expander:
            if st.session_state.lang != st.session_state.last_lang:
                curr_ypoema = load_lypo()  # changes in lang, keep LYPO
            else:
                curr_ypoema = load_poema(st.session_state.tema, "")
                curr_ypoema = load_lypo()

            if st.session_state.lang != "pt":  # translate if idioma <> pt
                curr_ypoema = translate(curr_ypoema)
                typo_user = "TYPO_" + IPAddres
                with open(
                    os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
                ) as save_typo:
                    save_typo.write(curr_ypoema)
                    save_typo.close()
                curr_ypoema = load_typo()  # to normalize line breaks in text

            update_readings(st.session_state.tema)
            LOGO_TEXT = curr_ypoema
            LOGO_IMAGE = None
            if st.session_state.draw:
                LOGO_IMAGE = load_arts(st.session_state.tema)

            write_ypoema(LOGO_TEXT, LOGO_IMAGE)
            
        if st.session_state.talk:
            talk(curr_ypoema)

        # st.markdown(get_binary_file_downloader_html('./temp/'+"LYPO_" + IPAddres, '➪ '+st.session_state.tema), unsafe_allow_html=True)


def page_eureka():
    help_me = load_help(st.session_state.lang)
    help_rand = help_me[1]
    help_more = help_me[4]

    seed, more, rand, aide, occurrences = st.columns([2.5, 1.5, 1.5, 0.7, 4])

    with seed:
        find_what = st.text_input(
            label=translate("digite algo para buscar..."),
            value=st.session_state.find_word,
        )

    with more:
        more = more.button("✚", help=help_more)

    with rand:
        rand = rand.button("✻", help=help_rand)
            
    if len(find_what) < 3:
        st.warning("digite pelo menos 3 letras...")
    else:
        seed_list = []
        eureka_list = load_eureka(find_what)
        for line in eureka_list:
            palas_fonte = line.strip("\n")
            part_string = palas_fonte.partition(' : ')
            palas = part_string[0]
            fonte = part_string[2]
            if palas is None or fonte is None:
                continue
            else:
                seed_list.append(palas + " ➪ " + fonte)

        if len(seed_list) > 0:
            seed_list.sort()
            st.session_state.find_word = find_what
            if len(seed_list) == 1:
                info_find = translate("ocorrência")
            else:
                info_find = translate("ocorrências")

            info_find += ' de "' + find_what + '"'

            if rand:
                st.session_state.eureka = random.randrange(0, len(seed_list)-1, 1)
                this_seed = seed_list[st.session_state.eureka]
                seed_tema = get_seed_tema(seed_list[st.session_state.eureka])

            with occurrences:
                options = list(range(len(seed_list)))
                opt_ocur = st.selectbox(
                    '↓  ' + str(len(seed_list)) + " " + info_find,
                    options,
                    index=st.session_state.eureka,
                    format_func=lambda y: seed_list[y],
                    key="opt_ocur",
                )

            st.session_state.eureka = opt_ocur
            this_seed = seed_list[st.session_state.eureka]
            seed_tema = get_seed_tema(seed_list[st.session_state.eureka])
            st.session_state.tema = seed_tema
            analise = say_number(seed_tema)

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

            lnew = True
            if st.session_state.vide:
                lnew = False
                show_video("eureka")
                update_readings("video_eureka")
                st.session_state.vide = False

            if lnew:
                if aide:
                    st.markdown(analise, unsafe_allow_html=True)
                    st.subheader(load_md_file("MANUAL_EUREKA.md"))
                else:
                    eureka_expander = st.expander("", expanded=True)
                    with eureka_expander:
                        LOGO_TEXT = curr_ypoema
                        LOGO_IMAGE = None
                        if st.session_state.draw:
                            LOGO_IMAGE = load_arts(seed_tema)

                        write_ypoema(LOGO_TEXT, LOGO_IMAGE)
                        update_readings(seed_tema)

                    if st.session_state.talk:
                        talk(curr_ypoema)
        else:
            st.warning("nenhum verbete encontrado com essas letras ---> " + find_what)


def page_off_machina():  # available off_machina_books
    off_books_list = load_all_offs()
    options = list(range(len(off_books_list)))
    opt_off_book = st.selectbox(
        "↓  lista de livros",
        options,
        index=st.session_state.off_book,
        format_func=lambda x: off_books_list[x],
        # help="books",
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
    rand = rand.button("✻", help=help_rand)
    nest = nest.button("▶", help=help_nest)
    love = love.button("❤", help=help_love)
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
        "↓  lista de títulos",
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
        st.subheader(load_md_file("MANUAL_OFF-MACHINA.md"))

    if love:
        lnew = False
        list_readings()
        st.markdown(
            get_binary_file_downloader_html("./temp/read_list.txt", "views"),
            unsafe_allow_html=True,
        )

    if st.session_state.vide:
        lnew = False
        show_video("off-machina")
        update_readings("video_off-machina")
        st.session_state.vide = False

    if lnew:
        what_book = (
            "⚫  "
            + st.session_state.lang
            + " ( "
            + str(st.session_state.off_take + 1)
            + "/"
            + str(len(off_book_pagys))
            + " )"
        )

        off_machina_expander = st.expander(what_book, True)
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
                    if off_book_name == "livro_vivo":
                        LOGO_CAPA = load_arts("livro_vivo")
                        st.image(LOGO_CAPA, use_column_width=True)
                    else:
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

                LOGO_TEXT = off_book_text
                LOGO_IMAGE = None
                if st.session_state.draw:
                    LOGO_IMAGE = load_arts(off_book_name)

                write_ypoema(LOGO_TEXT, LOGO_IMAGE)
                update_readings(off_book_name)

        if st.session_state.talk:
            talk(off_book_text)


def page_books():  # available books
    bb, ok = st.columns([9.3, 0.7])
    with bb:
        books_list = [
            "livro vivo",
            "poemas",
            "jocosos",
            "ensaios",
            "variações",
            "metalinguagem",
            "todos os temas",
            "outros autores",
            "signos_fem",
            "signos_mas",
            "todos os signos",
        ]

        options = list(range(len(books_list)))
        opt_book = st.selectbox(
            "↓  lista de livros",
            options,
            index=books_list.index(st.session_state.book),
            format_func=lambda x: books_list[x],
            key="opt_book",
        )

        with ok:
            doit = st.button("✔", help="confirm ?")

        lnew = True
        if st.session_state.vide:
            lnew = False
            show_video("books")
            update_readings("video_books")
            st.session_state.vide = False
    
        if lnew:
            list_book = ""
            temas_list = load_temas(books_list[opt_book])
            for line in temas_list:
                list_book += line.strip() + ", "
            st.write(list_book[:-2])

            books_expander = st.expander("", True)
            with books_expander:
                st.subheader(load_md_file("MANUAL_BOOKS.md"))
        
                if doit:
                    st.session_state.take = 0
                    st.session_state.book = books_list[opt_book]
                    return None


def page_polys():  # available languages
    pp, ok = st.columns([9.3, 0.7])
    with pp:
        poly_list = []
        poly_pais = []
        poly_ling = []
        with open(
            os.path.join("./base/" + st.session_state.poly_file), encoding="utf-8"
        ) as poly:
            for line in poly:
                poly_list.append(line)
                string = line.strip("\n")
                part_string = string.partition(' : ')
                poly_pais.append(translate(part_string[0]))
                poly_ling.append(part_string[2])
        poly.close()

        options = list(range(len(poly_list)))
        opt_poly = st.selectbox(
            '↓  lista: ' + str(len(poly_list)) + " idiomas",
            options,
            index=st.session_state.poly_take,
            format_func=lambda x: poly_list[x],
            key="opt_poly",
        )

    with ok:
        doit = st.button("✔", help="confirm ?")

    lnew = True
    if st.session_state.vide:
        lnew = False
        show_video("poly")
        update_readings("video_poly")
        st.session_state.vide = False
    
    if doit:
        poly_pais = poly_pais[opt_poly]
        poly_ling = poly_ling[opt_poly]
        st.session_state.poly_name = translate(poly_pais)
        st.session_state.poly_lang = poly_ling
        st.session_state.poly_take = opt_poly

        st.session_state.last_lang = st.session_state.lang
        st.session_state.lang = st.session_state.poly_lang
        
    if lnew:
        poly_expander = st.expander("", True)
        with poly_expander:
            st.subheader(load_md_file("MANUAL_POLY.md"))
        

def page_abouts():
    abouts_list = [
        "comments",
        "prefácio",
        "machina",
        "off-machina",
        "outros",
        "traduttore",
        "bibliografia",
        "imagens",
        "samizdát",
        "pensares",
        "notes",
        "license",
        "index",
    ]

    options = list(range(len(abouts_list)))
    opt_abouts = st.selectbox(
        "↓  sobre...",
        options,
        format_func=lambda x: abouts_list[x],
        key="opt_abouts",
    )

    lnew = True
    if st.session_state.vide:
        lnew = False
        show_video("about")
        update_readings("video_about")
        st.session_state.vide = False

    if lnew:
        choice = abouts_list[opt_abouts].upper()
        about_expander = st.expander("", True)
        with about_expander:
            if choice == 'MACHINA':
                st.subheader(load_md_file("ABOUT_MACHINA_A.md"))
                LOGO_TEXT = load_info(st.session_state.tema)
                LOGO_IMAGE = "./images/matrix/" + st.session_state.tema + ".jpg"
                write_ypoema(LOGO_TEXT, LOGO_IMAGE)
                st.subheader(load_md_file("ABOUT_MACHINA_D.md"))
            else:
                st.subheader(load_md_file("ABOUT_" + choice + ".md"))

### eof: pages

if __name__ == "__main__":
    main()
