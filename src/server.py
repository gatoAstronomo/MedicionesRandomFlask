from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Nodo005"
mongo = PyMongo(app)

@app.route('/mediciones', methods=['POST'])
def post():
    if request.is_json:
        medicion = request.get_json()
        device_name = medicion["device_name"]
        epoch_time = medicion["epoch_time"]
        value = medicion["value"]
        print(request.get_data.__dict__)

        # Buscamos un documento con el mismo nombre de dispositivo
        device = mongo.db.mediciones.find_one({"device_name": device_name})

        if device:
            # Si se encuentra un documento con el mismo nombre de dispositivo,
            # agregamos la nueva medición a la lista de mediciones existente
            mongo.db.mediciones.update_one(
                {"_id": device["_id"]},
                {"$push": {"mediciones": {"epoch_time": epoch_time, "value": value}}}
            )

            return jsonify({"message": "Medicion agregada correctamente"}), 201
        else:
            # Si no se encuentra un documento con el mismo nombre de dispositivo,
            # creamos un nuevo documento con el nombre de dispositivo y la lista de mediciones
            mongo.db.mediciones.insert_one({
                "device_name": device_name,
                "mediciones": [{"epoch_time": epoch_time, "value": value}]
            })

            return jsonify({"message": "Dispositivo agregado y medicion agregada correctamente"}), 201
    else:
        return jsonify({"message": "Solicitud no válida"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
