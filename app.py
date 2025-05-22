import streamlit as st
import os
import json
import unicodedata

def limpiar_texto(texto):
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto.strip()

def cargar_historial(usuario):
    ruta = f"usuarios/{usuario}.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_historial(usuario, historial):
    os.makedirs("usuarios", exist_ok=True)
    with open(f"usuarios/{usuario}.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)

# --------------------------- INTERFAZ ---------------------------

st.markdown("""
    <h1 style='
        color: #b66459;
        font-family: "Monserrat", sans-serif;
        text-align: center;
        padding-bottom: 10px;
    '>Agenda Personal Bilingüe</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# --- LOGIN DE USUARIO ---
st.sidebar.header("Iniciar sesión")
usuario = st.sidebar.text_input("Nombre de usuario").strip().lower()

if usuario:
    st.success(f"Sesión iniciada como: {usuario}")
    historial = cargar_historial(usuario)

    opcion = st.radio("¿Qué querés hacer?", ["Buscar palabra", "Agregar nueva", "Modificar palabra"])
    st.markdown("---")

    if opcion == "Buscar palabra":
        palabra = st.text_input("Ingresá una palabra (en inglés o español):")

        # Búsqueda en vivo
        if palabra:
            palabra_limpia = limpiar_texto(palabra)
            sugerencias = [p for p in historial if palabra_limpia in p]
            if sugerencias:
                st.caption("Sugerencias:")
                for s in sugerencias:
                    st.write(f"• {s} → {historial[s]['traduccion']}")

            # Resultado exacto
            if palabra_limpia in historial:
                st.subheader(f"Resultado para: {palabra_limpia}")
                st.write(f"**Traducción:** {historial[palabra_limpia]['traduccion']}")
                st.write(f"**Descripción:** {historial[palabra_limpia]['descripcion']}")
                if 'categoria' in historial[palabra_limpia] and historial[palabra_limpia]['categoria']:
                    st.write(f"**Categoría:** {historial[palabra_limpia]['categoria']}")
            else:
                st.warning("Palabra no encontrada en tu historial.")
                if st.checkbox("¿Querés agregarla?"):
                    col1, col2 = st.columns(2)
                    with col1:
                        palabra_nueva = st.text_input("Palabra (en español o inglés)", value=palabra)
                    with col2:
                        traduccion = st.text_input("Traducción (en el otro idioma):")

                    descripcion = st.text_area("Descripción opcional:")
                    categoria = st.selectbox("Categoría:", ["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"])

                    if st.button("Guardar palabra"):
                        palabra_limpia = limpiar_texto(palabra_nueva)
                        historial[palabra_limpia] = {
                            "traduccion": limpiar_texto(traduccion),
                            "descripcion": descripcion.strip(),
                            "categoria": categoria
                        }
                        guardar_historial(usuario, historial)
                        st.success("Palabra agregada.")
                        st.rerun()

    elif opcion == "Agregar nueva":
        col1, col2 = st.columns(2)
        with col1:
            nueva = st.text_input("Nueva palabra:")
        with col2:
            traduccion = st.text_input("Traducción:")

        descripcion = st.text_area("Descripción:")
        categoria = st.selectbox("Categoría:", ["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"])

        if nueva:
            nueva_limpia = limpiar_texto(nueva)
            if nueva_limpia in historial:
                st.warning("Esa palabra ya existe.")
            elif st.button("Guardar"):
                historial[nueva_limpia] = {
                    "traduccion": limpiar_texto(traduccion),
                    "descripcion": descripcion.strip(),
                    "categoria": categoria
                }
                guardar_historial(usuario, historial)
                st.success("Palabra agregada.")
                st.rerun()

    elif opcion == "Modificar palabra":
        palabras = list(historial.keys())
        if palabras:
            seleccion = st.selectbox("Elegí la palabra a modificar:", palabras)

            col1, col2 = st.columns(2)
            with col1:
                nueva_palabra = st.text_input("Cambiar palabra:", seleccion)
            with col2:
                nueva_traduccion = st.text_input("Nueva traducción:", historial[seleccion]["traduccion"])

            nueva_descripcion = st.text_area("Nueva descripción:", historial[seleccion]["descripcion"])

            nueva_categoria = st.selectbox(
                "Categoría:",
                ["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"],
                index=["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"].index(
                    historial[seleccion].get("categoria", "")
                ) if historial[seleccion].get("categoria", "") in ["Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"] else 0
            )

            if st.button("Actualizar"):
                nueva_palabra_limpia = limpiar_texto(nueva_palabra)
                nueva_traduccion_limpia = limpiar_texto(nueva_traduccion)

                if nueva_palabra_limpia != seleccion:
                    historial.pop(seleccion)

                historial[nueva_palabra_limpia] = {
                    "traduccion": nueva_traduccion_limpia,
                    "descripcion": nueva_descripcion.strip(),
                    "categoria": nueva_categoria
                }

                guardar_historial(usuario, historial)
                st.success("Palabra actualizada.")
                st.rerun()
        else:
            st.info("Todavía no tenés palabras cargadas.")
else:
    st.warning("Ingresá tu nombre de usuario en el panel izquierdo para comenzar.")
