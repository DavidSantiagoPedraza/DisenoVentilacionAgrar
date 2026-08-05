import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

# ==================================================
# Catálogo de ventiladores
# ==================================================

VENTILADORES = {

    "Atem Plus": {
        "caudal": 17000,
        "consumo": 0.7,
        "ruido": 74,
        "radio": 17
    },

    "Atem White": {
        "caudal": 16553,
        "consumo": 0.418,
        "ruido": 76,
        "radio": 17
    },

    "Multifan 63cm": {
            "caudal": 9950,
            "consumo": 0.26,
            "ruido": 57,
            "radio": 15
    },

    "Multifan 71cm": {
        "caudal": 14615,
        "consumo": 0.45,
        "ruido": 64,
        "radio": 17
    },

    "Multifan 92cm": {
        "caudal": 22150,
        "consumo": 0.62,
        "ruido": 69,
        "radio": 22
    },

    "Atem Basic": {
        "caudal": 9301,
        "consumo": 0.35,
        "ruido": 64,
        "radio": 12
    },

}

EXTRACTORES = {

    "ATEM 1100 EC": {
        "caudal": 32500,
        "consumo": 1.10,
        "ruido": 64
    },

    "ATEM 620": {
        "caudal": 5700,
        "consumo": 0.704,
        "ruido": 60
    },

    "ATEM BASIC": {
        "caudal": 9301,
        "consumo": 2.8,
        "ruido": 64
    }

}

logo = Image.open("logo.png")
st.set_page_config(
    page_title="AGRAR Ingeniería",
    page_icon=logo,
    layout="wide"
)

st.image(logo, width=100)
st.title("AGRAR Ingeniería")
st.subheader("Optimización de Ventilación para Invernaderos")

st.divider()

def select_best_lines(lines, distancia):

    if len(lines) == 0:
        return []

    best = []

    for start in range(len(lines)):

        sel = [lines[start]]

        last = sel[-1]

        for line in lines[start + 1:]:

            if line - last >= distancia:

                sel.append(line)

                last = line

        if len(sel) > len(best):

            best = sel

    return best

def plot_invernadero(
    largo,
    ancho_nave,
    num_naves,
    radio,
    dx,
    dy,
    mx,
    my,
    distancia_extractores
):
    fig, ax = plt.subplots(figsize=(12,8))

    ancho_total = ancho_nave * num_naves

    espacio_util = largo - 2 * mx

    if espacio_util < dx:

        xs = []

    else:

        n_cols = int(
            np.floor(espacio_util / dx)
        ) + 1

        espacio = espacio_util - ((n_cols - 1) * dx)

        offset = mx + espacio / 2

        xs = offset + np.arange(n_cols) * dx

    lines = np.arange(
    0,
    ancho_total + ancho_nave,
    ancho_nave
    )

    lines = lines[
        (lines >= my)
        &
        (lines <= ancho_total - my)
    ]

    ys = select_best_lines(
        lines,
        dy
    )

    centros = []

    for x in xs:

        for y in ys:

            c = Circle(
                (x, y),
                radio,
                alpha=0.4,
                color="skyblue"
            )

            ax.add_patch(c)

            ax.plot(
                x,
                y,
                "ro"
            )

            centros.append((x, y))

    #Extractores
    extractores = []

    espacio_util = ancho_total - 2 * my

    if espacio_util >= distancia_extractores:

        n_extractores = int(np.floor(espacio_util / distancia_extractores)) + 1

        espacio_sobrante = espacio_util - (n_extractores - 1) * distancia_extractores

        offset = my + espacio_sobrante / 2

        y_extractores = offset + np.arange(n_extractores) * distancia_extractores

    else:

        y_extractores = np.array([ancho_total / 2])

    for y in y_extractores:

        extractores.append((largo - 0.5, y))

    # =========================================
    # DIBUJAR LOS EXTRACTORES
    # =========================================

    for x, y in extractores:

        ax.scatter(
            x,
            y,
            s=120,
            color="blue",
            marker="s",
            edgecolors="black",
            zorder=10
        )

    ########################################

    res = 200

    xs_grid = np.linspace(
        0,
        largo,
        res
    )

    ys_grid = np.linspace(
        0,
        ancho_total,
        res
    )

    gx, gy = np.meshgrid(
        xs_grid,
        ys_grid
    )

    mask = np.zeros_like(
        gx,
        dtype=bool
    )

    for cx, cy in centros:

        mask |= (
            (gx-cx)**2
            +
            (gy-cy)**2
            <= radio**2
        )

    area_cubierta = (
    np.sum(mask)
    * (largo/res)
    * (ancho_total/res)
    )

    area_total = (
        len(centros)
        * np.pi
        * radio**2
    )

    traslape = max(
        0,
        100
        *
        (area_total-area_cubierta)
        /
        area_total
    )

    ax.plot(
    [0,largo,largo,0,0],
    [0,0,ancho_total,ancho_total,0],
    color="black"
    )


    #Camino central
    ancho_camino = 2   # metros
    x_camino = (largo / 2) - (ancho_camino / 2)

    camino = Rectangle(
        (x_camino, 0),
        ancho_camino,
        ancho_total,
        facecolor="orange",
        edgecolor="black",
        alpha=0.5
    )

    ax.add_patch(camino)

    ########################################

    for k in range(1,num_naves):

        ax.axhline(
            k*ancho_nave,
            linestyle="--",
            color="black"
        )

    ax.set_aspect("equal")

    ax.set_xlabel("Largo (m)")

    ax.set_ylabel("Ancho (m)")

    ax.set_title(
        "Distribución de ventilación"
    )

    return fig, len(centros), len(extractores), traslape

