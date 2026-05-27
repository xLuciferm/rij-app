from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageOps
from io import BytesIO
import base64
import traceback
import os

app = Flask(__name__)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# BASE64 -> IMAGE
# =========================
def procesar_base64(img_base64):

    img_data = base64.b64decode(img_base64.split(",")[1])

    img = Image.open(BytesIO(img_data))
    img = ImageOps.exif_transpose(img)

    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    img.thumbnail((1500, 1500))

    output = BytesIO()
    img.save(output, format="JPEG", quality=55, optimize=True)
    output.seek(0)

    return ImageReader(output)


# =========================
# GENERAR PDF
# =========================
@app.route("/generar", methods=["POST"])
def generar():

    try:

        data = request.get_json()

        if not data or "hojas" not in data:
            return "No data received", 400

        nombre = data.get("nombre", "RIJ_CFE")
        hojas = data["hojas"]

        pdf_writer = PdfWriter()
        width, height = letter

        plantilla_path = os.path.join(
            os.path.dirname(__file__),
            "plantilla.pdf"
        )

        # =========================
        # HOJAS
        # =========================
        for fotos in hojas:

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            # ==================================================
            # 🔥 CASO 1: SOLO UNA IMAGEN (CENTRADA SEGURA)
            # ==================================================
            if len(fotos) == 1:

                img = procesar_base64(fotos[0])
                iw, ih = img.getSize()

                # 🔥 ÁREA REAL DE TU PLANTILLA (ajustada visualmente)
                margin_x = 50
                margin_top = 140   # evita encabezado
                margin_bottom = 100  # evita footer

                usable_w = width - (margin_x * 2)
                usable_h = height - margin_top - margin_bottom

                # 🔥 escala segura dentro del área real
                scale = min(usable_w / iw, usable_h / ih)

                w = iw * scale
                h = ih * scale

                # 🔥 centrado dentro del área útil (NO toda la hoja)
                x = margin_x + (usable_w - w) / 2
                y = margin_bottom + (usable_h - h) / 2

                c.drawImage(
                    img,
                    x,
                    y,
                    w,
                    h,
                    preserveAspectRatio=True,
                    mask='auto'
                )

            # ==================================================
            # 🔥 CASO 2: VARIAS IMÁGENES
            # ==================================================
            else:

                cols = 2 if len(fotos) <= 8 else 3

                margin_x = 45
                margin_top = 140
                margin_bottom = 60
                gap = 10

                usable_w = width - (margin_x * 2)
                usable_h = height - margin_top - margin_bottom

                img_w = (usable_w - (cols - 1) * gap) / cols
                rows = (len(fotos) + cols - 1) // cols
                img_h = (usable_h - (rows - 1) * gap) / rows

                x0 = margin_x
                y0 = height - margin_top - img_h

                x = x0
                y = y0

                for i, f in enumerate(fotos):

                    img = procesar_base64(f)
                    iw, ih = img.getSize()

                    scale = min(img_w / iw, img_h / ih)

                    w = iw * scale
                    h = ih * scale

                    c.drawImage(
                        img,
                        x + (img_w - w) / 2,
                        y + (img_h - h) / 2,
                        w,
                        h,
                        preserveAspectRatio=True,
                        mask='auto'
                    )

                    if (i + 1) % cols == 0:
                        x = x0
                        y -= (img_h + gap)
                    else:
                        x += (img_w + gap)

            c.save()

            packet.seek(0)

            overlay = PdfReader(packet)
            plantilla = PdfReader(plantilla_path)

            page = plantilla.pages[0]
            page.merge_page(overlay.pages[0])

            pdf_writer.add_page(page)

        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{nombre}.pdf"
        )

    except Exception:
        traceback.print_exc()
        return "Error al generar PDF", 500


if __name__ == "__main__":
    app.run(debug=True)