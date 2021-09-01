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

OVNY == anOther Visitor iN Ypoemas
VISY == New Visitor
NANY_VISY == Number of Visitors
LYPO == Last YPOema created from curr_ypoema
TYPO == Translated Ypoema from LYPO
POLY == Poliglot Idiom == Changed on Catalán
user_ip == the User IP for LYPO, TYPO

https://gonative.io/share/rbqdod
https://www.buymeacoffee.com/yPoemas
https://share.streamlit.io/nandoulopes/ypoemas/main/ypo.py
https://www.facebook.com/fernando.lopes.942/posts/3797156397062571?comment_id=3797297573715120&notif_id=1626293136581310&notif_t=feed_comment&ref=notif
https://youtu.be/SxtA5SM1hUw

"""

import os
import io
import re
import time
import random
import streamlit as st

from deep_translator import GoogleTranslator

# for ovny's
import pytz
from datetime import datetime

def utcnow():  # Coordinated Universal Time (UTC)
    return datetime.now(tz=pytz.utc)

def utcnew():  # Local Time
    tznow = str(datetime.now().astimezone())
    return tznow[-6:]

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


hostname = socket.gethostname()
user_ip = socket.gethostbyname(hostname)


# hide Streamlit Menu
# MainMenu {visibility: hidden;}
st.markdown(
    """ <style>
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
        width: 304px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 304px;
        margin-left: -500px;
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

if "ache" not in st.session_state:
    st.session_state.ache = "mar"


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
    page = st.sidebar.selectbox("Menu",tuple(pages.keys()))
    pages[page]()

    st.sidebar.info(load_file("INFO_"+page.upper()+".md"))
    st.sidebar.image("./images/img_coffee.jpg")
    st.sidebar.markdown("[email](mailto:lopes.fernando@hotmail.com) [face](https://www.facebook.com/nandoulopes) [coffee](https://www.buymeacoffee.com/yPoemas) [insta](https://www.instagram.com/fernando.lopes.942/) [whatsap-pix](https://api.whatsapp.com/send?phone=+5512991368181)")
    st.sidebar.state = True


def update_ovny():  # count one more ovny
    ovny_data = utcnow().isoformat()
    date_time = ovny_data[0:16]
    with open(os.path.join("./temp/ovny_data.txt"), "a", encoding="utf-8") as data:
        data.write(date_time + " " + utcnew() + "\n")
    data.close()


def load_ovny():  # days, zone, full
    days = 0
    ini_day = "2001-01-01"
    this_list = []
    with open(os.path.join("./temp/ovny_data.txt"), "r", encoding="utf-8") as data:
        for line in data:
            days = days+1
            cur_day = line[0:10]  # time = line[11:16] zone = line[17:23]
            if cur_day != ini_day and cur_day != "":
                this_list.append(ini_day+" - "+str(days))
                days = 0
                ini_day = cur_day
        this_list.append(ini_day+" - "+str(days))
    return this_list


def load_hour():  # hours
    hour = 0
    ini_hhh = "00"
    this_list = []
    with open(os.path.join("./temp/ovny_data.txt"), "r", encoding="utf-8") as data:
        for line in data:
            hour = hour+1
            cur_hhh = line[11:13]
            if cur_hhh != ini_hhh and cur_hhh != "":
                this_list.append(ini_hhh+" - "+str(hour))
                hour = 0
                ini_hhh = cur_hhh
        this_list.append(ini_hhh+" - "+str(hour))
    return this_list


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
    update_ovny()
    # st.session_state.visy = False


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