##Calculos Ventiladores
def calculos_ventiladores(
    num_ventiladores,
    largo,
    ancho_nave,
    num_naves,
    consumo_vent,
    ruido_vent,
    caudal_vent,
    altura
):


    N = num_ventiladores

    # Consumo eléctrico total
    consumo = N * consumo_vent

    # Ruido total
    if N > 0:
        ruido = ruido_vent + 10 * np.log10(N)
    else:
        ruido = 0

    # Caudal total
    caudal_total = N * caudal_vent

    # Volumen del invernadero
    #altura = 6  # m

    volumen = (
        largo
        * ancho_nave
        * num_naves
        * altura
    )

    # Renovaciones de aire por hora
    renovaciones = caudal_total / volumen

    return consumo, ruido, renovaciones

##Calculos Extractores

def calculos_extractores(
    num_extractores,
    consumo_ext,
    ruido_ext,
    caudal_ext,
    largo,
    ancho_nave,
    num_naves,
    altura
):

    #altura = 6

    volumen = (
        largo
        * ancho_nave
        * num_naves
        * altura
    )

    consumo = (
        num_extractores
        * consumo_ext
    )

    if num_extractores > 0:

        ruido = (
            ruido_ext
            + 10*np.log10(num_extractores)
        )

    else:

        ruido = 0

    caudal_total = (
        num_extractores
        * caudal_ext
    )

    renovaciones = (
        caudal_total
        / volumen
    )

    return (
        consumo,
        ruido,
        renovaciones
    )

##La interfaz de usuario con Streamlit

st.sidebar.header("Parámetros del invernadero")

# =====================================
# Selección del Extractor
# =====================================

st.sidebar.subheader("Extractor")

modelo_extractor = st.sidebar.selectbox(
    "Modelo de extractor",
    list(EXTRACTORES.keys())
)

datos_extractor = EXTRACTORES[modelo_extractor]

caudal_ext = datos_extractor["caudal"]

consumo_ext = datos_extractor["consumo"]

ruido_ext = datos_extractor["ruido"]

# =====================================
# FICHA TECNICA DEL EXTRACTOR
# =====================================

st.sidebar.info(
    f"""
### Extractor seleccionado

**Caudal:** {caudal_ext:,.0f} m³/h

**Consumo:** {consumo_ext:.2f} kW

**Ruido:** {ruido_ext:.1f} dB
"""
)


# =====================================
# Selección del ventilador
# =====================================

st.sidebar.subheader("Ventilador")

modelo = st.sidebar.selectbox(
    "Modelo de ventilador",
    list(VENTILADORES.keys())
)

# =====================================
# AQUÍ VA EL PASO 2.2
# =====================================

