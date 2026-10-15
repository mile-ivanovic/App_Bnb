import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Rotación de Turnos y Partidos", page_icon="⚽", layout="wide"
)

st.title("⚽ Aplicación de Rotación de Puestos y Partidos")
st.markdown(
    "Gestión exacta para 10 puestos y 10 personas con alternancia de descanso y"
    " asignación aleatoria de regalos."
)

# --- 1. CONFIGURACIÓN DE PERSONAL (Exactamente 10 personas) ---
st.sidebar.header("1. Personal de Puestos (10 personas)")
nombres_default = (
    "Ana, Carlos, Elena, Javier, Lucía, Marcos, Sofía, Diego, Marta, Pablo"
)
input_personal = st.sidebar.text_area(
    "Introduce los 10 nombres separados por comas:", nombres_default
)
personal = [p.strip() for p in input_personal.split(",") if p.strip()]

# Los 10 puestos fijos exactos (incluyendo Ropero 2)
puestos = [
    "Accesos 411 - 1",
    "Accesos 411 - 2",
    "Sala 411",
    "Recibidor 411",
    "Ropero",
    "Ropero 2",
    "Accesos 412 - 1",
    "Accesos 412 - 2",
    "Sala 412",
    "Recibidor 412",
]

# Puestos que van de verde (viendo el partido) en cada mitad
# Primer tiempo: Ropero 2 está ausente de esta lista, por lo que sale en ROJO (trabajando)
puestos_verdes_t1 = [
    "Accesos 411 - 1",
    "Accesos 412 - 1",
    "Ropero",
    "Sala 411",
    "Recibidor 412",
]
# Segundo tiempo: Ropero 2 está incluido aquí, por lo que sale en VERDE (viendo el partido)
puestos_verdes_t2 = [
    "Accesos 411 - 2",
    "Accesos 412 - 2",
    "Recibidor 411",
    "Sala 412",
    "Ropero 2",
]

# Inicializar índice de rotación general entre partidos
if "indice_rotacion" not in st.session_state:
  st.session_state["indice_rotacion"] = 0

# --- 2. GENERADOR DE ROTACIÓN ---
st.markdown("---")
st.header("2. Generar Asignación para el Partido")

if st.button("🔄 Rotar Puestos y Partido"):
  if len(personal) != 10:
    st.error(
        f"Has introducido {len(personal)} personas. Deben ser exactamente 10"
        " para los 10 puestos."
    )
  else:
    # 1. Seleccionar dos personas al azar para los regalos
    regaladores = random.sample(personal, 2)

    # 2. Rotar el orden general del equipo según el histórico de partidos
    shift = st.session_state["indice_rotacion"] % len(personal)
    equipo = personal[shift:] + personal[:shift]

    # Dividimos al equipo en dos grupos de 5:
    # - Grupo Verde T1 (5 personas): Estarán en verde en el T1 y pasarán a rojo (trabajo) en el T2.
    # - Grupo Rojo T1 (5 personas): Estarán en rojo (trabajo) en el T1 y pasarán a verde en el T2.
    grupo_verde_t1 = equipo[:5]
    grupo_rojo_t1 = equipo[5:]

    t1_rows = []
    t2_rows = []

    # --- PRIMER TIEMPO ---
    idx_v1 = 0
    idx_r1 = 0
    for puesto in puestos:
      if puesto in puestos_verdes_t1:
        persona = grupo_verde_t1[idx_v1]
        estado = "Viendo"
        idx_v1 += 1
      else:
        persona = grupo_rojo_t1[idx_r1]
        estado = "Trabajando"
        idx_r1 += 1
      t1_rows.append({"Puesto": puesto, "Persona": persona, "Estado": estado})

    # --- SEGUNDO TIEMPO ---
    puestos_t2_ordenados = puestos[5:] + puestos[:5]
    idx_r1_t2 = 0
    idx_v1_t2 = 0

    temp_t2 = []
    for puesto in puestos_t2_ordenados:
      if puesto in puestos_verdes_t2:
        persona = grupo_rojo_t1[idx_r1_t2]
        estado = "Viendo"
        idx_r1_t2 += 1
      else:
        persona = grupo_verde_t1[idx_v1_t2]
        estado = "Trabajando"
        idx_v1_t2 += 1
      temp_t2.append({"Puesto": puesto, "Persona": persona, "Estado": estado})

    t2_rows = sorted(temp_t2, key=lambda x: puestos.index(x["Puesto"]))

    # Guardar en sesión
    st.session_state["resultado"] = {
        "regalos": regaladores,
        "t1": t1_rows,
        "t2": t2_rows,
    }
    st.session_state["indice_rotacion"] += 1
    st.success("¡Rotación y selección de regalos generadas con éxito!")


# --- FUNCIÓN DE ESTILO PARA COLORES (Oculta la columna de control) ---
def destacar_estado(row):
  if row["Estado"] == "Viendo":
    return [
        "background-color: #d4edda; color: #155724; font-weight: bold;"
    ] * len(row)  # Verde para partido
  else:
    return [
        "background-color: #ffcccc; color: #990000; font-weight: bold;"
    ] * len(row)  # Rojo para trabajando


# --- 3. VISUALIZACIÓN DE RESULTADOS ---
if "resultado" in st.session_state:
  res = st.session_state["resultado"]

  # Mostrar encargados de los regalos
  st.subheader("🎁 Encargados de los Regalos")
  st.info(
      f"**{res['regalos'][0]}** y **{res['regalos'][1]}** son los encargados de"
      " llevar los regalos en este partido."
  )

  st.markdown("---")

  col_t1, col_t2 = st.columns(2)

  with col_t1:
    st.subheader("⏱️ Primer Tiempo")
    df_t1 = pd.DataFrame(res["t1"])
    df_t1_styled = (
        df_t1.style.apply(destacar_estado, axis=1)
        .hide(subset=["Estado"], axis="columns")
    )
    st.dataframe(df_t1_styled, use_container_width=True, hide_index=True)

  with col_t2:
    st.subheader("⏱️ Segundo Tiempo")
    df_t2 = pd.DataFrame(res["t2"])
    df_t2_styled = (
        df_t2.style.apply(destacar_estado, axis=1)
        .hide(subset=["Estado"], axis="columns")
    )
    st.dataframe(df_t2_styled, use_container_width=True, hide_index=True)

  st.markdown(
      "*Nota: Las filas en **verde** muestran a quienes ven el partido. Quien"
      " está en rojo en el primer tiempo pasa a verde en el segundo, y"
      " viceversa, cambiando de puesto sin repetir.*"
  )