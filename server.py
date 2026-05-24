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

        fotos = data.get("fotos", [])
        nombre = data.get("nombre", "RIJ_CFE")

        print("📌 TOTAL FOTOS:", len(fotos))

        if not fotos:
            return "No hay fotos", 400

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        width, height = letter

        img_width = 380
        img_height = 260

        total = len(fotos)

        # =========================
        # 📄 PAGINAS DE FOTOS
        # =========================
        for i, foto in enumerate(fotos):

            # fondo blanco
            c.setFillColorRGB(1, 1, 1)
            c.rect(0, 0, width, height, fill=1)

            # encabezado verde CFE
            c.setFillColorRGB(0, 0.5, 0.2)
            c.rect(0, height-80, width, 80, fill=1)

            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, height-40, "COMISIÓN FEDERAL DE ELECTRICIDAD (CFE)")
            c.setFont("Helvetica", 11)
            c.drawString(30, height-60, "REUNIÓN DE INICIO DE JORNADA - RIJ")

            # numeración
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(520, height-40, f"{i+1}/{total}")

            # =========================
            # 📸 IMAGEN CENTRADA
            # =========================
            try:
                if foto and "," in foto:

                    img_data = base64.b64decode(foto.split(",")[1])
                    img = ImageReader(BytesIO(img_data))

                    x = (width - img_width) / 2
                    y = (height - img_height) / 2

                    c.drawImage(img, x, y, width=img_width, height=img_height)

            except Exception as e:
                print("❌ Error imagen:", e)

            # pie de página
            c.setFont("Helvetica", 9)
            c.drawString(30, 50, f"Página {i+1} de {total} - RIJ Sistema")

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
        print("🔥 ERROR REAL:")
        traceback.print_exc()
        return str(e), 500


if __name__ == "__main__":
    app.run(debug=True)