def save_readings(this_read):
    with open(os.path.join("./temp/read_list.txt"), "w", encoding="utf-8") as new_reader:
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
    soma_one = 0
    soma_zod = 0
    soma_hhh = 0
    read_day = []  # days
    read_zod = []  # zodiac
    tag_text = ""
    readings = load_readings()
    for line in readings:
        pipe_line = line.split("|")
        name = pipe_line[1]
        qtds = pipe_line[2]
        
        soma_hhh += int(qtds)
        if not "=" in line:
            soma_one += int(qtds)
        else:
            soma_zod += int(qtds)

        if qtds != "0":
            new_line = str(qtds) + " - " + name + "\n"
            if not "=" in line:
                read_day.append(new_line)
                tag_text += name + " "
            else:
                read_zod.append(new_line)

    read_day.sort(key=natural_keys, reverse=True)
    read_zod.sort(key=natural_keys, reverse=True)

    options = list(range(len(read_day)))
    opt_readings = st.selectbox(
        str(len(read_day)) + " temas, " + str(soma_one) + " leituras por " + str(st.session_state.nany_visy) + " visitantes",
        options,
        format_func=lambda x: read_day[x],
        key="opt_readings",
    )

    # tag_cloud(tag_text)

    options = list(range(len(read_zod)))
    zod_readings = st.selectbox(
        str(len(read_zod)) + " signos, " + str(soma_zod) + " leituras ( de " + str(soma_zod+soma_one)+" )",
        options,
        format_func=lambda x: read_zod[x],
        key="zod_readings",
    )

    visitors = []
    tot_days = 0
    ovny_list = load_ovny()
    for line in ovny_list:
        date = line[0:10]
        days = int(line[13:len(line)])
        if int(days) > 0:
            visitors.append(line)
            tot_days += days
    visitors.pop(0)  # because ini_day = "2001-01-01"

    options = list(range(len(visitors)))
    opt_visitors = st.selectbox(
        str(tot_days) + " visitas em " + str(len(visitors)) + " dias",
        options,
        format_func=lambda x: visitors[x],
        key="opt_visitors",
        )

    read_hhh = load_hour()
    read_hhh.sort(key=natural_keys, reverse=False)

    by_hours = []
    tmp_hour = 0
    tot_hour = 0
    ini_hour = "00"
    for line in read_hhh:
        line = line.strip("\n")
        hour = int(line[0:2])
        if hour == 2:
            hour = 23
        elif hour == 1:
            hour = 22
        elif hour == 0:
            hour = 21
        else:
            hour -= 3  #  UTC -3 for Brasil
        hour = str(hour).zfill(2)
        
        qtds = int(line[4:len(line)])
        tot_hour += qtds
        if hour == ini_hour:
            tmp_hour += qtds
        else:
            by_hours.append(str(tmp_hour)+" - "+ini_hour+" h")
            ini_hour = hour
            tmp_hour = qtds

    by_hours.sort(key=natural_keys, reverse=True)
    options = list(range(len(by_hours)))
    opt_by_hours = st.selectbox(
        str(tot_hour) + " visitas em " + str(len(by_hours)+1) + " horários",
        options,
        format_func=lambda x: by_hours[x],
        key="opt_by_hours",
        )
# eof: update themes readings


# bof: loaders
@st.cache(allow_output_mutation=True)
def load_file(file):  # Open files for about's
    try:
        with open(os.path.join("./md_files/" + file), encoding="utf-8") as f:
            file_text = f.read()

        if file != "index.md":  # don't want to translate original titles
            if not ".rol" in file:
                file_text = translate(file_text)
    except:
        file_text = "ooops... arquivo ( " + file + " ) não pode ser aberto. Sorry."
        st.session_state.lang = "pt"
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
def load_temas(book):  # List of yPoemas themes inside a Book
    all_temas_list = []
    full_name = os.path.join("./data/", book) + ".rol"
    with open(full_name, encoding="utf-8") as file:
        for line in file:
            all_temas_list.append(line.strip("\n"))
    return all_temas_list


@st.cache(allow_output_mutation=True)
def load_index():  # Load indexes numbers for all themes
    index_list = []
    with open(os.path.join("./data/index.txt"), encoding="utf-8") as lista:
        for line in lista:
            index_list.append(line)
    return index_list


def load_lypo():  # load last yPoema & replace "\n" with "<br>" for translator returned text
    lypo_text = ""
    lypo_user = "LYPO_" + user_ip
    with open(os.path.join("./temp/" + lypo_user), encoding="utf-8") as script:
        for line in script:
            line = line.strip()
            lypo_text += line + "<br>"
    return lypo_text


def load_typo():  # load translated yPoema & clean translator returned text
    typo_text = ""
    typo_user = "TYPO_" + user_ip
    with open(os.path.join("./temp/" + typo_user), encoding="utf-8") as script:
        for line in script:  # just 1 line
            line = line.strip()
            line = line.replace("< br>", "<br>")
            line = line.replace("<br >", "<br>")
            line = line.replace("<br ", "<br>")
            line = line.replace(" br>", "<br>")
            typo_text += line + "<br>"
    return typo_text


