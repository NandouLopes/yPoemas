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

VISY == New Visitor
NANY_VISY == Number of Visitors
LYPO == Last YPOema created from curr_ypoema
TYPO == Translated YPOema from LYPO
POLY == Poliglot Idiom == Changed on Catalán

keywords = "| what  | why    | when   | how  | where | which | who  | whose   |".split("|")
keywords = "| o que | porquê | quando | como | onde  | qual  | quem | de quem |"

https://share.streamlit.io/ == deploy

https://youtu.be/SxtA5SM1hUw == vídeo-tutorial
https://www.buymeacoffee.com/yPoemas
https://share.streamlit.io/nandoulopes/ypoemas/main/ypo.py
https://www.youtube.com/watch?v=CTDj3BzsFxw == vídeo machina Xailer
https://studio.youtube.com/channel/UCBzkwy5R3K3WS_i5wz_UwNQ
"""

import os
import io
import re
import time
import random
import base64
import datetime
import streamlit as st

try:
    from deep_translator import GoogleTranslator
except ImportError as ex:
    st.warning("Google Translator não conectado. Traduções não disponíveis no momento.")
    print(ex)

# Project Module
from lay_2_ypo import gera_poema

# TagCloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# user_id: to create LYPO and TYPO for each hostname
import socket

from gtts import gTTS

st.set_page_config(
    page_title='yPoemas - a "machina" de fazer Poesia',
    page_icon=":star:",
    layout="centered",
    initial_sidebar_state="auto",
)

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
        st.warning("Internet não conectada. Traduções não disponíveis no momento.")
        print(ex)
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
        width: 312px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 312px;
        margin-left: -320px;
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
    st.session_state.find_word = "mar"
if "word_type" not in st.session_state:
    st.session_state.word_type = "semente"


def main():
    pages = {
        "yPoemas": page_ypoemas,
        "eureka": page_eureka,
        "poly": page_polys,
        "books": page_books,
        "comments": page_comments,
        "about": page_abouts,
        "off-machina": page_off_machina,
    }
    page = st.sidebar.selectbox("Menu", tuple(pages.keys()))
    pages[page]()
    st.sidebar.info(load_file("INFO_" + page.upper() + ".md"))
    st.sidebar.markdown(
        "([email](mailto:lopes.fernando@hotmail.com) [face](https://www.facebook.com/nandoulopes) [coffee](https://www.buymeacoffee.com/yPoemas) [insta](https://www.instagram.com/fernando.lopes.942/)  [whatsapp pix](https://api.whatsapp.com/send?phone=+5512991368181))"
    )
    st.sidebar.image("./images/img_coffee.jpg")
    st.sidebar.state = True


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


# bof: update themes readings
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
            if not "=" in name:  # out zodiac
                tag_text += name + " "
            read_days.append(new_line)

    read_days.sort(key=natural_keys, reverse=True)

    currrent_day = datetime.date.today()
    begining_day = datetime.date(2021, 7, 6)
    total_viewes = st.session_state.nany_visy
    days_of_runs = begining_day - currrent_day
    days_of_runs = abs(days_of_runs.days)
    views_by_day = total_viewes/days_of_runs
    reads_by_day = (sum_all_days/views_by_day)/days_of_runs

    options = list(range(len(read_days)))
    opt_readings = st.selectbox(
        str(len(read_days))
        + " temas, "
        + str(sum_all_days)
        + " leituras por "
        + str(total_viewes)
        + " visitantes ( "
        + str(int(views_by_day)) + " dia / "
        + str(int(reads_by_day)) + " reads )",
        options,
        format_func=lambda x: read_days[x],
        key="opt_readings",
    )
    tag_cloud(tag_text)
# eof: update themes readings


# bof: loaders
@st.cache(allow_output_mutation=True)
def load_file(file):  # Open files for about's
    try:
        with open(os.path.join("./md_files/" + file), encoding="utf-8") as f:
            file_text = f.read()

        # if file != "about_index.md":  # don't want to translate original titles
        if not ".rol" in file:
            file_text = translate(file_text)
    except:
        file_text = "ooops... arquivo ( " + file + " ) não pode ser aberto. Sorry."
        st.session_state.lang = "pt"
    return file_text


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
    if idiom in "_pt_es__it_fr_en_de_ca":
        helpers = load_help_tips()
        for line in helpers:
            pipe_line = line.split("|")
            if pipe_line[1].startswith(idiom+"_"):
                text = pipe_line[2]
                returns.append(text)
    else:
        returns.append(translate("anterior"))
        returns.append(translate("escolhe tema ao acaso"))
        returns.append(translate("próximo"))
        returns.append(translate("mais lidos..."))
        returns.append(translate("ouvir o texto"))
    return(returns)
    

@st.cache(allow_output_mutation=True)
def load_eureka_semente(seed):  # Lexicon
    index_eureka = []
    with open(os.path.join("./base/lexico_pt.txt"), encoding="utf-8") as lista:
        for line in lista:
            pipe_line = line.split("|")
            palas = pipe_line[1]
            fonte = pipe_line[2]
            if seed.lower() in palas.lower():
                index_eureka.append(line)

    return index_eureka


@st.cache(allow_output_mutation=True)
def load_eureka_letras(seed):  # Lexicon
    index_eureka = []
    with open(os.path.join("./base/lexico_pt.txt"), encoding="utf-8") as lista:
        for line in lista:
            pipe_line = line.split("|")
            palas = pipe_line[1]
            fonte = pipe_line[2]
            exists = True
            for letra in seed.lower():
                if not letra in palas.lower():
                    exists = False
            if exists:
                index_eureka.append(line)

    return index_eureka


@st.cache(allow_output_mutation=True)
def load_temas(book):  # List of yPoemas themes inside a Book
    all_temas_list = []
    with open(os.path.join("./base/" + book + ".rol"), "r", encoding = "utf-8") as file:
        for line in file:
            all_temas_list.append(line.strip("\n"))
    return all_temas_list


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


# generate new yPoema & save a copy of last generated in LYPO
def load_poema(nome_tema, seed_eureka):
    script = gera_poema(nome_tema, seed_eureka)
    novo_ypoema = ""
    lypo_user = "LYPO_" + user_id

    with open(os.path.join("./temp/" + lypo_user), "w", encoding="utf-8") as save_lypo:
        save_lypo.write(
            "**" + nome_tema + "**"
        )  # include title of yPoema in first line for translations
        save_lypo.write("\n")
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
def talk(text):  # text to speech(text in session_state.lang)
    text = text.replace('**','')  # clear mark_down & fix line_feeds
    text = text.replace('<br>','\n')
    text = text.replace('< br>','')
    text = text.replace('<br >','')
    # try:
    tts = gTTS(text=text, lang=st.session_state.lang, slow=False)
    nany_file = random.randint(1, 20000000)
    file_name = "audio" + str(nany_file) + ".mp3"
    tts.save(file_name)
    audio_file = open(file_name, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/ogg')
    audio_file.close()
    os.remove(file_name)


def say_numeros(tema):  # search index title for eureka
    analise = "#️ nonono"
    indexes = load_index()
    this = None
    for line in indexes:
        if line.startswith(tema):
            this = line.strip("\n")
            break
    if this is not None:
        analise = "#️ " + this
        if st.session_state.lang == "en":
            analise = analise.replace(".",",")
        elif st.session_state.lang == "de":
            analise = analise.replace("."," ")
    return analise


@st.cache(allow_output_mutation=True)
def translate(input_text):
    if st.session_state.lang == "pt":  # no need
        return input_text

    if internet():
        try:
            output_text = GoogleTranslator(
                source="pt", target=st.session_state.lang
            ).translate(text=input_text)
        except IOError as exc:
            raise RuntimeError(
                "oops... Google Translator não está repondendo... Offline?"
            ) from exc

        output_text = output_text.replace("<br>>", "<br>")
        output_text = output_text.replace("< br>", "<br>")
        output_text = output_text.replace("<br >", "<br>")
        output_text = output_text.replace("<br ", "<br>")
        output_text = output_text.replace(" br>", "<br>")
        return output_text
    else:
        st.session_state.lang = "pt"
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


def get_poly_name(this_poly):  # extract language name for poly
    pipe_line = this_poly.split("|")
    st.session_state.poly_name = translate(pipe_line[1])
    st.session_state.poly_lang = pipe_line[2]
    return True
# eof: functions


# bof: pages
def page_eureka():
    st.write("")
    st.sidebar.image("./images/img_eureka.jpg")
    eureka_expander = st.beta_expander("", expanded=True)
    icone = "✴"
    if st.session_state.word_type == "letras":
        icone = "Ø"
    lnew = True

    with eureka_expander:
        bb, sp, sm, lt, hh = st.beta_columns([4.6,2.3,.7,.7,.7])
        with bb:
            seed = st.text_input(
                label="digite uma palavra (ou parte dela) para buscar...",
                value=st.session_state.find_word,
            )

        with sm:
            semente = st.button("✴", help="temas com essa sequência de letras")

        with lt:
            letras = st.button("Ø", help="temas contendo as letras digitadas")

        with hh:
            aide = st.button("?", help="modo de usar")
            
        if semente:
            st.session_state.word_type = "semente"
            icone = "✴"
            
        if letras:
            st.session_state.word_type = "letras"
            icone = "Ø"

        if aide:
            lnew = False
            st.subheader(load_file("MANUAL_EUREKA.md"))

        if lnew and len(seed) > 2:
            words_list = []
            temas_list = []
            seeds_list = []
            leter_list = []
            eurek_list = []

            if st.session_state.word_type == "semente":
                eurek_list = load_eureka_semente(seed)
            else:
                eurek_list = load_eureka_letras(seed)
            
            for line in eurek_list:
                pipe_line = line.split("|")
                palas = pipe_line[1]
                fonte = pipe_line[2]
                
                if palas is None or fonte is None:
                    continue
                else:
                    if st.session_state.word_type == "semente":
                        seeds_list.append(palas + " - " + fonte)
                    else:
                        leter_list.append(palas + " - " + fonte)
                        
                    this_tema = get_seed_tema(palas + " - " + fonte)
                    if not palas.lower() in words_list:
                        words_list.append(palas.lower())
                    if not this_tema in temas_list:
                        temas_list.append(this_tema)
                        
            if len(seeds_list) > 0 or len(leter_list) > 0:
                tt, vv, oo, btns = st.beta_columns([2.3, 2.7, 4, 0.8])
                seeds_list.sort()
                leter_list.sort()

                with tt:
                    # options = list(range( len(temas_list)))
                    opt_tema = st.selectbox(
                        str(len(temas_list)) + " temas",
                        list(range( len(temas_list))),
                        format_func=lambda w: temas_list[w],
                        key="opt_tema",
                    )

                with vv:
                    # options = list(range( len(words_list)))
                    opt_word = st.selectbox(
                        str(len(words_list)) + " verbetes",
                        list(range( len(words_list))),
                        format_func=lambda x: words_list[x],
                        key="opt_word",
                    )

                with oo:
                    if st.session_state.word_type == "semente":
                        opt_seed = st.selectbox(
                            "( " + icone + " ) " + str(len(seeds_list)) + " ocorrências",
                            list(range( len(seeds_list))),
                            format_func=lambda y: seeds_list[y],
                            key="opt_seed",
                        )
                    else:
                        opt_letr = st.selectbox(
                            "( " + icone + " ) " + str(len(leter_list)) + " ocorrências",
                            list(range( len(leter_list))),
                            format_func=lambda y: leter_list[y],
                            key="opt_letr",
                        )

                if st.session_state.word_type == "semente":
                    if (opt_seed < 0) or (opt_seed > len(seeds_list)):
                        opt_seed = 0
                    seed_tema = get_seed_tema(seeds_list[opt_seed])
                    this_seed = seeds_list[opt_seed]
                else:
                    if (opt_letr < 0) or (opt_letr > len(leter_list)):
                        opt_letr = 0
                    seed_tema = get_seed_tema(leter_list[opt_letr])
                    this_seed = leter_list[opt_letr]

                with btns:
                    more = st.button("+", help=say_numeros(seed_tema))

                curr_ypoema = load_poema(seed_tema, this_seed)
                curr_ypoema = load_lypo()
                st.markdown(curr_ypoema, unsafe_allow_html=True)  # finally... write it
                update_readings(seed_tema)
            else:
                st.warning(
                    "nenhum verbete encontrado com essas letras ---> "
                    + seed
                )
        else:
            st.warning("digite pelo menos 3 letras...")


def page_polys():  # available languages
    st.write("")
    st.sidebar.image("./images/img_poly.jpg")
    poly_expander = st.beta_expander("", True)
    with poly_expander:
        pp, ok = st.beta_columns([9.3, 0.7])
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
    st.write("")
    st.sidebar.image("./images/img_books.jpg")
    books_expander = st.beta_expander("", True)
    with books_expander:
        bb, ok = st.beta_columns([9.3, 0.7])
        with bb:
            books_list = [
                "livro vivo",
                "poemas",
                "jocosos",
                "ensaios",
                "variações",
                "metalingua",
                "outros autores",
                "signos_fem",
                "signos_mas",
                "todos os signos",
                "todos os temas",
            ]
            this = books_list.index(st.session_state.book)

            options = list(range(len(books_list)))
            opt_book = st.selectbox(
                "",
                options,
                index=this,
                format_func=lambda x: books_list[x],
                key="opt_book",
            )

            list_book = ""
            all_temas_list = load_temas(books_list[opt_book])
            for line in all_temas_list:
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
    st.write("")
    st.sidebar.image("./images/img_comments.jpg")
    comments_expander = st.beta_expander("", True)
    with comments_expander:
        st.subheader(load_file("MANUAL_COMMENTS.md"))


def page_abouts():
    st.write("")
    st.sidebar.image("./images/img_about.jpg")
    abouts_list = [
        "machina",
        "prefácio",
        "off-machina",
        "outros",
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

    about_expander = st.beta_expander("", True)
    with about_expander:
        st.subheader(load_file("ABOUT_" + abouts_list[opt_abouts].upper() + ".md"))


st.session_state.last_lang = st.session_state.lang


def page_off_machina():  # available off_books
    st.write("")
    st.sidebar.image("./images/img_off_machina.jpg")
    talk_text_button = st.sidebar.checkbox("☄", help=translate("clique para ouvir o texto"), key="ypoemas")
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

    i0, i1, i2, i3, i4, i5, i6, i7, i8 = st.beta_columns(
        [1.5, 1, 1, 1, 1, 1, 1, 1, 1.5]
    )
    i1 = i1.button("pt", help="Português")
    i2 = i2.button("es", help="Español")
    i3 = i3.button("it", help="Italiano")
    i4 = i4.button("fr", help="Français")
    i5 = i5.button("en", help="English")
    i6 = i6.button("de", help="Deutsche")
    i7 = i7.button("☀", help=st.session_state.poly_name)

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
        st.session_state.last_lang = st.session_state.lang
        st.session_state.lang = st.session_state.poly_lang

    help_me = load_help(st.session_state.lang)
    h_last = help_me[0]
    h_rand = help_me[1]
    h_nest = help_me[2]

    c1, last, rand, nest, manu, c5 = st.beta_columns([3, 1, 1, 1, 1, 3])
    last = last.button("◀", help=h_last)
    rand = rand.button("★", help=h_rand)
    nest = nest.button("▶", help=h_nest)
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

        off_machina_expander = st.beta_expander(info, True)
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
                pipe_line[1] = "**" + pipe_line[1] + "**"
                for text in pipe_line:
                    off_book_text += text + "<br>"

            capo = st.session_state.off_take == 0

            if capo:
                ii, cc = st.beta_columns([2.5, 7.5])
                with ii:
                    st.image(
                        "./off_machina/capa_" + off_book_name + ".jpg",
                        use_column_width=True,
                    )
                with cc:
                    st.markdown(
                        off_book_text, unsafe_allow_html=True
                    )  # finally... write it
            else:
                if (
                    st.session_state.lang != "pt"
                ):  # translate if idioma <> pt == redundant but... ok
                    off_book_text = translate(off_book_text)
                st.markdown(
                    off_book_text, unsafe_allow_html=True
                )  # finally... write it
            
        if talk_text_button:
            talk(off_book_text)


st.session_state.last_lang = st.session_state.lang
all_temas_list = load_temas(st.session_state.book)
maxy = len(all_temas_list) - 1
if st.session_state.take > maxy:  # just in case
    st.session_state.take = 0

if st.session_state.visy:  # random text at first entry
    st.session_state.take = random.randrange(0, maxy, 1)
    st.session_state.visy = False


def page_ypoemas():
    st.write("")
    st.sidebar.image("./images/img_home.jpg")
    talk_text_button = st.sidebar.checkbox("☄", help=translate("clique para ouvir o texto"), key="ypoemas")
    i0, i1, i2, i3, i4, i5, i6, i7, i8 = st.beta_columns(
        [1.5, 1, 1, 1, 1, 1, 1, 1, 1.5]
    )

    i1 = i1.button("pt", help="Português")
    i2 = i2.button("es", help="Español")
    i3 = i3.button("it", help="Italiano")
    i4 = i4.button("fr", help="Français")
    i5 = i5.button("en", help="English")
    i6 = i6.button("de", help="Deutsche")
    i7 = i7.button("☀", help=st.session_state.poly_name)

    lnew = True

    if i1:
        st.session_state.lang = "pt"
        st.session_state.poly_file = "poly_pt.txt"
    elif i2:
        st.session_state.lang = "es"
        st.session_state.poly_file = "poly_es.txt"
    elif i3:
        st.session_state.lang = "it"
        st.session_state.poly_file = "poly_it.txt"
    elif i4:
        st.session_state.lang = "fr"
        st.session_state.poly_file = "poly_fr.txt"
    elif i5:
        st.session_state.lang = "en"
        st.session_state.poly_file = "poly_en.txt"
    elif i6:
        st.session_state.lang = "de"
        st.session_state.poly_file = "poly_de.txt"
    elif i7:
        st.session_state.last_lang = st.session_state.lang
        st.session_state.lang = st.session_state.poly_lang
                
    b0, last, rand, nest, love, numb, manu, b1 = st.beta_columns(
        [2, 1, 1, 1, 1, 1, 1, 2]
    )

    help_me = load_help(st.session_state.lang)
    h_last = help_me[0]
    h_rand = help_me[1]
    h_nest = help_me[2]
    h_love = help_me[3]

    last = last.button("◀", help=h_last)
    rand = rand.button("★", help=h_rand)
    nest = nest.button("▶", help=h_nest)
    love = love.button("❤", help=h_love)

    if love:
        lnew = False
        status_readings()
        st.markdown(
            get_binary_file_downloader_html("./temp/read_list.txt", "views"),
            unsafe_allow_html=True,
        )

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

    options = list(range(len(all_temas_list)))
    opt_take = st.selectbox(
        "",
        options,
        index=st.session_state.take,
        format_func=lambda z: all_temas_list[z],
        key="opt_take",
    )

    if opt_take != st.session_state.take:
        st.session_state.take = opt_take

    curr_tema = all_temas_list[st.session_state.take]
    analise = say_numeros(curr_tema)
    numb = numb.button("☁", help=analise)
    manu = manu.button("?", help="help !!!")

    if numb:
        lnew = False
        st.subheader(analise)
        tag_cloud("_ypo_")

    if manu:
        lnew = False
        st.write( "✔ [**vídeo-tutorial**](https://youtu.be/SxtA5SM1hUw)" )
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
            + str(len(all_temas_list))
            + " )"
        )
        ypoemas_expander = st.beta_expander(info, expanded=True)
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

            st.markdown(curr_ypoema, unsafe_allow_html=True)  # finally... write it
            update_readings(curr_tema)
            
        if talk_text_button:
            talk(curr_ypoema)

        # st.markdown(get_binary_file_downloader_html('./temp/'+"LYPO_" + user_id, curr_tema), unsafe_allow_html=True)
# eof: pages


if __name__ == "__main__":
    main()
