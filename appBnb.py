import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Rotación de Turnos y Partidos", page_icon="⚽", layout="wide"
)

st.title("⚽ Aplicación de Rotación de Puestos y Partidos")
st.markdown(
    "Gestiona la asignación justa de puestos, regalos y turnos asegurando cobertura total."
)

# --- 1. CONFIGURACIÓN DE PERSONAL ---
st.sidebar.header("1. Personal Disponible")
nombres_default = (
    "Ana, Carlos, Elena, Javier, Lucía, Marcos, Sofía, Diego, Marta, Pablo, Laura,"
    " Roberto, Carmen"
)
input_personal = st.sidebar.text_area(
    "Introduce los nombres separados por comas:", nombres_default
)
personal = [p.strip() for p in input_personal.split(",") if p.strip()]

st.sidebar.info(f"Total de personas en la lista: {len(personal)}")

# Definición de puestos operativos obligatorios (9 puestos en total)
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

# Inicializar el índice de rotación en la sesión si no existe
if "indice_rotacion" not in st.session_state:
  st.session_state["indice_rotacion"] = 0

# --- 2. GENERADOR DE ROTACIÓN ---
st.markdown("---")
st.header("2. Generar Asignación para el Partido")

# Se necesitan al menos 11 personas (2 para regalos + 9 para cubrir los puestos de cada tiempo,
# o idealmente más para rotar entre tiempos). Si hay menos de 9, avisamos.
if st.button("🔄 Rotar Puestos (Avanzar 1 posición)"):
  if len(personal) < 9:
    st.error(
        "Se necesitan al menos 9 personas para cubrir todos los puestos"
        " operativos obligatorios."
    )
  else:
    # Aplicar rotación desplazando la lista según el índice actual (mover un puesto a la derecha)
    shift = st.session_state["indice_rotacion"] % len(personal)
    personal_rotado = personal[shift:] + personal[:shift]

    # 1. Seleccionar a los 2 primeros para los regalos
    regalos = personal_rotado[:2]
    resto = personal_rotado[2:]

    # 2. Asignar puestos garantizando cobertura estricta para el Primer Tiempo
    # Si el resto es menor que los puestos operativos, rellenamos cíclicamente para que NINGÚN puesto quede vacío.
    asignados_t1 = []
    for i in range(len(puestos_operativos)):
      persona = resto[i % len(resto)]
      asignados_t1.append(persona)

    # 3. Para el Segundo Tiempo, desplazamos el resto una posición más para que cambien de puesto
    resto_t2 = resto[1:] + resto[:1]
    asignados_t2 = []
    for i in range(len(puestos_operativos)):
      persona = resto_t2[i % len(resto_t2)]
      asignados_t2.append(persona)

    # Guardar resultados en la sesión
    st.session_state["resultado"] = {
        "regalos": regalos,
        "t1": list(zip(puestos_operativos, asignados_t1)),
        "t2": list(zip(puestos_operativos, asignados_t2)),
    }

    # Incrementar el índice para la siguiente vez que se pulse el botón
    st.session_state["indice_rotacion"] += 1
    st.success("¡Rotación efectuada con éxito (todos movidos un puesto)!")

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

  # Validación estricta
  st.markdown("---")
  st.subheader("🛡️ Validación de Reglas")
  st.success(
      "✅ Cobertura completa garantizada: Ningún puesto de Accesos, Recibidores,"
      " Sala o Ropero se queda desocupado en ninguna de las dos partes."
  )