@st.cache(allow_output_mutation=True)
def load_all_offs():  # List off_themes
    all_books_off = []
    for file in os.listdir("./off_machina/"):
        this = file.lower()
        if this.endswith(".Pip"):
            this = this.replace(".Pip","")
            all_books_off.append(this)
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
    

def load_poema(
    nome_tema, seed_eureka
):  # generate new yPoema & save a copy of last generated in LYPO
    script = gera_poema(nome_tema, seed_eureka)
    novo_ypoema = ""
    lypo_user = "LYPO_" + user_ip

    with open(os.path.join("./temp/" + lypo_user), "w", encoding="utf-8") as save_lypo:
        save_lypo.write("**"+nome_tema+"**")  # include title of yPoema in first line for translations
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
def say_numeros(tema):  # search index title for eureka
    analise = "#️ nonono"
    indexes = load_index()
    this = next(i for i in indexes if i.startswith(tema))
    if this is not None:
        analise = "#️ " + this
    return analise


def translate(input_text):
    if st.session_state.lang == "pt":  # no need
        return input_text
        
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
    lexico_list = load_lexico()
    lnew = True

    with eureka_expander:
        bb, hh = st.beta_columns([9.3,.7])
        with bb:
            st.session_state.ache = st.text_input(label="digite uma palavra (ou parte dela) para buscar...")
    
        with hh:
            aide = st.button("?", help="help !!!")
    
        if aide:
            lnew = False
            st.session_state.ache = ""
            st.subheader(load_file("MANUAL_EUREKA.md"))

        if lnew and len(st.session_state.ache) > 2:
            seeds_list = []
            words_list = []
            temas_list = []
            for line in lexico_list:
                pipe_line = line.split("|")
                palas = pipe_line[1]
                fonte = pipe_line[2]
                if st.session_state.ache.lower() in palas.lower():
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
                        key="opt_tema",
                    )
            
                with vv:
                    options = list(range(len(words_list)))
                    opt_word = st.selectbox(
                        str(len(words_list)) + " verbetes",
                        options,
                        format_func=lambda x: words_list[x],
                        key="opt_word",
                    )
            
                with oo:
                    options = list(range(len(seeds_list)))
                    opt_seed = st.selectbox(
                        str(len(seeds_list)) + " ocorrências",
                        options,
                        help="use letras para filtrar a lista",
                        format_func=lambda x: seeds_list[x],
                        key="opt_seed",
                    )
            
                if opt_seed > len(seeds_list):  # just in case
                    opt_seed = 0
                    
                seed_tema = get_seed_tema(seeds_list[opt_seed])
            
                with btns:
                    more = st.button("+", help=say_numeros(seed_tema))
            
                curr_ypoema = load_poema(seed_tema, seeds_list[opt_seed])
                curr_ypoema = load_lypo()
                st.markdown(
                    curr_ypoema, unsafe_allow_html=True
                )  # finally... write it
                update_readings(seed_tema)
            else:
                st.warning("nenhum verbete encontrado com essas letras ---> " + st.session_state.ache)
        else:
            st.warning("digite pelo menos 3 letras...")


def page_polys():  # available languages
    st.write("")
    st.sidebar.image("./images/img_poly.jpg")
    poly_expander = st.beta_expander("", True)
    with poly_expander:
        pp, ok = st.beta_columns([9.3,.7])
        with pp:
            poly_list = []
            poly_show = []
            with open(os.path.join("./data/"+st.session_state.poly_file), encoding="utf-8") as poly:
                for line in poly:
                    poly_list.append(line)
                    pipe_line = line.split("|")
                    poly_show.append(pipe_line[1]+" : "+pipe_line[2])
            poly.close()
            
            if len(poly_list) > 0:
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
        bb, ok = st.beta_columns([9.3,.7])
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
                list_book += line.strip()+", "
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
        "prefácio",
        "machina",
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
        st.subheader(load_file("ABOUT_"+abouts_list[opt_abouts].upper() + ".md"))


