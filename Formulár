import streamlit as st
import csv
import os

# Nastavenie vzhľadu stránky
st.set_page_config(page_title="Poistné udalosti", page_icon="📋")

# --- PAMÄŤ APLIKÁCIE ---
if 'strana' not in st.session_state:
    st.session_state.strana = 1

if 'data' not in st.session_state:
    # Pridali sme 'foto_nazov' do pamäte
    st.session_state.data = {
        'meno': '', 'telefon': '', 'email': '', 'vozidlo': '', 'popis': '', 'foto_nazov': 'Žiadna'
    }

# --- FUNKCIE PRE UKLADANIE A NAVIGÁCIU ---
def uloz_do_tabulky(data):
    subor_existuje = os.path.isfile('databaza_udalosti.csv')
    
    with open('databaza_udalosti.csv', mode='a', newline='', encoding='utf-8') as f:
        # Hlavičky tabuľky sa zhodujú s našimi dátami
        hlavicky = ['meno', 'telefon', 'email', 'vozidlo', 'popis', 'foto_nazov']
        zapisovac = csv.DictWriter(f, fieldnames=hlavicky)
        
        if not subor_existuje:
            zapisovac.writeheader()
            
        zapisovac.writerow(data)

def chod_dalej():
    st.session_state.strana += 1

def zacat_znova():
    # Vyresetuje aplikáciu na stranu 1 a vymaže údaje pre ďalšieho klienta
    st.session_state.strana = 1
    st.session_state.data = {
        'meno': '', 'telefon': '', 'email': '', 'vozidlo': '', 'popis': '', 'foto_nazov': 'Žiadna'
    }

# --- LOGIKA JEDNOTLIVÝCH STRÁNOK ---

# STRANA 1: Začíname
if st.session_state.strana == 1:
    st.title("🛡️ Hlásenie poistnej udalosti")
    st.write("Vitajte. Tento sprievodca vás prevedie nahlásením udalosti.")
    st.button("Začať nahlásenie", on_click=chod_dalej)

# STRANA 2: Kontaktné údaje
elif st.session_state.strana == 2:
    st.title("👤 Kontaktné údaje")
    st.info("Všetky údaje na tejto strane sú povinné.")
    
    meno = st.text_input("Meno a priezvisko", value=st.session_state.data['meno'])
    telefon = st.text_input("Telefónne číslo", value=st.session_state.data['telefon'])
    email = st.text_input("E-mailová adresa", value=st.session_state.data['email'])

    if st.button("Ďalej"):
        if meno and telefon and email:  
            st.session_state.data['meno'] = meno
            st.session_state.data['telefon'] = telefon
            st.session_state.data['email'] = email
            chod_dalej()
        else:
            st.error("Prosím, vyplňte všetky povinné údaje.")

# STRANA 3: Identifikácia vozidla
elif st.session_state.strana == 3:
    st.title("🚗 Údaje o vozidle")
    vozidlo = st.text_input("Zadajte EČV (ŠPZ) alebo VIN", value=st.session_state.data['vozidlo'])
    
    if st.button("Ďalej"):
        st.session_state.data['vozidlo'] = vozidlo
        chod_dalej()

# STRANA 4: Popis udalosti a Fotografie
elif st.session_state.strana == 4:
    st.title("📝 Popis a Fotografie")
    popis = st.text_area("Popíšte, čo presne sa stalo:", value=st.session_state.data['popis'], height=150)
    
    st.markdown("### 📷 Priložte fotografiu (voliteľné)")
    # Pridanie widgetu na nahrávanie súborov
    foto = st.file_uploader("Nahrajte fotku z miesta nehody", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Odoslať hlásenie"):
        st.session_state.data['popis'] = popis
        # Ak používateľ nahral fotku, uložíme jej názov
        if foto is not None:
            st.session_state.data['foto_nazov'] = foto.name
            
        uloz_do_tabulky(st.session_state.data)
        chod_dalej()

# STRANA 5: Hotovo
elif st.session_state.strana == 5:
    st.balloons()
    st.title("✅ Hotovo")
    st.success("Vaša poistná udalosť bola úspešne zaznamenaná a uložená do databázy.")
    
    st.subheader("Zhrnutie zadaných údajov:")
    d = st.session_state.data
    st.write(f"**Klient:** {d['meno']}")
    st.write(f"**Kontakt:** {d['telefon']} | {d['email']}")
    st.write(f"**Vozidlo:** {d['vozidlo']}")
    st.write(f"**Popis:** {d['popis']}")
    st.write(f"**Priložená fotografia:** {d['foto_nazov']}")
    
    st.markdown("---")
    st.button("Nahlásiť novú udalosť", on_click=zacat_znova)
