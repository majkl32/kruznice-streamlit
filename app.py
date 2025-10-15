import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from fpdf import FPDF
import tempfile
import os
import requests

# --- Nastavení stránky ---
st.set_page_config(page_title="Kružnice – Body na kružnici", page_icon="⚪", layout="wide")

st.title("⚪ Body na kružnici – webová aplikace")

# --- Vstupní parametry ---
st.sidebar.header("Parametry kružnice")
cx = st.sidebar.number_input("Střed X", value=0.0)
cy = st.sidebar.number_input("Střed Y", value=0.0)
r = st.sidebar.number_input("Poloměr", value=5.0, min_value=0.0)
n = st.sidebar.number_input("Počet bodů na kružnici", value=12, min_value=1, step=1)
barva = st.sidebar.color_picker("Barva bodů", "#ff3b30")
jednotka = st.sidebar.text_input("Jednotka (např. m)", "m")

st.sidebar.header("Autor a kontakt")
autor = st.sidebar.text_input("Tvé jméno", "Jan Novák")
kontakt = st.sidebar.text_input("Kontakt (e-mail, web...)", "jan.novak@example.com")

# --- Výpočet bodů ---
uhly = np.linspace(0, 2 * np.pi, n, endpoint=False)
x = cx + r * np.cos(uhly)
y = cy + r * np.sin(uhly)

# --- Vykreslení ---
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect("equal", adjustable="box")
ax.grid(True, which="both", linestyle="--", linewidth=0.5)
ax.axhline(0, color="black", linewidth=1)
ax.axvline(0, color="black", linewidth=1)
ax.set_xlabel(f"X [{jednotka}]")
ax.set_ylabel(f"Y [{jednotka}]")

# Kružnice a body
ax.plot(cx, cy, "ko", label="Střed")
ax.plot(x, y, "o", color=barva, label="Body na kružnici")
circle = plt.Circle((cx, cy), r, fill=False, color="blue", linewidth=1.5)
ax.add_artist(circle)

# Popisky bodů
for i, (xi, yi) in enumerate(zip(x, y), 1):
    ax.text(xi, yi, f"{i}", fontsize=9, ha="left", va="bottom")

ax.legend()
st.pyplot(fig)

# --- Funkce pro vytvoření PDF s automatickým fontem ---
def create_pdf():
    buffer = BytesIO()
    pdf = FPDF()
    pdf.add_page()

    # --- Stáhnout DejaVuSans.ttf pokud neexistuje ---
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(r.content)

    # Přidání Unicode fontu
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "Kružnice – parametry úlohy", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 8, f"Střed: ({cx}, {cy}) {jednotka}", ln=True)
    pdf.cell(0, 8, f"Poloměr: {r} {jednotka}", ln=True)
    pdf.cell(0, 8, f"Počet bodů: {n}", ln=True)
    pdf.cell(0, 8, f"Barva bodů: {barva}", ln=True)
    pdf.cell(0, 8, f"Autor: {autor}", ln=True)
    pdf.cell(0, 8, f"Kontakt: {kontakt}", ln=True)

    # --- Ulož graf do dočasného obrázku ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, format="png", bbox_inches="tight")
        tmpfile_path = tmpfile.name

    # --- Vlož do PDF ---
    pdf.image(tmpfile_path, x=10, y=80, w=180)

    # --- Smaž dočasný soubor ---
    os.remove(tmpfile_path)

    pdf.output(buffer)
    return buffer.getvalue()

# --- Tlačítko pro stažení PDF ---
st.download_button(
    label="📄 Stáhnout PDF",
    data=create_pdf(),
    file_name="kruznice.pdf",
    mime="application/pdf",
)

# --- Info ---
st.markdown("---")
with st.expander("ℹ️ Informace o aplikaci"):
    st.write("""
    **Autor aplikace:** *zadej své jméno v levém panelu*  
    **Asistent:** GPT-5  
    **Použité technologie:** Streamlit, Matplotlib, NumPy, FPDF  
    **Funkce:**  
    - zadání středu, poloměru, počtu bodů, barvy a jednotky  
    - vykreslení kružnice s body  
    - export výsledku a parametrů do PDF  
    """)