st.session_state.last_lang = st.session_state.lang
def page_off_machina():  # available off_books
    st.write("")
    st.sidebar.image("./images/img_off_machina.jpg")

    off_books_list = load_all_offs()
    options = list(range(len(off_books_list)))
    opt_off_book = st.selectbox(
        "",
        options,
        index=st.session_state.off_book,
        format_func=lambda x: off_books_list[x],
        help = "books",
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

    if st.session_state.lang == "pt":
        h_last = "anterior"
        h_rand = "escolhe tema ao acaso"
        h_nest = "próximo"
        h_page = "selecione um título"
    else:
        h_last = translate("anterior")
        h_rand = translate("escolhe tema ao acaso")
        h_nest = translate("próximo")
        h_page = translate("selecione um título")

    c1, last, rand, nest, manu, c5 = st.beta_columns([3,1,1,1,1,3])
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
        help=h_page,
        key="opt_off_take",
    )
        
    lnew = True
    if manu:
        lnew = False
        st.subheader(load_file("MANUAL_OFF-MACHINA.md"))
        
    if lnew:
        info = (
            "⚫  " + st.session_state.lang
            + " ( "
            + str(st.session_state.off_take + 1)
            + "/"
            + str(len(off_book_pagys))
            + " )"
        )
        
        if opt_off_take != st.session_state.off_take:
            st.session_state.off_take = opt_off_take
            
        off_machina_expander = st.beta_expander(info, True)
        with off_machina_expander:
            off_book_text = ""
            pipe_line = this_off_book[st.session_state.off_take].split("|")
            if "@ " in pipe_line[1]:
                if st.session_state.lang != st.session_state.last_lang:
                    off_book_text = load_lypo()  # changes in lang, keep LYPO
                else:
                    nome_tema = pipe_line[1].replace("@ ", "")
                    off_book_text = load_poema(nome_tema, "" )  # no seed_eureka
                    off_book_text = "<br>"+load_lypo()
            else:
                pipe_line[1] = "**" + pipe_line[1] + "**"
                for text in pipe_line:
                    off_book_text += text + "<br>"
            
            capo = (st.session_state.off_take == 0)

            if capo:
                ii, cc = st.beta_columns([2.5,7.5])
                with ii:
                    st.image("./off_machina/capa_"+off_book_name+".jpg",use_column_width=True)
                with cc:
                    st.markdown(off_book_text, unsafe_allow_html=True)  # finally... write it
            else:
                if st.session_state.lang != "pt":  # translate if idioma <> pt == redundant but... ok
                    off_book_text = translate(off_book_text)
                st.markdown(off_book_text, unsafe_allow_html=True)  # finally... write it

        

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

    if st.session_state.lang == "pt":
        h_last = "anterior"
        h_rand = "escolhe tema ao acaso"
        h_nest = "próximo"
        h_love = "mais lidos..."
        h_numb = "nuvem de palavras"
        h_page = "selecione um yPoema"
    else:  # translate helper's
        h_last = translate("anterior")
        h_rand = translate("escolhe tema ao acaso")
        h_nest = translate("próximo")
        h_love = translate("mais lidos...")
        h_numb = translate("nuvem de palavras")
        h_page = translate("selecione um yPoema")

    last = last.button("◀", help=h_last)
    rand = rand.button("★", help=h_rand)
    nest = nest.button("▶", help=h_nest)
    love = love.button("❤", help=h_love)

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
        help=h_page,
        key="opt_take",
    )
    if opt_take != st.session_state.take:
        curr_tema = all_temas_list[st.session_state.take]
        st.session_state.take = opt_take

    curr_tema = all_temas_list[st.session_state.take]
    analise = say_numeros(curr_tema)
    numb = numb.button("☁", help=h_numb)
    # numb = numb.button("☁", help=analise)
    manu = manu.button("?", help="help !!!")

    lnew = True
    if love:
        lnew = False
        status_readings()

    if numb:
        lnew = False
        st.subheader(analise)
        tag_cloud("_ypo_")
        # st.markdown("[Vídeo_YouTube](https://www.youtube.com/watch?v=CTDj3BzsFxw)")
        # st.video("video.webm")
    
    if manu:
        lnew = False
        st.write(translate("✔ clique no link para ver o [**vídeo-tutorial**](https://youtu.be/SxtA5SM1hUw)"))
        st.subheader(load_file("MANUAL_YPOEMAS.md"))

    if lnew:
        info = (
            "⚫  " + st.session_state.lang
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
                typo_user = "TYPO_" + user_ip
                with open(
                    os.path.join("./temp/" + typo_user), "w", encoding="utf-8"
                ) as save_typo:
                    save_typo.write(curr_ypoema)
                    save_typo.close()
                curr_ypoema = load_typo()  # to normalize line breaks in text
                
            st.markdown(curr_ypoema, unsafe_allow_html=True)  # finally... write it
            update_readings(curr_tema)
# eof: pages


if __name__ == "__main__":
    main()
