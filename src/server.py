from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
import pytz
import logging
from bson.json_util import dumps
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from math import sqrt

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Nodo005"
mongo = PyMongo(app)

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/allMediciones', methods=['GET'])
def getAllMediciones():
    return jsonify(obtenerTodasLasMediciones())
    
@app.route('/mediciones', methods=['GET'])
def get():
    device_name = "Nodo005"

    if not device_name:
        return jsonify({'error': 'No se proporcionó el nombre del dispositivo'}), 400

    return obtenerUltimaMedicion(device_name)

@app.route('/mediciones', methods=['POST'])
def post():
    if not request.is_json:
        return jsonify({"message": "Solicitud no válida"}), 400
    
    medicion = request.get_json()
    return saveMedicion(medicion)
    
@app.route('/')
def pagina_principal():
    return render_template('indexArturo.html', datos_temperatura=obtenerTodasLasMediciones())

def obtenerUltimaMedicion(device_name):
    collection = mongo.db.mediciones
    result = collection.find_one({'device_name': device_name}, {'mediciones': {'$slice': -1}})

    if not result:
        return jsonify({'error': 'No se encontraron mediciones para el dispositivo especificado'}), 404

    last_measurement = result['mediciones'][0]
    formatted_result = {'device_name': device_name, 'epoch_time': last_measurement['epoch_time'], 
                        'x': last_measurement['x'], 
                        'y': last_measurement['y'], 
                        'z': last_measurement['z'], 
                        'gx': last_measurement['gx'], 
                        'gy': last_measurement['gy'], 
                        'gz': last_measurement['gz'],
                        'ismove': last_measurement['ismove']}

    return jsonify(formatted_result)

def obtenerTodasLasMediciones():
    try:
        result = mongo.db.mediciones.find_one({}, {'_id': 0})
        return result['mediciones']
    except Exception as error:
        logger.error(f"Error al obtener datos: {error}")
        return []
    
def saveMedicion(medicion):
    device_name = medicion["device_name"]
    epoch_time = medicion["epoch_time"]
    x = medicion["x"]
    y = medicion["y"]
    z = medicion["z"]
    gx = medicion["gx"]
    gy = medicion["gy"]
    gz = medicion["gz"]
    ismove = False
    print(medicion)
    print(modulo(x,y,z))
        
    device = mongo.db.mediciones.find_one({"device_name": device_name})

    if modulo(x,y,z) > 2:
            sendMail("Anomalia se esta agotando el combustible", f'El vector aceleracion es ({x},{y},{z}) el giroscopio es ({gx},{gy},{gz})')
    
    if 1.5 < modulo(x,y,z):
        ismove = True

    if device:
        """ Si se encuentra un documento con el mismo nombre de dispositivo,
            agregamos la nueva medición a la lista de mediciones existente """
        mongo.db.mediciones.update_one(
            {"_id": device["_id"]},
            {"$push": {"mediciones": {
                "epoch_time": epoch_time, 
                "x": x, 
                "y": y, 
                "z": z,
                "gx": gx, 
                "gy": gy, 
                "gz": gz,
                "ismove": ismove
                }}}
        )
        
        return jsonify({"message": "Medicion agregada correctamente"}), 201
    else:
        """ Si no se encuentra un documento con el mismo nombre de dispositivo,
            creamos un nuevo documento con el nombre de dispositivo y la lista de mediciones """
        mongo.db.mediciones.insert_one({
            "device_name": device_name,
            "mediciones": [{"epoch_time": epoch_time, "x": x, "y": y, "z": z, "gx": gx, "gy": gy, "gz": gz, "ismove": ismove}]
        })

        return jsonify({"message": "Dispositivo agregado y medicion agregada correctamente"}), 201
    
def modulo(x, y, z):
    return sqrt(x**2 + y**2 + z**2)
    
def extractUndo():
    with open("/home/ubuntu/undo.json", "r") as file:
        undo = json.load(file)
        print(undo["p"][::-1])
        return undo["p"][::-1]

def sendMail(subject, body):

    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    sender_email = "a.rivas06@ufromail.cl"
    receiver_email = "a.rivas06@ufromail.cl"
    # receiver_email = "jorge.diaz@ufrontera.cl"
    password = extractUndo()
    mensaje = MIMEMultipart()

    mensaje['From'] = sender_email
    mensaje['To'] = receiver_email
    mensaje['Subject'] = subject

    mensaje.attach(MIMEText(body, 'plain'))
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, mensaje.as_string())
        print("Correo electrónico enviado exitosamente.")

    except Exception as e:
        print(f"No se pudo enviar el correo electrónico. Error: {e}")

    finally:
        server.quit()

def main():
    app.run(debug=True, host='0.0.0.0', port=8081)

if __name__ == '__main__':
    main()
