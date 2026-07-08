import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- ZÁKLADNÉ NASTAVENIE STRÁNKY ---
# Musí byť prvý príkaz Streamlitu
st.set_page_config(page_title="Poistné udalosti", page_icon="📋", layout="centered")

# --- BEZPEČNOSTNÁ KONTROLA KNIŽNÍC ---
try:
    import gspread
    from google.oauth2.service_account import Credentials
    KNIŽNICE_OK = True
except ImportError:
    KNIŽNICE_OK = False
    st.warning("⚠️ Chýbajú knižnice pre Google Tabuľky. Aby sa údaje ukladali, vytvor/uprav súbor `requirements.txt` na GitHube a vlož doň: `streamlit`, `gspread`, `google-auth`.")

# --- PAMÄŤ APLIKÁCIE (Session State) ---
if 'strana' not in st.session_state:
    st.session_state.strana = 1
if 'data' not in st.session_state:
    st.session_state.data = {'meno': '', 'telefon': '', 'email': '', 'vozidlo': '', 'popis': '', 'foto_nazov': 'Žiadna'}

def chod_dalej(): 
    st.session_state.strana += 1

def zacat_znova():
    st.session_state.strana = 1
    st.session_state.data = {'meno': '', 'telefon': '', 'email': '', 'vozidlo': '', 'popis': '', 'foto_nazov': 'Žiadna'}

# --- FUNKCIA 1: ZÁPIS DO GOOGLE TABUĽKY ---
def uloz_do_google_tabulky(data):
    if not KNIŽNICE_OK:
        return False
        
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("Chýbajú prístupové kľúče ku Google Cloud v sekcii Streamlit Secrets.")
            return False
            
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        tabulka = gc.open("Databaza_Udalosti")
        list1 = tabulka.sheet1
        
        riadok_na_zapis = [data['meno'], data['telefon'], data['email'], data['vozidlo'], data['popis'], data['foto_nazov']]
        list1.append_row(riadok_na_zapis)
        return True
    except Exception as e:
        st.error(f"❌ Chyba pri zápise do Google Tabuľky: Skontrolujte, či sa tabuľka volá 'Databaza_Udalosti' a či má robot editorské práva. Detail chyby: {e}")
        return False

# --- FUNKCIA 2: ODOSLANIE E-MAILU ---
def posli_email_notifikaciu(data):
    try:
        if "EMAIL_SENDER" not in st.secrets:
            st.error("Chýbajú heslá k e-mailu v sekcii Streamlit Secrets.")
            return False
            
        EMAIL_ODOSIELATEL = st.secrets["EMAIL_SENDER"]
        EMAIL_HESLO = st.secrets["EMAIL_PASSWORD"]
        EMAIL_PRIJIMATEL = st.secrets["EMAIL_RECEIVER"]

        msg = MIMEMultipart()
        msg['From'] = f"Formulár <{EMAIL_ODOSIELATEL}>"
        msg['To'] = EMAIL_PRIJIMATEL
        msg['Subject'] = f"🚨 NOVÁ POISTNÁ UDALOSŤ: {data['meno']}"

        telo = f"""
Nová nahlásená udalosť z webu:

KLIENT: {data['meno']}
TELEFÓN: {data['telefon']}
E-MAIL: {data['email']}

VOZIDLO (EČV/VIN): {data['vozidlo']}
POPIS NEHODY: 
{data['popis']}

Fotografia priložená: {data['foto_nazov']}
        """
        msg.attach(MIMEText(telo, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ODOSIELATEL, EMAIL_HESLO)
        server.sendmail(EMAIL_ODOSIELATEL, EMAIL_PRIJIMATEL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Chyba pri odosielaní e-mailu: Skontrolujte nastavenie hesla. Detail chyby: {e}")
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
        with st.spinner('Spracúvam údaje...'):
            st.session_state.data['popis'] = popis
            if foto is not None: 
                st.session_state.data['foto_nazov'] = foto.name
            
            # Pokus o zápis a odoslanie
            ulozene = uloz_do_google_tabulky(st.session_state.data)
            poslane = posli_email_notifikaciu(st.session_state.data)
            
            # Pustíme používateľa ďalej, aj keby zlyhalo odoslanie (aby nezostal zaseknutý)
            chod_dalej()

elif st.session_state.strana == 5:
    st.balloons()
    st.title("✅ Proces ukončený")
    st.info("Vaše údaje prešli systémom.")
    
    st.subheader("Zhrnutie zadaných údajov:")
    d = st.session_state.data
    st.write(f"**Klient:** {d['meno']}")
    st.write(f"**Kontakt:** {d['telefon']} | {d['email']}")
    st.write(f"**Vozidlo:** {d['vozidlo']}")
    st.write(f"**Popis:** {d['popis']}")
    
    st.markdown("---")
    st.button("Nahlásiť novú udalosť", on_click=zacat_znova)
