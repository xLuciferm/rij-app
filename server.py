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

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        width, height = letter

        for i, hoja in enumerate(hojas):

            c.setFillColorRGB(1,1,1)
            c.rect(0,0,width,height,fill=1)

            header_h = 80
            c.setFillColorRGB(0,0.5,0.2)
            c.rect(0,height-header_h,width,header_h,fill=1)

            c.setFillColorRGB(1,1,1)
            c.drawString(30,height-40,"CFE RIJ")

            fotos = hoja

            if len(fotos) == 1:

                img = ImageReader(BytesIO(base64.b64decode(fotos[0].split(",")[1])))

                iw, ih = img.getSize()
                scale = min((width-80)/iw,(height-header_h-120)/ih)

                w, h = iw*scale, ih*scale

                x = (width-w)/2
                y = (height-header_h-h)/2

                c.drawImage(img, x, y, w, h)

            else:

                cols = 2 if len(fotos) <= 6 else 3
                gap = 12

                img_w = 200
                img_h = 150

                start_x = 60
                start_y = height-header_h-20

                x = start_x
                y = start_y

                for j, foto in enumerate(fotos):

                    img = ImageReader(BytesIO(base64.b64decode(foto.split(",")[1])))

                    c.drawImage(img, x, y-img_h, img_w, img_h)

                    if (j+1) % cols == 0:
                        x = start_x
                        y -= img_h + gap
                    else:
                        x += img_w + gap

            c.showPage()

        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{nombre}.pdf"
        )

    except Exception:
        traceback.print_exc()
        return "Error", 500


if __name__ == "__main__":
    app.run(debug=True)