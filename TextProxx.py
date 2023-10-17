import pickle
import random
import numpy
import json
import tensorflow
import tflearn
from influxdb import InfluxDBClient
from flask import Flask, render_template, request
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
 

with open("contenido.json") as archivo:
    datos = json.load(archivo)

palabras = []
tags = []
auxX = []
auxY = []

for contenido in datos["contenido"]:
    for patrones in contenido["patrones"]:
        auxPalabra = nltk.word_tokenize(patrones)
        palabras.extend(auxPalabra)
        auxX.append(auxPalabra)
        auxY.append(contenido["tag"])

        if contenido["tag"] not in tags:
            tags.append(contenido["tag"])

palabras = [stemmer.stem(w.lower()) for w in palabras if w != "?"]
palabras = sorted(list(set(palabras)))
tags = sorted(tags)
aprendizaje = []
salida = []

salidaVacia = [0 for _ in range(len(tags))]
for x, documento in enumerate(auxX):
    corchete = []
    auxPalabra = [stemmer.stem(w.lower()) for w in documento]
    for w in palabras:
        if w in auxPalabra:
            corchete.append(1)
        else:
            corchete.append(0)
    filaSalida = salidaVacia[:]
    filaSalida[tags.index(auxY[x])] = 1
    aprendizaje.append(corchete)
    salida.append(filaSalida)

aprendizaje = numpy.array(aprendizaje)
salida = numpy.array(salida)


red = tflearn.input_data(shape=[None, len(aprendizaje[0])])
red = tflearn.fully_connected(red, 10)
red = tflearn.fully_connected(red, 10)
red = tflearn.fully_connected(red, len(salida[0]), activation="softmax")
red = tflearn.regression(red)

modelo = tflearn.DNN(red)
modelo .fit(aprendizaje, salida, n_epoch=1000, batch_size=11, show_metric=True)
modelo .save("modelo.tflearn")


def Lucy(entrada):

        corchete = [0 for _ in range(len(palabras))]
        entradaProcesada = nltk.word_tokenize(entrada)
        print("entradaProcesada: ", entradaProcesada)
        entradaProcesada = [stemmer.stem(palabra.lower())
                                         for palabra in entradaProcesada]
        for palabraInidvidual in entradaProcesada:
            for i, palabra in enumerate(palabras):
                if palabra == palabraInidvidual:
                    corchete[i] = 1
        resultados = modelo.predict([numpy.array(corchete)])
        resultadosIndices = numpy.argmax(resultados)
        tag = tags[resultadosIndices]

        for tagAux in datos["contenido"]:
            if tagAux["tag"] == tag:
                respuesta = tagAux["respuestas"]
    
        print("Lucy: ",random.choice(respuesta))

        return (random.choice(respuesta))



app = Flask(__name__, template_folder='templates',
                   static_folder='../chatbot/static', static_url_path='/static')


@app.route("/get")
def getBotResponse():
    userText = ''
    userText = request.args.get('msg')
    if userText == "":
        return str("No te entiendo")

    return Lucy(userText)

@app.route('/')
def principal():
    return render_template('index.html')
#@app.route('/sobreNosotros')
#def sobreNosotros():
#    return render_template('Info.html')



if __name__ == "__main__":
    app.debug=False
    app.run(host="localhost", port=6081)