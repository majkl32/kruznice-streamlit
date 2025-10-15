import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from fpdf import FPDF
import tempfile
import os
import requests

# --- Nastavení stránky ---
st.set_page_config(page_title="Kružnice – Body na kružnici", page_icon="⭕", layout="wide")

st.title("⭕ Body na kružnici – webová aplikace")

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

pdf_button_col1, pdf_button_col2 = st.columns([2,1])
with pdf_button_col1:
    pdf_note = st.text_area("Poznámka do PDF (volitelné)", value="")

with pdf_button_col2:
    if st.button("Vytvořit a stáhnout PDF"):
        # Create PDF in memory
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            # 1) Save plot page
            fig_plot, ax_plot = plt.subplots(figsize=(8,8))
            ax_plot.scatter(df["x"], df["y"], c=color, s=20)
            ax_plot.set_aspect('equal', adjustable='box')
            ax_plot.set_xlabel(f"X ({units})")
            ax_plot.set_ylabel(f"Y ({units})")
            ax_plot.set_title("Bodová kružnice")
            if show_grid:
                ax_plot.grid(True, linestyle='--', linewidth=0.5)
            pdf.savefig(fig_plot, bbox_inches='tight')
            plt.close(fig_plot)

            # 2) Save parameters page as a simple text figure
            fig_text = plt.figure(figsize=(8,11))
            plt.axis('off')
            lines = [
                "Parametry úlohy:",
                f" - Střed: ({center_x:.4f}, {center_y:.4f}) {units}",
                f" - Poloměr: {radius:.4f} {units}",
                f" - Počet bodů: {num_points}",
                f" - Barva bodů: {color}",
                f" - Použit nahraný soubor: {'Ano' if (uploaded_file is not None and use_uploaded) else 'Ne'}",
                "",
                "Autor / kontakt:",
                f" - Jméno: {author_name}",
                f" - Kontakt: {author_contact}",
                "",
                "Poznámka:",
                pdf_note
            ]
            # render text
            y = 0.95
            for ln in lines:
                plt.text(0.05, y, ln, fontsize=12, transform=plt.gcf().transFigure)
                y -= 0.05
            pdf.savefig(fig_text, bbox_inches='tight')
            plt.close(fig_text)

        buffer.seek(0)
        st.success("PDF připraveno ke stažení.")
        st.download_button("Stáhnout PDF", data=buffer, file_name="kruznice_report.pdf", mime="application/pdf")

st.write("---")
st.caption("Tip: pro tisk do fyzické tiskárny můžeš stáhnout PDF a použít tisk z prohlížeče nebo použít tisk přímo (Ctrl+P) z rozhraní Streamlit pro tuto stránku.")
