from flask import Flask, request, send_file, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import base64
from io import BytesIO
import os
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
        cantidad = data.get("cantidad", 0)
        nombre = data.get("nombre", "RIJ_CFE")

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        width, height = letter

        # 🔥 AQUÍ VA TU RUTA CORRECTA
        ruta = os.path.join(os.path.dirname(__file__), "plantilla.jpg")
        plantilla = ImageReader(ruta)

        img_width = 400
        img_height = 250

        for i, foto in enumerate(fotos):

            c.drawImage(plantilla, 0, 0, width=width, height=height)

            try:
                if foto and "," in foto:
                    img_data = base64.b64decode(foto.split(",")[1])
                    img = ImageReader(BytesIO(img_data))

                    x = (width - img_width) / 2
                    y = 180

                    c.drawImage(img, x, y, width=img_width, height=img_height)

            except Exception as e:
                print(f"Error en foto {i}: {e}")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(500, 750, str(i + 1))

            c.showPage()

        # 🟢 HOJA FINAL
        c.drawImage(plantilla, 0, 0, width=width, height=height)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(150, 500, "FOTOS DEL PERSONAL PRESENTE")
        c.drawString(150, 470, f"Cantidad: {cantidad}")

        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=nombre + ".pdf"
        )

    except Exception:
        traceback.print_exc()
        return "Error interno al generar PDF", 500


if __name__ == "__main__":
    app.run(debug=True)