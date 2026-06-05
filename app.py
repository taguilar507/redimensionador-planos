import streamlit as st
import img2pdf
from pdf2image import convert_from_path
from PIL import Image
from pypdf import PdfReader
import io
import os

Image.MAX_IMAGE_PIXELS = None

# Interfaz limpia y estética
st.set_page_config(page_title="Estandarizador de Planos 9000px", page_icon="📐", layout="centered")

st.title("📐 Redimensionador de Planos Pro")
st.write("Sube tus archivos PDF para normalizarlos automáticamente a **9000px de ancho** manteniendo la proporción.")

ANCHO_OBJETIVO = 9000
DPI_ESTANDAR = 300

archivos_subidos = st.file_uploader("Arrastra tus planos aquí (Formatos .PDF)", type=["pdf"], accept_multiple_files=True)

if archivos_subidos:
    for archivo in archivos_subidos:
        nombre_sin_ext, ext = os.path.splitext(archivo.name)
        nuevo_nombre = f"{nombre_sin_ext.upper()}{ext.upper()}"
        
        st.markdown("---")
        st.subheader(f"🔄 Procesando: {nombre_sin_ext}")
        barra_progreso = st.progress(0)
        
        try:
            pdf_bytes = archivo.read()
            
            # Lectura limpia de vectores para evitar el error de 1px
            reader = PdfReader(io.BytesIO(pdf_bytes))
            paginas_imagenes = convert_from_path(pdf_bytes, dpi=DPI_ESTANDAR, poppler_path=None)
            
            imagenes_procesadas_bytes = []
            foto_testigo = None
            total_paginas = len(paginas_imagenes)
            
            for i, pagina in enumerate(paginas_imagenes):
                num_pagina = i + 1
                
                caja_pdf = reader.pages[i].mediabox
                ancho_calculado_px = int(float(caja_pdf.width) * (DPI_ESTANDAR / 72))
                alto_calculado_px = int(float(caja_pdf.height) * (DPI_ESTANDAR / 72))
                
                proporcion = alto_calculado_px / ancho_calculado_px
                alto_nuevo = int(ANCHO_OBJETIVO * proporcion)
                
                imagen_final = pagina.resize((ANCHO_OBJETIVO, alto_nuevo), Image.Resampling.LANCZOS)
                
                img_byte_arr = io.BytesIO()
                imagen_final.save(img_byte_arr, format='JPEG', quality=90)
                imagenes_procesadas_bytes.append(img_byte_arr.getvalue())
                
                if num_pagina == 1:
                    foto_testigo = imagen_final
                
                barra_progreso.progress(int((num_pagina / total_paginas) * 100))
            
            pdf_resultado = img2pdf.convert(imagenes_procesadas_bytes)
            
            st.success(f"✅ ¡{nuevo_nombre} listo para descargar!")
            
            col1, col2 = st.columns([1, 1.2])
            with col1:
                st.write("📸 **Muestra de Validación:**")
                st.image(foto_testigo, caption="Primera página a 9000px", use_container_width=True)
            with col2:
                st.write("📥 **Descargas Disponibles:**")
                st.download_button(
                    label="⬇️ Descargar PDF Optimizado",
                    data=pdf_resultado,
                    file_name=nuevo_nombre,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.write("") 
                
                img_testigo_bytes = io.BytesIO()
                foto_testigo.save(img_testigo_bytes, format='JPEG', quality=95)
                st.download_button(
                    label="🖼️ Descargar Foto Testigo (JPG)",
                    data=img_testigo_bytes.getvalue(),
                    file_name=f"{nombre_sin_ext.upper()}_PAG_1.JPG",
                    mime="image/jpeg",
                    use_container_width=True
                )
                st.caption("💡 Comprueba los 9000px en Paint.")
                
        except Exception as e:
            st.error(f"❌ Error al procesar este archivo: {str(e)}")
