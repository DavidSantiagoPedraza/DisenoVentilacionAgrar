import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
# --------------------------------------------------
# Configuración de la página
# --------------------------------------------------

st.set_page_config(
    page_title="AGRAR Ingeniería",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 AGRAR Ingeniería")
st.subheader("Optimización de Ventilación para Invernaderos")

st.divider()

# --------------------------------------------------
# Barra lateral
# --------------------------------------------------

st.sidebar.header("Parámetros")

largo = st.sidebar.number_input(
    "Largo (m)",
    value=60.0
)

ancho_nave = st.sidebar.number_input(
    "Ancho de la nave (m)",
    value=6.8
)

num_naves = st.sidebar.number_input(
    "Número de naves",
    value=23,
    step=1
)

radio = st.sidebar.number_input(
    "Radio de cobertura (m)",
    value=20.0
)

dx = st.sidebar.number_input(
    "Distancia X (m)",
    value=28.0
)

dy = st.sidebar.number_input(
    "Distancia Y (m)",
    value=28.0
)

mx = st.sidebar.number_input(
    "Margen X (m)",
    value=12.0
)

my = st.sidebar.number_input(
    "Margen Y (m)",
    value=14.0
)

largo = st.number_input(
    "Largo (m)",
    value=60.0
)
ancho_nave = st.number_input(
    "Ancho de nave (m)",
    value=6.8
)

# --------------------------------------------------
# Botón
# --------------------------------------------------

generar = st.sidebar.button("Generar distribución")

# --------------------------------------------------
# Área principal
# --------------------------------------------------

if generar:

    st.success("Los parámetros fueron cargados correctamente.")

    st.write("### Parámetros seleccionados")

    st.write({
        "Largo": largo,
        "Ancho nave": ancho_nave,
        "Número de naves": num_naves,
        "Radio": radio,
        "Distancia X": dx,
        "Distancia Y": dy,
        "Margen X": mx,
        "Margen Y": my
    })

def select_best_lines(lines, distancia): #Linea son las filas de parales donde se ponen los ventiladores y distancia es la distancia minima entre ventiladores
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
    my):

    
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

    ys = select_best_lines(lines, dy)


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

            ax.plot(x, y, "ro")

            centros.append((x, y))

    #self.num_ventiladores = len(centros)


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
            (gx - cx)**2
            +
            (gy - cy)**2
            <= radio**2
        )

    area_cubierta = (
        np.sum(mask)
        * (largo / res)
        * (ancho_total / res)
    )

    area_total = (
        len(centros)
        * np.pi
        * radio**2
    )

    traslape = max(
        0,
        100 *
        (area_total - area_cubierta)
        / area_total
    )

    ax.plot(
    [0, largo, largo, 0, 0],
    [0, 0, ancho_total,
        ancho_total, 0],
    color="black"
    )

    for k in range(1, num_naves):

        ax.axhline(
            k * ancho_nave,
            linestyle="--",
            color="black"
        )

    ax.set_aspect("equal")

    ax.set_xlabel("Largo (m)")

    ax.set_ylabel("Ancho (m)")

    ax.set_title(
        "Distribución de ventilación"
    )
    return fig, len(centros)

# fig, num_ventiladores = plot_invernadero(
#     largo,
#     ancho_nave,
#     num_naves,
#     radio,
#     dx,
#     dy,
#     mx,
#     my
# )

# st.pyplot(fig)

def calculos(
    num_ventiladores,
    largo,
    ancho_nave,
    num_naves
):
    consumo_vent = 0.55
    ruido_vent = 74
    caudal_vent = 17000

    N = num_ventiladores

    consumo = N * consumo_vent

    if N > 0:
        ruido = ruido_vent + 10 * np.log10(N)
    else:
        ruido = 0

    caudal_total = N * caudal_vent

    altura = 6

    volumen = (
        largo
        * ancho_nave
        * num_naves
        * altura
    )

    renovaciones = (
        caudal_total / volumen
    )

    return consumo, ruido, renovaciones


# Interfaz Streamlit
st.write(
    "Calculadora para distribución de ventiladores."
)



if st.button("Generar distribución"):
    fig, num_ventiladores = plot_invernadero(
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

    st.write(f"Consumo eléctrico: {consumo:.2f} kW")

    st.write(f"Ruido: {ruido:.1f} dB")

    st.write(f"Renovaciones/hora: {renovaciones:.2f}")
