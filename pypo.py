
import os
import streamlit as st
from deep_translator import GoogleTranslator

# --- 1. CPC: LISTA OFICIAL DE 21 IDIOMAS ---
IDIOMAS_OFICIAIS = {
    "Português": "pt", "Espanhol": "es", "Italiano": "it", "Francês": "fr",
    "Inglês": "en", "Catalão": "ca", "Córsico": "co", "Galego": "gl",
    "Basco": "eu", "Esperanto": "eo", "Latin": "la", "Galês": "cy",
    "Sueco": "sv", "Polonês": "pl", "Holandês": "nl", "Norueguês": "no",
    "Finlandês": "fi", "Dinamarquês": "da", "Irlandês": "ga", "Romeno": "ro", "Russo": "ru"
}

# --- 2. EXORCISMO E SEGURANÇA (Mata o KeyError definitivamente) ---
def init_session():
    """ Garante a existência das chaves antes de qualquer renderização """
    if "lang" not in st.session_state:
        st.session_state["lang"] = "pt"
    if "last_lang" not in st.session_state:
        st.session_state["last_lang"] = "pt"

def translate(text):
    """ 
    Usa .get() para evitar KeyError caso o Streamlit tente traduzir 
    algo antes da inicialização completa do estado. 
    """
    lang_atual = st.session_state.get("lang", "pt")
    if lang_atual == "pt": 
        return text
    try:
        return GoogleTranslator(source='pt', target=lang_atual).translate(text)
    except: 
        return text

# --- 3. COMPONENTES DE INTERFACE ---
def language_selector():
    """ Dropdown única no topo - Comando Central de Idiomas """
    lang_inv = {v: k for k, v in IDIOMAS_OFICIAIS.items()}
    lista_nomes = sorted(list(IDIOMAS_OFICIAIS.keys()))
    
    # Garante que o idioma atual seja o primeiro da lista visual
    nome_atual = lang_inv.get(st.session_state.get("lang", "pt"), "Português")
    if nome_atual in lista_nomes:
        lista_nomes.insert(0, lista_nomes.pop(lista_nomes.index(nome_atual)))

    selecionado = st.selectbox("↓ " + translate("idioma"), lista_nomes, key="cpc_main_selector")
    novo_code = IDIOMAS_OFICIAIS[selecionado]

    if novo_code != st.session_state.get("lang"):
        st.session_state["lang"] = novo_code
        st.rerun()

def render_poema_style(texto):
    """ Estética 20px - IBM Plex Sans """
    st.markdown(f"""
    <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 20px; line-height: 1.6; color: #333; padding: 15px;">
        {texto.replace('|', '<br>')}
    </div>
    """, unsafe_allow_html=True)

# --- 4. PÁGINAS INTEGRAIS ---
def page_eureka():
    st.subheader("Eureka")
    render_poema_style(translate("A arquitetura do acaso | não admite reformas."))

def page_livros():
    """ Item 5 do CPC: Oficialmente 'Livros' """
    st.subheader(translate("Livros"))
    st.info(translate("Nenhum livro aberto no momento."))

def page_off_machina():
    st.subheader("Off-Machina")
    render_poema_style(translate("O verso livre | é o prisioneiro | da própria liberdade."))

# --- 5. MAIN (ORQUESTRAÇÃO SEM FALHAS) ---
def main():
    # A ORDEM ABAIXO É OBRIGATÓRIA PELO CPC
    init_session() # 1. Cria as variáveis na memória
    
    # 2. Configurações de UI
    st.set_page_config(page_title="Machina", layout="centered")

    with st.sidebar:
        language_selector() # 3. Seletor no topo
        st.write("---")
        
        # 4. Menu Traduzido (Só funciona porque o init_session rodou antes)
        opcoes = {
            translate("Início"): "inicio",
            "Eureka": "eureka",
            translate("Livros"): "livros",
            "Off-Machina": "off"
        }
        escolha_traduzida = st.radio("Menu", list(opcoes.keys()))
        escolha = opcoes[escolha_traduzida]

    # 5. Roteamento
    if escolha == "eureka":
        page_eureka()
    elif escolha == "livros":
        page_livros()
    elif escolha == "off":
        page_off_machina()
    else:
        st.title("Machina")
        render_poema_style(translate("Bem-vindo ao mar de poesia."))

if __name__ == "__main__":
    main()
