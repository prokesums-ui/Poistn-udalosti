import streamlit as st

# --- ZÁKLADNÉ NASTAVENIE STRÁNKY ---
st.set_page_config(page_title="Poistné udalosti", page_icon="📋", layout="centered")

# --- KONTROLA KNIŽNÍC ---
try:
    import gspread
    from google.oauth2.service_account import Credentials
    KNIŽNICE_OK = True
except ImportError:
    KNIŽNICE_OK = False
    st.warning("⚠️ Chýbajú knižnice pre Google Tabuľky. Na GitHube vytvorte súbor requirements.txt s obsahom: streamlit, gspread, google-auth.")

# --- PAMÄŤ APLIKÁCIE (Inicializácia) ---
if 'strana' not in st.session_state:
    st.session_state.strana = 1

# Inicializujeme každú hodnotu priamo v session_state, aby sme na ne mohli viazať widgety cez parameter 'key'
if 'meno' not in st.session_state:
    st.session_state.meno = ''
if 'telefon' not in st.session_state:
    st.session_state.telefon = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'vozidlo' not in st.session_state:
    st.session_state.vozidlo = ''
if 'popis' not in st.session_state:
    st.session_state.popis = ''
if 'foto_nazov' not in st.session_state:
    st.session_state.foto_nazov = 'Žiadna'

def chod_dalej(): 
    st.session_state.strana += 1

def zacat_znova():
    st.session_state.strana = 1
    st.session_state.meno = ''
    st.session_state.telefon = ''
    st.session_state.email = ''
    st.session_state.vozidlo = ''
    st.session_state.popis = ''
    st.session_state.foto_nazov = 'Žiadna'

# --- ZÁPIS DÁT DO GOOGLE TABUĽKY ---
def uloz_do_google_tabulky():
    if not KNIŽNICE_OK:
        return False
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("Chýbajú prístupové kľúče (sekcia [gcp_service_account]) v Streamlit Secrets.")
            return False
            
        # Načítanie slovníka zo secrets
        info_o_kluci = dict(st.secrets["gcp_service_account"])
        
        # Prevod textových \n na skutočné znaky konca riadku pre privátny kľúč
        if "private_key" in info_o_kluci:
            info_o_kluci["private_key"] = info_o_kluci["private_key"].replace("\\n", "\n")
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(
            info_o_kluci,
            scopes=scopes
        )
        
        # Inicializácia gspread klienta
        gc = gspread.authorize(credentials)
        
        # OTVORENIE CEZ ID TABUĽKY
        id_tabulky = "11t9ktzcZSeDfBfH5BsmfFEsbtGFD559EONP7i1_e0ww"
        tabulka = gc.open_by_key(id_tabulky)
        list1 = tabulka.sheet1
        
        # Dáta berieme priamo zo session_state, kde sú na 100% uložené
        riadok_na_zapis = [
            st.session_state.meno, 
            st.session_state.telefon, 
            st.session_state.email, 
            st.session_state.vozidlo, 
            st.session_state.popis, 
            st.session_state.foto_nazov
        ]
        list1.append_row(riadok_na_zapis)
        return True
    except Exception as e:
        st.error(f"❌ Chyba pri zápise do Google Tabuľky. Detail: {e}")
        return False

# --- LOGIKA FORMULÁRA ---
if st.session_state.strana == 1:
    st.title("🛡️ Hlásenie poistnej udalosti")
    st.write("Vitajte. Tento sprievodca vás prevedie nahlásením udalosti.")
    st.button("Začať nahlásenie", on_click=chod_dalej)

elif st.session_state.strana == 2:
    st.title("👤 Kontaktné údaje")
    # Cez parameter key="meno" sa vstup ukladá priamo a okamžite do pamäte
    st.text_input("Meno a priezvisko", key="meno")
    st.text_input("Telefónne číslo", key="telefon")
    st.text_input("E-mailová adresa", key="email")
    if st.button("Ďalej"):
        if st.session_state.meno and st.session_state.telefon and st.session_state.email:  
            chod_dalej()
        else: 
            st.error("Prosím, vyplňte všetky povinné údaje.")

elif st.session_state.strana == 3:
    st.title("🚗 Údaje o vozidle")
    # KLÚČOVÁ OPRAVA: Vstup je priamo prepojený s klúčom 'vozidlo' v pamäti
    st.text_input("Zadajte EČV (ŠPZ) alebo VIN", key="vozidlo")
    st.button("Ďalej", on_click=chod_dalej)

elif st.session_state.strana == 4:
    st.title("📝 Popis a Fotografie")
    st.text_area("Popíšte, čo presne sa stalo:", key="popis", height=150)
    foto = st.file_uploader("Nahrajte fotku z miesta nehody", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Odoslať hlásenie"):
        with st.spinner('Ukladám hlásenie do databázy...'):
            if foto is not None: 
                st.session_state.foto_nazov = foto.name
            
            ulozene = uloz_do_google_tabulky()
            if ulozene:
                chod_dalej()

elif st.session_state.strana == 5:
    st.balloons()
    st.title("✅ Proces ukončený")
    st.success("Vaša poistná udalosť bola úspešne zaznamenaná v Google Tabuľke!")
    
    st.subheader("Zhrnutie odoslaných údajov:")
    st.write(f"**Klient:** {st.session_state.meno}")
    st.write(f"**Kontakt:** {st.session_state.telefon} | {st.session_state.email}")
    st.write(f"**Vozidlo:** {st.session_state.vozidlo}")
    st.write(f"**Popis:** {st.session_state.popis}")
    
    st.markdown("---")
    st.button("Nahlásiť novú udalosť", on_click=zacat_znova)
