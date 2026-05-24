from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for i, foto in enumerate(fotos):
        c.drawString(200, 750, "REUNION DE INICIO DE JORNADA")

        img_data = base64.b64decode(foto.split(",")[1])
        img = BytesIO(img_data)

        c.drawImage(img, 100, 300, width=400, height=300)

        c.drawString(500, 730, str(i+1))
        c.showPage()

    c.drawString(150, 500, "FOTOS DEL PERSONAL PRESENTE")
    c.drawString(150, 480, f"Cantidad: {data['cantidad']}")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="reporte.pdf")

# 👇 ESTA ES LA CLAVE
if __name__ == "__main__":
    app.run()