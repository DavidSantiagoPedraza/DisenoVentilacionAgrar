import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

st.set_page_config(
    page_title="AGRAR Ingeniería",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 AGRAR Ingeniería")
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
    my
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

    return fig, len(centros), traslape

def calculos(
    num_ventiladores,
    largo,
    ancho_nave,
    num_naves
):
    consumo_vent = 0.55      # kW por ventilador
    ruido_vent = 74          # dB por ventilador
    caudal_vent = 17000      # m³/h por ventilador

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
    altura = 6  # m

    volumen = (
        largo
        * ancho_nave
        * num_naves
        * altura
    )

    # Renovaciones de aire por hora
    renovaciones = caudal_total / volumen

    return consumo, ruido, renovaciones

##LA interfaz de usuario con Streamlit

st.sidebar.header("Parámetros del invernadero")

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

num_naves = st.sidebar.number_input(
    "Número de naves",
    value=23,
    min_value=1,
    step=1
)

radio = st.sidebar.number_input(
    "Radio de cobertura (m)",
    value=20.0,
    min_value=1.0
)

dx = st.sidebar.number_input(
    "Distancia X (m)",
    value=28.0,
    min_value=1.0
)

dy = st.sidebar.number_input(
    "Distancia Y (m)",
    value=28.0,
    min_value=1.0
)

mx = st.sidebar.number_input(
    "Margen X (m)",
    value=12.0,
    min_value=0.0
)

my = st.sidebar.number_input(
    "Margen Y (m)",
    value=14.0,
    min_value=0.0
)

if st.sidebar.button("Generar distribución"):
    fig, num_ventiladores, traslape = plot_invernadero(
        largo,
        ancho_nave,
        num_naves,
        radio,
        dx,
        dy,
        mx,
        my
    )

    consumo, ruido, renovaciones = calculos(
        num_ventiladores,
        largo,
        ancho_nave,
        num_naves
    )
    st.pyplot(fig)

    st.write(f"Número de ventiladores: {num_ventiladores}")
    st.write(f"Traslape: {traslape:.2f}%")

    col1, col2, col3, col4 = st.columns(4)

    #Num de ventiladore
    col1.metric(
    "Ventiladores",
    num_ventiladores
    )

    #Consumo
    col2.metric(
    "Consumo",
    f"{consumo:.2f} kW"
    )

    #Ruido
    col3.metric(
    "Ruido",
    f"{ruido:.1f} dB"
    )

    #Renovaciones
    col4.metric(
    "Renovaciones",
    f"{renovaciones:.2f} h⁻¹"
    )

    st.metric(
    "Traslape de cobertura",
    f"{traslape:.2f} %"
    )

    