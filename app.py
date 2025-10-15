# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO

st.set_page_config(page_title="Bodová kružnice", layout="wide")

st.title("⭕Bodová kružnice — generátor a vizualizace")

# --- SIDEBAR: informace, autor ---
with st.sidebar:
    st.header("O aplikaci")
    st.write(
        """
        Tato aplikace generuje nebo vizualizuje body na kružnici.
        Umožňuje zadat střed, poloměr, počet bodů a barvu bodů.
        Součástí je export grafu a parametrů do PDF.
        """
    )
    st.markdown("---")
    st.header("Autor / Kontakt")
    author_name = st.text_input("Tvé jméno (pro PDF)", value="Jméno Příjmení")
    author_contact = st.text_input("Kontakt (email / telefon)", value="email@example.com")
    st.markdown("Technologie: Python, Streamlit, NumPy, Pandas, Matplotlib.")
    st.markdown("---")
    st.info("Nahraj Excel s `x` a `y`, pokud chceš vizualizovat vlastní data.\nZačne se použivat nahraný soubor pokud je nahraný.")

st.write("## Vstupní parametry")

col1, col2, col3 = st.columns([1,1,1])

with col1:
    use_uploaded = st.checkbox("Použít nahraný Excel (přepisovat generování)", value=False)
    uploaded_file = st.file_uploader("Nahraj .xlsx nebo .csv (sloupce x,y)", type=["xlsx","csv"])

with col2:
    st.subheader("Parametry kružnice (pro generování)")
    center_x = st.number_input("Střed x", value=0.0, format="%.4f")
    center_y = st.number_input("Střed y", value=0.0, format="%.4f")
    radius = st.number_input("Poloměr", min_value=0.0, value=1.0, format="%.4f")
    units = st.text_input("Jednotka os (např. m)", value="m")

with col3:
    num_points = st.slider("Počet bodů na kružnici", min_value=3, max_value=5000, value=100)
    color = st.color_picker("Barva bodů", value="#1f77b4")
    show_grid = st.checkbox("Zobrazit mřížku", value=True)
    show_coords = st.checkbox("Zobrazit tabulku souřadnic", value=True)

# --- Load data either from upload or generate ---
df = None
error_msg = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        # Ensure x,y exist
        if not {"x","y"}.issubset(df.columns):
            # try lowercase/uppercase tolerance
            cols = {c.lower(): c for c in df.columns}
            if "x" in cols and "y" in cols:
                df = df.rename(columns={cols["x"]:"x", cols["y"]:"y"})
            else:
                error_msg = "Soubor musí obsahovat sloupce 'x' a 'y' (citlivost na názvy sloupců aplikována)."
                df = None
        else:
            df = df[["x","y"]].astype(float)
        if df is not None:
            st.success(f"Nahrán soubor: {uploaded_file.name} — {len(df)} bodů")
    except Exception as e:
        error_msg = f"Chyba při načítání souboru: {e}"
        df = None

# If user opted to use uploaded data, enforce that
if use_uploaded and df is None:
    st.warning("Vybral(a) jste použití nahraného souboru, ale žádný validní .xlsx/.csv s x,y byl nahrán.")
elif (not use_uploaded) or (use_uploaded and df is None):
    # generate circle
    theta = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    x = center_x + radius * np.cos(theta)
    y = center_y + radius * np.sin(theta)
    df_generated = pd.DataFrame({"x": x, "y": y})
    if df is None or not use_uploaded:
        df = df_generated

if error_msg:
    st.error(error_msg)

# --- Plot ---
st.write("## Graf kružnice")
fig, ax = plt.subplots(figsize=(6,6))
ax.scatter(df["x"], df["y"], c=color, s=20)
ax.set_aspect('equal', adjustable='box')
ax.set_xlabel(f"X ({units})")
ax.set_ylabel(f"Y ({units})")
ax.set_title("Bodová kružnice (vizualizace)")
if show_grid:
    ax.grid(True, linestyle='--', linewidth=0.5)

# adjust ticks to include unit in label (but keep numeric ticks)
xticks = ax.get_xticks()
yticks = ax.get_yticks()
ax.set_xticklabels([f"{t:.2f}" for t in xticks])
ax.set_yticklabels([f"{t:.2f}" for t in yticks])

st.pyplot(fig)

# Show coordinates table and CSV download
if show_coords:
    st.write("### Tabulka souřadnic")
    st.dataframe(df.reset_index(drop=True).rename(columns={"x":"x ("+units+")", "y":"y ("+units+")"}))

    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button("Stáhnout souřadnice (CSV)", data=csv_bytes, file_name="kruznice_souradnice.csv", mime="text/csv")

# --- PDF export ---
st.write("---")
st.write("## Export do PDF")

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

st.write("## Další možnosti / nápady")
st.write(
    """
    - Přidat měření délky oblouku mezi dvěma body.\n
    - Přidat označení indexů bodů přímo v grafu.\n
    - Export do SVG nebo EPS pro vektorové zpracování.
    """
)

