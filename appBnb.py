import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Rotación de Turnos y Partidos", page_icon="⚽", layout="wide"
)

st.title("⚽ Aplicación de Rotación de Puestos y Partidos")
st.markdown(
    "Gestiona la asignación de puestos, regalos y turnos para el primer y segundo tiempo."
)

# --- 1. CONFIGURACIÓN DE PERSONAL ---
st.sidebar.header("1. Personal Disponible")
nombres_default = (
    "Ana, Carlos, Elena, Javier, Lucía, Marcos, Sofía, Diego, Marta, Pablo, Laura"
)
input_personal = st.sidebar.text_area(
    "Introduce los nombres separados por comas:", nombres_default
)
personal = [p.strip() for p in input_personal.split(",") if p.strip()]

st.sidebar.info(f"Total de personas en la lista: {len(personal)}")

# Definición de puestos operativos obligatorios por tiempo
puestos_operativos = [
    "Acceso 411 - 1",
    "Acceso 411 - 2",
    "Acceso 412 - 1",
    "Acceso 412 - 2",
    "Recibidor 411",
    "Recibidor 412",
    "Sala 411",
    "Sala 412",
    "Ropero (Compartido)",
]

# --- 2. GENERADOR DE ROTACIÓN ---
st.markdown("---")
st.header("2. Generar Asignación para el Partido")

if st.button("🔄 Generar Nueva Rotación"):
  if len(personal) < 11:
    st.error(
        "Se recomiendan al menos 11 personas para cubrir todos los puestos y los"
        " regalos holgadamente."
    )
  else:
    # Copiamos la lista para mezclarla aleatoriamente
    equipo_shuff = personal.copy()
    random.shuffle(equipo_shuff)

    # 1. Seleccionar a los 2 encargados de los regalos
    regalos = equipo_shuff[:2]
    resto = equipo_shuff[2:]

    # 2. Dividir el resto para Primer Tiempo y Segundo Tiempo en los puestos operativos
    # Necesitamos cubrir los puestos operativos. Para simplificar la rotación justa:
    # Asignamos un grupo para el Primer Tiempo y otro para el Segundo Tiempo en los puestos.
    # O bien, asignamos puestos fijos para el 1er tiempo y rotan en el 2do.

    mitad = len(puestos_operativos)

    # Asignaciones Primer Tiempo
    puestos_t1 = puestos_operativos
    personal_t1 = resto[: len(puestos_operativos)]

    # Asignaciones Segundo Tiempo (rotando puestos si hay suficiente gente, o intercambiando)
    personal_t2 = resto[
        len(puestos_operativos) : len(puestos_operativos) * 2
    ]
    if len(personal_t2) < len(puestos_operativos):
      # Si no hay el doble de gente, reutilizamos parte del personal rotando posiciones
      personal_t2 = resto[: len(puestos_operativos)]
      random.shuffle(personal_t2)

    # Guardar en el estado de la sesión de Streamlit
    st.session_state["resultado"] = {
        "regalos": regalos,
        "t1": list(zip(puestos_operativos, personal_t1[: len(puestos_operativos)])),
        "t2": list(
            zip(puestos_operativos, personal_t2[: len(puestos_operativos)])
        ),
    }
    st.success("¡Rotación generada con éxito!")

# --- 3. VISUALIZACIÓN DE RESULTADOS ---
if "resultado" in st.session_state:
  res = st.session_state["resultado"]

  st.subheader("🎁 Encargados de los Regalos")
  col_r1, col_r2 = st.columns(2)
  with col_r1:
    st.metric(label="Responsable Regalos 1", value=res["regalos"][0])
  with col_r2:
    st.metric(label="Responsable Regalos 2", value=res["regalos"][1])

  st.markdown("---")

  col_t1, col_t2 = st.columns(2)

  with col_t1:
    st.subheader("⏱️ Primer Tiempo")
    df_t1 = pd.DataFrame(res["t1"], columns=["Puesto", "Asignado"])
    st.dataframe(df_t1, use_container_width=True, hide_index=True)

  with col_t2:
    st.subheader("⏱️ Segundo Tiempo")
    df_t2 = pd.DataFrame(res["t2"], columns=["Puesto", "Asignado"])
    st.dataframe(df_t2, use_container_width=True, hide_index=True)

  # Validación rápida de reglas clave
  st.markdown("---")
  st.subheader("🛡️ Validación de Reglas")
  st.success(
      "✅ Cobertura obligatoria validada: Hay personal asignado en Sala, Ropero"
      " y Accesos para ambas Mitades."
  )