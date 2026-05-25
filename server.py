from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import base64
from io import BytesIO
import traceback
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generar", methods=["POST"])
def generar():

    try:

        data = request.json
        hojas = data.get("hojas", [])
        nombre = data.get("nombre", "RIJ_CFE")

        plantilla_path = os.path.join(
            os.path.dirname(__file__),
            "plantilla.pdf"
        )

        pdf_writer = PdfWriter()

        width, height = letter

        for hoja in hojas:

            packet = BytesIO()

            c = canvas.Canvas(packet, pagesize=letter)

            fotos = hoja

            # =========================
            # UNA FOTO
            # =========================
            if len(fotos) == 1:

                img = ImageReader(
                    BytesIO(
                        base64.b64decode(
                            fotos[0].split(",")[1]
                        )
                    )
                )

                iw, ih = img.getSize()

                # MÁRGENES
                margin_x = 35
                margin_top = 145
                margin_bottom = 45

                usable_w = width - (margin_x * 2)
                usable_h = height - margin_top - margin_bottom

                scale = min(
                    usable_w / iw,
                    usable_h / ih
                )

                new_w = iw * scale
                new_h = ih * scale

                x = (width - new_w) / 2

                y = (
                    margin_bottom +
                    (usable_h - new_h) / 2
                )

                c.drawImage(
                    img,
                    x,
                    y,
                    new_w,
                    new_h,
                    preserveAspectRatio=True
                )

            # =========================
            # VARIAS FOTOS
            # =========================
            else:

                total = len(fotos)

                if total <= 4:
                    cols = 2
                elif total <= 9:
                    cols = 3
                else:
                    cols = 4

                rows = (total + cols - 1) // cols

                margin_x = 45
                margin_top = 155
                margin_bottom = 60
                gap = 10

                usable_w = width - (margin_x * 2)
                usable_h = height - margin_top - margin_bottom

                img_w = (
                    usable_w - (gap * (cols - 1))
                ) / cols

                img_h = (
                    usable_h - (gap * (rows - 1))
                ) / rows

                x0 = margin_x
                y0 = height - margin_top - img_h

                x = x0
                y = y0

                for j, foto in enumerate(fotos):

                    img = ImageReader(
                        BytesIO(
                            base64.b64decode(
                                foto.split(",")[1]
                            )
                        )
                    )

                    iw, ih = img.getSize()

                    scale = min(
                        img_w / iw,
                        img_h / ih
                    )

                    final_w = iw * scale
                    final_h = ih * scale

                    pos_x = x + (img_w - final_w) / 2
                    pos_y = y + (img_h - final_h) / 2

                    c.drawImage(
                        img,
                        pos_x,
                        pos_y,
                        final_w,
                        final_h,
                        preserveAspectRatio=True
                    )

                    if (j + 1) % cols == 0:
                        x = x0
                        y -= img_h + gap
                    else:
                        x += img_w + gap

            c.save()

            packet.seek(0)

            overlay_pdf = PdfReader(packet)

            plantilla = PdfReader(plantilla_path)

            base_page = plantilla.pages[0]

            base_page.merge_page(
                overlay_pdf.pages[0]
            )

            pdf_writer.add_page(base_page)

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
        return "Error", 500


if __name__ == "__main__":
    app.run(debug=True)