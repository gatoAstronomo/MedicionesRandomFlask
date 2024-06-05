from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
import pytz
import logging
from bson.json_util import dumps
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Nodo005"
mongo = PyMongo(app)

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obtener_todos_los_datos():
    try:
        result = mongo.db.mediciones.find_one({}, {'_id': 0})
        if result:
            return result['mediciones']
        else:
            return []
    except Exception as error:
        logger.error(f"Error al obtener datos: {error}")
        return []


@app.route('/allMediciones', methods=['GET'])
def obetener_todas_mediciones():
    return jsonify(obetener_todas_mediciones())

    
def obtenerUltimaMedicion(device_name):
    collection = mongo.db.mediciones
    result = collection.find_one({'device_name': device_name}, {'mediciones': {'$slice': -1}})

    if not result:
        return jsonify({'error': 'No se encontraron mediciones para el dispositivo especificado'}), 404

    last_measurement = result['mediciones'][0]
    formatted_result = {'device_name': device_name, 'epoch_time': last_measurement['epoch_time'], 'temperature': last_measurement['temperature'], 'humidity': last_measurement['humidity']}

    return jsonify(formatted_result)


@app.route('/mediciones', methods=['GET'])
def get():
    device_name = "Nodo005"

    if not device_name:
        return jsonify({'error': 'No se proporcionó el nombre del dispositivo'}), 400

    collection = mongo.db.mediciones
    result = collection.find_one({'device_name': device_name}, {'mediciones': {'$slice': -1}})

    if not result:
        return jsonify({'error': 'No se encontraron mediciones para el dispositivo especificado'}), 404

    # Formatear el resultado en el formato deseado
    last_measurement = result['mediciones'][0]
    formatted_result = {'device_name': device_name, 'epoch_time': last_measurement['epoch_time'], 'temperature': last_measurement['temperature'], 'humidity': last_measurement['humidity']}

    return jsonify(formatted_result)

@app.route('/mediciones', methods=['POST'])
def post():
    if request.is_json:
        medicion = request.get_json()
        device_name = medicion["device_name"]
        epoch_time = medicion["epoch_time"]
        temperature = medicion["temperature"]
        humidity = medicion["humidity"]
        print(medicion)
        
        device = mongo.db.mediciones.find_one({"device_name": device_name})

        if device:
            """ Si se encuentra un documento con el mismo nombre de dispositivo,
                agregamos la nueva medición a la lista de mediciones existente """
            mongo.db.mediciones.update_one(
                {"_id": device["_id"]},
                {"$push": {"mediciones": {"epoch_time": epoch_time, "temperature": temperature, "humidity": humidity}}}
            )

            return jsonify({"message": "Medicion agregada correctamente"}), 201
        else:
            """ Si no se encuentra un documento con el mismo nombre de dispositivo,
                creamos un nuevo documento con el nombre de dispositivo y la lista de mediciones """
            mongo.db.mediciones.insert_one({
                "device_name": device_name,
                "mediciones": [{"epoch_time": epoch_time, "temperature": temperature, "humidity": humidity}]
            })
            
            return jsonify({"message": "Dispositivo agregado y medicion agregada correctamente"}), 201
    else:
        return jsonify({"message": "Solicitud no válida"}), 400
    

def imprimirMedicion(medicion):
    device_name = medicion["device_name"]
    epoch_time = medicion["epoch_time"]
    temperature = medicion["temperature"]
    humidity = medicion["humidity"]
    print("{")
    print(f'"device_name":{device_name},"epoch_time":{epoch_time},"temperature":{temperature}","humidity":{humidity}')
    print("}")

# Rutas
@app.route('/')
def pagina_principal():
    return render_template('indexArturo.html', datos_temperatura=obtener_todos_los_datos())

def main():
    app.run(debug=True, host='0.0.0.0', port=8081)

if __name__ == '__main__':
    main()
