from flask import Flask, render_template, request
import os
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
nltk.download('punkt') 
import cv2
import requests as req
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
import re
#---------------------------------
color_dict = {
    "Vermell Fosc": ((0, 0, 150), (50, 50, 200)),
    "Vermell Clar": ((50, 50, 200), (100, 100, 255)),
    "Verd Fosc": ((0, 150, 0), (50, 200, 50)),
    "Verd Clar": ((50, 200, 50), (100, 255, 100)),
    "Blau Fosc": ((150, 0, 0), (200, 50, 50)),
    "Blau Clar": ((200, 50, 50), (255, 100, 100)),
    "Groc": ((0, 150, 150), (100, 255, 255)),
    "Taronja": ((0, 80, 150), (100, 165, 255)),
    "Porpra Fosc": ((80, 0, 80), (120, 50, 120)),
    "Porpra Clar": ((120, 50, 120), (165, 100, 165)),
    "Rosa": ((150, 0, 150), (255, 100, 255)),
    "Marró": ((10, 30, 60), (20, 50, 100)),
    "Gris Fosc": ((100, 100, 100), (150, 150, 150)),
    "Gris Clar": ((150, 150, 150), (200, 200, 200)),
    "Cian": ((150, 150, 0), (255, 255, 100)),
    "Llima": ((50, 205, 50), (100, 255, 100)),
    "Indi": ((130, 0, 75), (255, 100, 130)),
    "Oliva": ((47, 107, 85), (0, 128, 128)),
    "Beix": ((220, 245, 245), (240, 255, 255)),
    "Blau Verdós": ((128, 128, 0), (150, 150, 100)),
    "Blau Marí": ((128, 0, 0), (205, 100, 100)),
    "Granat": ((0, 0, 128), (96, 48, 176)),
    "Daurat": ((0, 215, 255), (48, 255, 255)),
    "Groc Clar": ((0, 200, 200), (100, 255, 255)),
    "Groc Fosc": ((0, 150, 150), (0, 200, 200)),
    "Magenta": ((200, 0, 200), (255, 0, 255)),
    "Cel": ((255, 255, 0), (255, 255, 100)),
    "Violeta": ((211, 0, 148), (211, 85, 186)),
    "Salmó": ((114, 128, 250), (122, 160, 255)),
    "Caqui": ((107, 183, 189), (140, 230, 240)),
    "Turquesa": ((208, 224, 64), (238, 238, 175)),
    "Xocolata": ((0, 63, 123), (45, 82, 160)),
    "Tomàquet": ((0, 0, 255), (71, 99, 255)),
    "Plata": ((192, 192, 192), (211, 211, 211)),
    "Lavanda": ((221, 160, 221), (170, 232, 238)),
    "Vori": ((170, 232, 238), (240, 255, 255)),
    "Or Vell": ((32, 165, 218), (170, 232, 238)),
    "Vermell": ((0, 0, 150), (100, 100, 255)),
    "Verd": ((0, 150, 0), (100, 255, 100)),
    "Blau": ((150, 0, 0), (255, 100, 100)),
    "Porpra": ((80, 0, 80), (165, 100, 165)),
    "Gris": ((100, 100, 100), (200, 200, 200)),
}
#-------------------------------------------------------------------------------
def analitza_colors(img_path):
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    avg_luminosity_total = np.mean(img)
    luminosity_str = "La imatge és generalment lluminosa." if avg_luminosity_total > 128 else "La imatge és generalment fosca."
    total_pixels = img.shape[0] * img.shape[1]
    color_var = {}
    response_printed = False  

    for color_name, (lower, upper) in color_dict.items():
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(img, lower, upper)
        color_pixels = cv2.countNonZero(mask)
        output_str = ""

        percentage = (color_pixels / total_pixels) * 100
        if percentage >= 0.01:
            if color_name not in color_var:
                output_str = f"{color_name} {percentage:.2f}% "
                if color_pixels > 0:
                    masked_img = cv2.bitwise_and(img, img, mask=mask)
                    avg_luminosity = np.mean(masked_img[mask > 0])
                    output_str += f"({ 'Lluminós' if avg_luminosity > 128 else 'Fosc'})"
                output_str += "\n"
                color_var[color_name] = output_str

                if not response_printed:
                    print(output_str)
                    response_printed = True

    return color_var, luminosity_str
#-------------------------------------------------------------------------------
x = '0'
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
            file.save(file_path)
            color_var, luminosity_str = analitza_colors(file_path)
            esquema = (str(color_var) + str(luminosity_str))
            print(esquema)
            #'http://localhost:5000'
            #payload = {'color_var': color_var, 'luminosity_str': luminosity_str}
            #req.post(other_app_url, data=payload)
            #req.post("http://localhost:5000/?=" + str(color_var) + str(luminosity_str))
            url_post = 'http://localhost:5000'
            data_post = {'esquema': esquema}
            response_post = req.post(url_post, data=data_post)
            print(response_post.text)
            palabras_especificas = re.findall(r'\b(blau fosc|vermell fosc|groc fosc|verd fosc|taronja fosc|blau clar|vermell clar|groc clar|verd clar|taronja clar|blau|vermell|groc|verd|taronja|lluminosa|fosca)\b', response_post.text, flags=re.IGNORECASE)
            print("Palabras encontradas:", palabras_especificas)
            palabras_unicas = list(set(palabras_especificas))

            print("Palabras únicas encontradas:", palabras_unicas)
            resultado = []
            x = 1
            for palabra in palabras_unicas:
                url = "http://localhost:5002/get?msg=" + palabra
                resp = req.get(url)
                respuesta = f"Resposta{x}: {resp.text}"
                print(respuesta)
                resultado.append(respuesta)  
                x += 1

            #return render_template('result.html', color_var=color_var, luminosity_str=luminosity_str, image_path='uploads/uploaded_image.jpg')
            return render_template('result.html', color_var=color_var, luminosity_str=luminosity_str, image_path='uploads/uploaded_image.jpg', resultado=resultado)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port='5001')
