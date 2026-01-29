'''import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.title("Dashboard de Análisis de Sensibilidad del VPN")

# Sliders (variables financieras)
r = st.slider("Tasa de interés (%)", 5.0, 15.0, 8.0) / 100
i = st.slider("Inflación (%)", 0.0, 10.0, 4.0) / 100
e = st.slider("Tipo de cambio (factor)", 1.0, 1.5, 1.1)

# Parámetros del proyecto
I0 = 10000
FC_base = 3000
n = 3

# Cálculo del VPN
VPN = 0
for t in range(1, n + 1):
    FC = FC_base * (1 - i) / e
    VPN += FC / (1 + r) ** t
VPN -= I0

st.subheader("Valor Presente Neto (VPN)")
st.write(f"VPN = ${VPN:,.2f}")

# Gráfico VPN vs tasa de interés
r_values = np.linspace(0.05, 0.15, 50)
VPN_values = []

for rv in r_values:
    vpn_temp = 0
    for t in range(1, n + 1):
        FC = FC_base * (1 - i) / e
        vpn_temp += FC / (1 + rv) ** t
    vpn_temp -= I0
    VPN_values.append(vpn_temp)

plt.figure()
plt.plot(r_values * 100, VPN_values)
plt.xlabel("Tasa de interés (%)")
plt.ylabel("VPN")
plt.title("VPN vs Tasa de interés")
st.pyplot(plt)'''



import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ==============================================================================
# 1. FUNCIÓN DE CÁLCULO DEL VPN (Valor Presente Neto)
# ==============================================================================

def calcular_vpn(r, i, e, n=3, FC_base=3000, IO=10000):
    """
    Calcula el VPN dadas las variables financieras.
    r: Tasa de interés (Tasa de descuento)
    i: Inflación
    e: Tipo de cambio (factor)
    n: Número de períodos
    FC_base: Flujo de caja base
    IO: Inversión inicial
    """
    vpn = -IO
    
    # El flujo de caja es afectado por la Inflación y el Tipo de Cambio
    # (Asumiendo que el FC base está en moneda local y se ajusta por estas variaciones)
    FC_neto = FC_base * (1 - i) / e
    
    # Sumatoria de valores presentes de los flujos de caja futuros
    t = np.arange(1, n + 1)
    
    # La parte vectorial: calcula todos los valores presentes a la vez
    vpn += np.sum(FC_neto / (1 + r)**t)
    return vpn

# ==============================================================================
# 2. CONFIGURACIÓN Y SLIDERS INTERACTIVOS
# ==============================================================================

st.title("Dashboard de Análisis de Sensibilidad del VPN")

st.sidebar.header("Variables Financieras")

# Sliders (Variables que el usuario controla)
r = st.sidebar.slider("Tasa de interés (%)", 5.0, 15.0, 8.0) / 100
i = st.sidebar.slider("Inflación (%)", 0.0, 10.0, 4.0) / 100
e = st.sidebar.slider("Tipo de cambio (factor)", 1.0, 1.5, 1.1)

# Parámetros del proyecto (Fijos)
IO = 10000
FC_base = 3000
n = 3

st.write(f"### Parámetros Fijos: Inversión Inicial={IO}, Flujo Base={FC_base}, Periodos={n}")

# Cálculo y muestra del VPN en el escenario actual
vpn_actual = calcular_vpn(r, i, e, n, FC_base, IO)
st.metric(label="VPN (Valor Presente Neto) Actual", value=f"${vpn_actual:,.2f}")

# ==============================================================================
# 3. GRÁFICO DE LÍNEA: VPN vs. TASA DE INTERÉS (Sensibilidad Simple)
# ==============================================================================

st.header("1. Sensibilidad del VPN vs. Tasa de Interés")
st.markdown("_(Manteniendo la Inflación y el Tipo de Cambio fijos)_")

# Rango de prueba para la Tasa de Interés
r_test = np.linspace(0.01, 0.20, 50) 
# Calculamos el VPN para cada punto de prueba, usando los valores fijos de los sliders
vpn_line = [calcular_vpn(val_r, i, e, n, FC_base, IO) for val_r in r_test]

fig_line, ax_line = plt.subplots(figsize=(8, 4))
ax_line.plot(r_test * 100, vpn_line, label="VPN")
ax_line.axhline(0, color='red', linestyle='--', label="VPN = 0 (TIR)") # Línea del VPN=0
ax_line.scatter(r * 100, vpn_actual, color='green', s=100, label="VPN Actual") # Punto actual
ax_line.set_xlabel("Tasa de Interés (%)")
ax_line.set_ylabel("VPN ($)")
ax_line.set_title("VPN vs. Tasa de Interés (Con r={}, i={}, e={})".format(r, i, e))
ax_line.grid(True, linestyle=':', alpha=0.6)
ax_line.legend()
st.pyplot(fig_line)

# ==============================================================================
# 4. GRÁFICO DE SUPERFICIE 3D: VARIACIONES SIMULTÁNEAS
# ==============================================================================

st.header("2. Análisis de Superficie 3D (r vs i)")
st.markdown("_(Muestra la sensibilidad del VPN variando la Tasa de Interés y la Inflación al mismo tiempo)_")

# --- 4a. Generar la Malla de Datos ---
r_range = np.linspace(0.01, 0.20, 50)  # Tasa de interés (1% a 20%)
i_range = np.linspace(0.00, 0.10, 50)  # Inflación (0% a 10%)

# Crea una cuadrícula de todas las combinaciones posibles de r e i
R, I = np.meshgrid(r_range, i_range)

# Calcular el VPN para cada punto de la malla, manteniendo 'e' fijo (del slider)
VPN_surface = np.array([
    [calcular_vpn(R[m, l], I[m, l], e) for l in range(R.shape[1])]
    for m in range(R.shape[0])
])

# --- 4b. Construir el Gráfico con Plotly ---
fig_3d = go.Figure(data=[
    go.Surface(
        z=VPN_surface,
        x=r_range * 100, # Convertir a % para la etiqueta
        y=i_range * 100, # Convertir a % para la etiqueta
        colorscale='RdYlGn' # Esquema de color: Rojo (VPN bajo) a Verde (VPN alto)
    )
])

# Configuración y Títulos del gráfico 3D
fig_3d.update_layout(
    title=f'Sensibilidad del VPN (Tipo de Cambio fijo en {e:.2f})',
    scene=dict(
        xaxis_title='Tasa de Interés (%)',
        yaxis_title='Inflación (%)',
        zaxis_title='VPN ($)'
    ),
    autosize=True,
    width=700,
    height=700,
    scene_camera=dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.25, y=1.25, z=1.25) # Vista inicial
    )
)

st.plotly_chart(fig_3d)

st.markdown("""
### Cómo interpretar el Gráfico 3D:
* **Superficie alta (Verde):** Indica escenarios donde el VPN es más alto (proyecto rentable).
* **Superficie baja (Rojo):** Indica escenarios donde el VPN es más bajo, incluso negativo (proyecto no rentable).
* **Interacción:** Puedes ver que el VPN cae drásticamente cuando la Tasa de Interés es alta (moviéndose hacia la derecha) o la Inflación es alta (moviéndose hacia arriba).
""")