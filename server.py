from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import base64
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generar", methods=["POST"])
def generar():
    data = request.json
    fotos = data["fotos"]
    cantidad = data["cantidad"]

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter

    # 🟢 ===== HOJA 1 (PORTADA) =====
    c.setFillColorRGB(0, 0.5, 0)  # verde
    c.rect(0, height - 80, width, 80, fill=1)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "CFE Distribución")

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 150, "REUNION DE INICIO DE JORNADA")

    c.line(100, height - 160, width - 100, height - 160)

    c.showPage()

    # 🟢 ===== HOJAS DE FOTOS =====
    for i, foto in enumerate(fotos):

        # Header
        c.setFillColorRGB(0, 0.5, 0)
        c.rect(0, height - 50, width, 50, fill=1)

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 30, "REUNION DE INICIO DE JORNADA")

        # Número de hoja
        c.setFillColorRGB(0, 0, 0)
        c.drawString(width - 50, height - 30, str(i + 1))

        # Imagen
        img_data = base64.b64decode(foto.split(",")[1])
        img = ImageReader(BytesIO(img_data))

        c.drawImage(img, 100, 250, width=400, height=300)

        # Footer verde
        c.setFillColorRGB(0, 0.5, 0)
        c.rect(0, 0, width, 40, fill=1)

        c.showPage()

    # 🟢 ===== HOJA FINAL =====
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 500, "FOTOS DEL PERSONAL PRESENTE")

    c.setFont("Helvetica", 14)
    c.drawString(100, 470, f"Cantidad: {cantidad}")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="reporte_RIJ.pdf")


if __name__ == "__main__":
    app.run()