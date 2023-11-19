import re
from flask import Flask, render_template, request

app = Flask(__name__)

def processar_esquema(esquema):
    resultat = {}
    patro = re.compile(r'([^\d]+):\s[^\d]+(\d+(\.\d+)?)%\s\((\w+)\)')
    for linia in esquema.split('\n'):
        coincidencia = patro.search(linia)
        if coincidencia:
            color, percentatge, _, intensitat = coincidencia.groups()
            resultat[color.lower()] = (float(percentatge), intensitat.lower())
    return resultat

def classificar_colors(resultat_processat, umbral):
    colors_seleccionats = ['vermell', 'blau', 'groc', 'verd', 'taronja']
    colors_classificats = {color: "Alt" if percentatge > umbral else "Baix" for color, (percentatge, _) in resultat_processat.items() if color.lower() in colors_seleccionats}

    return colors_classificats

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        esquema_usuari = request.form['esquema']
        resultat_processat = processar_esquema(esquema_usuari)
        colors_classificats = classificar_colors(resultat_processat, umbral=7)
        return render_template('index.html', colors=colors_classificats, esquema=esquema_usuari)
    return render_template('index.html', colors=None, esquema=None)

if __name__ == '__main__':
    app.run(debug=True)

