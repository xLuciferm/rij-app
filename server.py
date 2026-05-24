from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import base64
from io import BytesIO
import traceback

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

        if not hojas:
            return "No hay fotos", 400

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        width, height = letter
        total_hojas = len(hojas)

        for i, hoja in enumerate(hojas):

            # =========================
            # FONDO
            # =========================
            c.setFillColorRGB(1, 1, 1)
            c.rect(0, 0, width, height, fill=1)

            # =========================
            # HEADER
            # =========================
            header_h = 80

            c.setFillColorRGB(0, 0.5, 0.2)
            c.rect(0, height-header_h, width, header_h, fill=1)

            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, height-40, "COMISIÓN FEDERAL DE ELECTRICIDAD (CFE)")
            c.setFont("Helvetica", 11)
            c.drawString(30, height-60, "REUNIÓN DE INICIO DE JORNADA - RIJ")

            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(520, height-40, f"{i+1}/{total_hojas}")

            total_imgs = len(hoja)

            # ======================================================
            # 📌 UNA IMAGEN (más grande + mejor proporción)
            # ======================================================
            if total_imgs == 1:

                foto = hoja[0]

                if foto and "," in foto:

                    img_data = base64.b64decode(foto.split(",")[1])
                    img = ImageReader(BytesIO(img_data))

                    margin_x = 40
                    margin_bottom = 70
                    margin_top = header_h + 10

                    max_w = width - (margin_x * 2)
                    max_h = height - margin_top - margin_bottom

                    iw, ih = img.getSize()

                    scale = min(max_w / iw, max_h / ih)

                    img_w = iw * scale
                    img_h = ih * scale

                    x = (width - img_w) / 2
                    y = (height - margin_top - img_h) / 2 + 10  # 👈 un poco más arriba

                    c.drawImage(img, x, y, width=img_w, height=img_h)

            # ======================================================
            # 📌 VARIAS IMÁGENES (MEJOR DISTRIBUIDO + MÁS ARRIBA)
            # ======================================================
            else:

                total_imgs = len(hoja)

                # columnas más estables
                if total_imgs <= 4:
                    cols = 2
                else:
                    cols = 3

                gap = 12

                # tamaños MÁS PROPORCIONALES (menos “cuadro aplastado”)
                if total_imgs <= 4:
                    img_w, img_h = 250, 190
                elif total_imgs <= 6:
                    img_w, img_h = 210, 160
                else:
                    img_w, img_h = 190, 140

                rows = (total_imgs + cols - 1) // cols

                grid_width = cols * img_w + (cols - 1) * gap
                grid_height = rows * img_h + (rows - 1) * gap

                header_space = header_h + 15
                footer_space = 50

                max_height = height - header_space - footer_space

                # SOLO ajusta si se pasa
                if grid_height > max_height:
                    scale = max_height / grid_height
                    img_w *= scale
                    img_h *= scale

                    grid_width = cols * img_w + (cols - 1) * gap
                    grid_height = rows * img_h + (rows - 1) * gap

                # =========================
                # 🔥 AJUSTE IMPORTANTE (SUBIR GRID)
                # =========================
                start_x = (width - grid_width) / 2

                # 👇 más arriba que antes (menos centrado vertical)
                start_y = height - header_space - 20

                x = start_x
                y = start_y

                for j, foto in enumerate(hoja):

                    try:
                        if foto and "," in foto:

                            img_data = base64.b64decode(foto.split(",")[1])
                            img = ImageReader(BytesIO(img_data))

                            c.drawImage(
                                img,
                                x,
                                y - img_h,
                                width=img_w,
                                height=img_h
                            )

                            if (j + 1) % cols == 0:
                                x = start_x
                                y -= img_h + gap
                            else:
                                x += img_w + gap

                    except Exception as e:
                        print("❌ Error imagen:", e)

            # =========================
            # FOOTER
            # =========================
            c.setFont("Helvetica", 9)
            c.drawString(30, 50, f"Página {i+1} de {total_hojas} - RIJ Sistema")

            c.showPage()

        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nombre + ".pdf"
        )

    except Exception as e:
        print("🔥 ERROR:")
        traceback.print_exc()
        return str(e), 500


if __name__ == "__main__":
    app.run(debug=True)