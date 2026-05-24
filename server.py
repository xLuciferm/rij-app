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

    plantilla = ImageReader("plantilla.jpg")

    img_width = 400
    img_height = 250

    for i, foto in enumerate(fotos):

    c.drawImage(plantilla, 0, 0, width=width, height=height)

    img_data = base64.b64decode(foto.split(",")[1])
    img = ImageReader(BytesIO(img_data))

    img_width = 400
    img_height = 250

    # 🎯 CENTRADO HORIZONTAL
    x = (width - img_width) / 2

    # 📉 MÁS ABAJO (AJUSTE PRINCIPAL)
    y = 180

    c.drawImage(img, x, y, width=img_width, height=img_height)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(500, 750, str(i + 1))

    c.showPage()

    c.drawImage(plantilla, 0, 0, width=width, height=height)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(150, 500, "FOTOS DEL PERSONAL PRESENTE")
    c.drawString(150, 470, f"Cantidad: {cantidad}")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="RIJ_CFE.pdf")


if __name__ == "__main__":
    app.run(debug=True)