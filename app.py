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

# --- PAMÄŤ APLIKÁCIE ---
if 'strana' not in st.session_state:
    st.session_state.strana = 1
if 'data' not in st.session_state:
    st.session_state.data = {'meno': '', 'telefon': '', 'email': '', 'vozidlo': '', 'popis': '', 'foto_nazov': 'Žiadna'}

def chod_dalej(): 
    st.session_state.strana += 1

def zacat_znova():
    st.session_state.strana = 1
    st.session_state.data = {'meno': '', 'telefon': '', 'email': '', 'vozidlo': '', 'popis': '', 'foto_nazov': 'Žiadna'}

# --- ZÁPIS DÁT DO GOOGLE TABUĽKY ---
def uloz_do_google_tabulky(data):
    if not KNIŽNICE_OK:
        return False
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("Chýbajú prístupové kľúče (sekcia [gcp_service_account]) v Streamlit Secrets.")
            return False
            
        # Načítanie slovníka zo secrets
        info_o_kluci = dict(st.secrets["gcp_service_account"])
        
        # FIX: Oprava formátu private_key (prevedie textové \n na skutočné znaky nového riadku)
        if "private_key" in info_o_kluci:
            info_o_kluci["private_key"] = info_o_kluci["private_key"].replace("\\n", "\n")
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(
            info_o_kluci,
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        tabulka = gc.open("Databaza_Udalosti")
        list1 = tabulka.sheet1
        
        riadok_na_zapis = [data['meno'], data['telefon'], data['email'], data['vozidlo'], data['popis'], data['foto_nazov']]
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
    meno = st.text_input("Meno a priezvisko", value=st.session_state.data['meno'])
    telefon = st.text_input("Telefónne číslo", value=st.session_state.data['telefon'])
    email = st.text_input("E-mailová adresa", value=st.session_state.data['email'])
    if st.button("Ďalej"):
        if meno and telefon and email:  
            st.session_state.data['meno'], st.session_state.data['telefon'], st.session_state.data['email'] = meno, telefon, email
            chod_dalej()
        else: 
            st.error("Prosím, vyplňte všetky povinné údaje.")

elif st.session_state.strana == 3:
    st.title("🚗 Údaje o vozidle")
    vozidlo = st.text_input("Zadajte EČV (ŠPZ) alebo VIN", value=st.session_state.data['vozidlo'])
    if st.button("Ďalej"):
        st.session_state.data['vozidlo'] = vozidlo
        chod_dalej()

elif st.session_state.strana == 4:
    st.title("📝 Popis a Fotografie")
    popis = st.text_area("Popíšte, čo presne sa stalo:", value=st.session_state.data['popis'], height=150)
    foto = st.file_uploader("Nahrajte fotku z miesta nehody", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Odoslať hlásenie"):
        with st.spinner('Ukladám hlásenie do databázy...'):
            st.session_state.data['popis'] = popis
            if foto is not None: 
                st.session_state.data['foto_nazov'] = foto.name
            
            ulozene = uloz_do_google_tabulky(st.session_state.data)
            if ulozene:
                chod_dalej()

elif st.session_state.strana == 5:
    st.balloons()
    st.title("✅ Proces ukončený")
    st.success("Vaša poistná udalosť bola úspešne zaznamenaná v Google Tabuľke!")
    
    st.subheader("Zhrnutie odoslaných údajov:")
    d = st.session_state.data
    st.write(f"**Klient:** {d['meno']}")
    st.write(f"**Kontakt:** {d['telefon']} | {d['email']}")
    st.write(f"**Vozidlo:** {d['vozidlo']}")
    st.write(f"**Popis:** {d['popis']}")
    
    st.markdown("---")
    st.button("Nahlásiť novú udalosť", on_click=zacat_znova)