datos_ventilador = VENTILADORES[modelo]

# =====================================
# AQUÍ VA EL PASO 2.3
# =====================================

caudal_vent = datos_ventilador["caudal"]
consumo_vent = datos_ventilador["consumo"]
ruido_vent = datos_ventilador["ruido"]
radio_default = datos_ventilador["radio"]

st.sidebar.markdown("### Especificaciones del ventilador")

st.sidebar.info(
    f"""
**Caudal:** {caudal_vent:,.0f} m³/h

**Consumo:** {consumo_vent:.2f} kW

**Ruido:** {ruido_vent:.1f} dB

**Radio recomendado:** {radio_default:.1f} m
"""
)

largo = st.sidebar.number_input(
    "Largo (m)",
    value=60.0,
    min_value=1.0
)

ancho_nave = st.sidebar.number_input(
    "Ancho de nave (m)",
    value=6.8,
    min_value=1.0
)

altura = st.sidebar.number_input(
    "Altura de nave (m)",
    value=4.5,
    min_value=1.0
)

num_naves = st.sidebar.number_input(
    "Número de naves",
    value=11,
    min_value=1,
    step=1
)

radio = st.sidebar.number_input(
    "Radio de cobertura (m)",
    value=float(radio_default),
    min_value=1.0
)

dx = st.sidebar.number_input(
    "Distancia entre ventiladores de diferentes tablas (m)",
    value=28.0,
    min_value=1.0
)

dy = st.sidebar.number_input(
    "Distancia entre ventiladores de la misma tabla (m)",
    value=28.0,
    min_value=1.0
)

mx = st.sidebar.number_input(
    "Distancia del ventilador al borde (X) (m)",
    value=12.0,
    min_value=0.0
)

my = st.sidebar.number_input(
    "Distancia del ventilador al borde (Y) (m)",
    value=14.0,
    min_value=0.0
)

distancia_extractores = st.sidebar.number_input(
    "Distancia entre extractores (m)",
    min_value=1.0,
    value=20.0,
    step=0.5
)

if st.sidebar.button("Generar distribución"):
    fig, num_ventiladores, num_extractores, traslape = plot_invernadero(
        largo,
        ancho_nave,
        num_naves,
        radio,
        dx,
        dy,
        mx,
        my,
        distancia_extractores
    )

    consumo, ruido, renovaciones = calculos_ventiladores(
        num_ventiladores,
        largo,
        ancho_nave,
        num_naves,
        consumo_vent,
        ruido_vent,
        caudal_vent,
        altura
    )

    consumo_ext_total, ruido_ext_total, renovaciones_ext = calculos_extractores(
        num_extractores,
        consumo_ext,
        ruido_ext,
        caudal_ext,
        largo,
        ancho_nave,
        num_naves,
        altura
    )


    st.pyplot(fig)

    #st.write(f"Número de ventiladores: {num_ventiladores}")
    #st.write(f"Traslape: {traslape:.2f}%")

    col1, col2, col3, col4 = st.columns(4)

#DATOS VENTILADORES
    #Num de ventiladore
    col1.metric(
    "Ventiladores",
    num_ventiladores
    )

    #Consumo
    col2.metric(
    "Consumo Ventiladores",
    f"{consumo:.2f} kW"
    )

    #Ruido
    col3.metric(
    "Ruido Ventiladores",
    f"{ruido:.1f} dB"
    )

    #Renovaciones
    col4.metric(
    "Recirculaciones",
    f"{renovaciones:.2f} h⁻¹"
    )

    st.metric(
    "Traslape de cobertura",
    f"{traslape:.2f} %"
    )


#DATOS EXTRACTORES
    #Num de extractores
    col1.metric(
    "Extractores",
    num_extractores
    )

    #Consumo
    col2.metric(
    "Consumo Extractores",
    f"{consumo_ext_total:.2f} kW"
    )

    #Ruido
    col3.metric(
    "Ruido Extractores",
    f"{ruido_ext_total:.1f} dB"
    )

    #Renovaciones
    col4.metric(
    "Renovaciones",
    f"{renovaciones_ext:.2f} h⁻¹"
    )
    