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
        color: #EB6E23;
        font-family: "Monserrat", sans-serif;
        text-align: center;
        padding-bottom: 10px;
    '>AGENDA PERSONAL DE IDIOMAS</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# --- LOGIN CON CORREO ---
st.sidebar.header("Iniciar sesión")
correo = st.sidebar.text_input("Ingresá tu correo electrónico").strip().lower()

if correo and "@" in correo and "." in correo:
    usuario = correo.replace("@", "_at_").replace(".", "_")
    st.success(f"Sesión iniciada como: {correo}")
    historial = cargar_historial(usuario)

    opcion = st.radio("¿Qué querés hacer?", [
        "Buscar palabra", "Agregar nueva", "Modificar palabra", "Ver historial completo"
    ])
    st.markdown("---")

    if opcion == "Buscar palabra":
        palabra = st.text_input("Ingresá una palabra (en cualquier idioma):")
        if palabra:
            palabra_limpia = limpiar_texto(palabra)
            sugerencias = [p for p in historial if palabra_limpia in p]
            if sugerencias:
                st.caption("Sugerencias:")
                for s in sugerencias:
                    st.write(f"• {s} → {historial[s]['traduccion']}")

            if palabra_limpia in historial:
                datos = historial[palabra_limpia]
                st.subheader(f"Resultado para: {palabra_limpia}")
                st.write(f"**Traducción:** {datos['traduccion']}")
                st.write(f"**Descripción:** {datos['descripcion']}")
                if datos.get("categoria"):
                    st.write(f"**Categoría:** {datos['categoria']}")
                if datos.get("idioma_origen") and datos.get("idioma_destino"):
                    st.write(f"**Idiomas:** {datos['idioma_origen']} → {datos['idioma_destino']}")
            else:
                st.warning("Palabra no encontrada en tu historial.")
                if st.checkbox("¿Querés agregarla?"):
                    idioma_origen = st.selectbox("Idioma de origen", ["Español", "Inglés", "Portugués"])
                    idioma_destino = st.selectbox("Idioma de destino", ["Español", "Inglés", "Portugués"])
                    col1, col2 = st.columns(2)
                    with col1:
                        palabra_nueva = st.text_input("Palabra:", value=palabra)
                    with col2:
                        traduccion = st.text_input("Traducción:")
                    descripcion = st.text_area("Descripción opcional:")
                    categoria = st.selectbox("Categoría:", ["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"])
                    if st.button("Guardar palabra"):
                        palabra_limpia = limpiar_texto(palabra_nueva)
                        traduccion_limpia = limpiar_texto(traduccion)
                        historial[palabra_limpia] = {
                            "traduccion": traduccion_limpia,
                            "descripcion": descripcion.strip(),
                            "categoria": categoria,
                            "idioma_origen": idioma_origen,
                            "idioma_destino": idioma_destino
                        }
                        if traduccion_limpia not in historial:
                            historial[traduccion_limpia] = {
                                "traduccion": palabra_limpia,
                                "descripcion": f"(Auto-generada de '{palabra_limpia}')",
                                "categoria": "Inversa",
                                "idioma_origen": idioma_destino,
                                "idioma_destino": idioma_origen
                            }
                        guardar_historial(usuario, historial)
                        st.success("Palabra agregada.")
                        st.rerun()

    elif opcion == "Agregar nueva":
        idioma_origen = st.selectbox("Idioma de origen", ["Español", "Inglés", "Portugués"])
        idioma_destino = st.selectbox("Idioma de destino", ["Español", "Inglés", "Portugués"])
        col1, col2 = st.columns(2)
        with col1:
            nueva = st.text_input("Nueva palabra:")
        with col2:
            traduccion = st.text_input("Traducción:")
        descripcion = st.text_area("Descripción:")
        categoria = st.selectbox("Categoría:", ["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"])
        if nueva:
            nueva_limpia = limpiar_texto(nueva)
            traduccion_limpia = limpiar_texto(traduccion)
            if nueva_limpia in historial:
                st.warning("Esa palabra ya existe.")
            elif st.button("Guardar"):
                historial[nueva_limpia] = {
                    "traduccion": traduccion_limpia,
                    "descripcion": descripcion.strip(),
                    "categoria": categoria,
                    "idioma_origen": idioma_origen,
                    "idioma_destino": idioma_destino
                }
                if traduccion_limpia not in historial:
                    historial[traduccion_limpia] = {
                        "traduccion": nueva_limpia,
                        "descripcion": f"(Auto-generada de '{nueva_limpia}')",
                        "categoria": "Inversa",
                        "idioma_origen": idioma_destino,
                        "idioma_destino": idioma_origen
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
            nueva_categoria = st.selectbox("Categoría:", ["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"],
                index=["", "Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"].index(
                    historial[seleccion].get("categoria", "")
                ) if historial[seleccion].get("categoria", "") in ["Sustantivo", "Verbo", "Adjetivo", "Frase", "Otro"] else 0)
            nuevo_idioma_origen = st.selectbox("Idioma de origen:", ["Español", "Inglés", "Portugués"],
                index=["Español", "Inglés", "Portugués"].index(historial[seleccion].get("idioma_origen", "Español")))
            nuevo_idioma_destino = st.selectbox("Idioma de destino:", ["Español", "Inglés", "Portugués"],
                index=["Español", "Inglés", "Portugués"].index(historial[seleccion].get("idioma_destino", "Inglés")))
            if st.button("Actualizar"):
                nueva_palabra_limpia = limpiar_texto(nueva_palabra)
                nueva_traduccion_limpia = limpiar_texto(nueva_traduccion)
                if nueva_palabra_limpia != seleccion:
                    historial.pop(seleccion)
                historial[nueva_palabra_limpia] = {
                    "traduccion": nueva_traduccion_limpia,
                    "descripcion": nueva_descripcion.strip(),
                    "categoria": nueva_categoria,
                    "idioma_origen": nuevo_idioma_origen,
                    "idioma_destino": nuevo_idioma_destino
                }
                guardar_historial(usuario, historial)
                st.success("Palabra actualizada.")
                st.rerun()
        else:
            st.info("Todavía no tenés palabras cargadas.")

    elif opcion == "Ver historial completo":
        st.subheader("Historial de palabras")
        filtro_origen = st.selectbox("Filtrar por idioma de origen:", ["Todos", "Español", "Inglés", "Portugués"])
        filtro_destino = st.selectbox("Filtrar por idioma de destino:", ["Todos", "Español", "Inglés", "Portugués"])
        if historial:
            encontrados = False
            for palabra, datos in historial.items():
                if filtro_origen != "Todos" and datos.get("idioma_origen") != filtro_origen:
                    continue
                if filtro_destino != "Todos" and datos.get("idioma_destino") != filtro_destino:
                    continue
                encontrados = True
                st.markdown(f"**Palabra:** {palabra}")
                st.markdown(f"- Traducción: {datos['traduccion']}")
                st.markdown(f"- Descripción: {datos['descripcion']}")
                if datos.get("categoria"):
                    st.markdown(f"- Categoría: {datos['categoria']}")
                if datos.get("idioma_origen") and datos.get("idioma_destino"):
                    st.markdown(f"- Idiomas: {datos['idioma_origen']} → {datos['idioma_destino']}")
                st.markdown("---")
            if not encontrados:
                st.info("No hay resultados que coincidan con los filtros.")
        else:
            st.info("Todavía no cargaste ninguna palabra.")

else:
    st.warning("Ingresá un correo electrónico válido para comenzar.")
