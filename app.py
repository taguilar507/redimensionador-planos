import streamlit as st
import img2pdf
from pdf2image import convert_from_path
from PIL import Image
from pypdf import PdfReader
import io
import os

Image.MAX_IMAGE_PIXELS = None

# Configuración estética de la interfaz web
st.set_page_config(page_title="Estandarizador de Planos 9000px", page_icon="📐", layout="centered")

st.title("📐 Redimensionador de Planos Pro")
st.write("Sube tus archivos PDF para normalizarlos automáticamente a **9000px de ancho** manteniendo la proporción.")

# Ajustes fijos del sistema para la nube
ANCHO_OBJETIVO = 9000
DPI_ESTANDAR = 300

# Componente web para arrastrar y soltar archivos
archivos_subidos = st.file_uploader("Arrastra tus planos aquí (Formatos .PDF)", type=["pdf"], accept_multiple_files=True)

if archivos_subidos:
    for archivo in archivos_subidos:
        nombre_sin_ext, ext = os.path.splitext(archivo.name)
        nuevo_nombre = f"{nombre_sin_ext.upper()}{ext.upper()}"
        
        st.markdown(f"---")
        st.subheader(f"🔄 Procesando: {nombre_sin_ext}")
        barra_progreso = st.progress(0)
        
        try:
            # Leer el archivo en la memoria del servidor
            pdf_bytes = archivo.read()
            
            # Lectura de vectores para evitar desbordamientos numéricos
            reader = PdfReader(io.BytesIO(pdf_bytes))
            paginas_imagenes = convert_from_path(pdf_bytes, dpi=DPI_ESTANDAR, poppler_path=None)
            
            imagenes_procesadas_bytes = []
            foto_testigo = None
            total_paginas = len(paginas_imagenes)
            
            for i, pagina in enumerate(paginas_imagenes):
                num_pagina = i + 1
                
                # Extraer dimensiones reales en puntos
                caja_pdf = reader.pages[i].mediabox
                ancho_calculado_px = int(float(caja_pdf.width) * (DPI_ESTANDAR / 72))
                alto_calculado_px = int(float(caja_pdf.height) * (DPI_ESTANDAR / 72))
                
                proporcion = alto_calculado_px / ancho_calculado_px
                alto_nuevo = int(ANCHO_OBJETIVO * proporcion)
                
                # Redimensionar la página con alta nitidez (Lanczos)
                imagen_final = pagina.resize((ANCHO_OBJETIVO, alto_nuevo), Image.Resampling.LANCZOS)
                
                # Guardar temporalmente en memoria interna
                img_byte_arr = io.BytesIO()
                imagen_final.save(img_byte_arr, format='JPEG', quality=90)
                imagenes_procesadas_bytes.append(img_byte_arr.getvalue())
                
                # Capturar la página 1 para el muestreo visual
                if num_pagina == 1:
                    foto_testigo = imagen_final
                
                barra_progreso.progress(int((num_pagina / total_paginas) * 100))
            
            # Unir todas las páginas procesadas en el PDF definitivo
            pdf_resultado = img2pdf.convert(imagenes_procesadas_bytes)
            
            st.success(f"✅ ¡{nuevo_nombre} listo para descargar!")
            
            # --- DISEÑO DEL CONTENEDOR DE VALIDACIÓN Y DESCARGAS ---
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.write("📸 **Muestra de Validación:**")
                st.image(foto_testigo, caption="Primera página a 9000px", use_container_width=True)
            
            with col2:
                st.write("📥 **Descargas Disponibles:**")
                
                # BOTÓN 1: PDF FINAL (Obligatorio)
                st.download_button(
                    label="⬇️ Descargar PDF Optimizado",
                    data=pdf_resultado,
                    file_name=nuevo_nombre,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.write("") # Espaciador
                
                # BOTÓN 2: JPG TESTIGO (Opcional a discreción)
                img_testigo_bytes = io.BytesIO()
                foto_testigo.save(img_testigo_bytes, format='JPEG', quality=95)
                
                st.download_button(
                    label="🖼️ Descargar Foto Testigo (JPG)",
                    data=img_testigo_bytes.getvalue(),
                    file_name=f"{nombre_sin_ext.upper()}_PAG_1.JPG",
                    mime="image/jpeg",
                    use_container_width=True
                )
                st.caption("💡 Opcional: descarga esta imagen para comprobar los 9000px en Paint.")
                
        except Exception as e:
            st.error(f"❌ Error al procesar este archivo: {e}")
