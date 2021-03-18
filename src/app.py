#Aplicacion desarrollada por Marco Antonio Gonzalez Martinez
from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import json_util, ObjectId
import smtplib
import email.utils
from email.mime.text import MIMEText

#Creacion del servidor
app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/MonolegalDB"
mongo = PyMongo(app)

from_addr = 'noesspamdecuenta0@gmail.com'
to = 'noesspamdecuenta8@outlook.com'

# Reemplaza estos valores con tus credenciales de Google Mail
# Tener en cuenta que hay que darle permiso al correo para poder acceder a la cuenta
username = 'noesspamdecuenta0@gmail.com'
password = 'esincorrecta1324'

@app.route("/AddFactura", methods=['POST'])
def createBill():
    # Reciviendo datos
    codigoFactura = request.json['codigoFactura']
    cliente = request.json['cliente']
    ciudad = request.json['ciudad']
    nit = request.json['nit']
    totalFactura = request.json['totalFactura']
    subTotal = request.json['subTotal']
    iva = request.json['iva']
    retencion = request.json['retencion']
    fechaDeCreacion = request.json['fechaDeCreacion']
    estado = request.json['estado']
    pagada = request.json['pagada']
    fechaDePago = request.json['fechaDePago']
    #verificando que los valores de codifo factura y estado no esten vacios
    if codigoFactura and estado:
        id = mongo.db.Factura.insert(
            {'codigoFactura': codigoFactura,
            'cliente': cliente,
            'ciudad': ciudad,
            'nit': nit,
            'totalFactura': totalFactura,
            'subTotal': subTotal,
            'iva': iva,
            'retencion': retencion,
            'fechaDeCreacion': fechaDeCreacion,
            'estado': estado,
            'pagada': pagada,
            'fechaDePago': fechaDePago 
            }
        )
        response = {
            'id': str(id),
            'CodigoFactura': codigoFactura,
            'Cliente': cliente,
            'estado': estado
        }
        return response
    else:
        return not_found()
    return {'message': 'recived'}

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource Not Found: ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response

@app.route("/getFacturas", methods=['GET'])
def getBill():
    facturas = mongo.db.Factura.find()
    response = json_util.dumps(facturas)
    return Response(response, mimetype='application/json')

@app.route('/getFacturas/<id>', methods=['GET'])
def getOneBill(id):
    client = mongo.db.Factura.find_one({'codigoFactura': id})
    response = json_util.dumps(client)
    return Response(response, mimetype='application/json')

@app.route('/deleteFacturas/<id>', methods=['DELETE'])
def deleteBill(id):
    client = mongo.db.Factura.delete_one({'codigoFactura': id})
    response = jsonify({'message': 'Factura ' + id + ' fue eliminada satisfactoriamente'})
    return response

@app.route('/updateFacturas/<id>', methods=['PUT'])
def UpdateBill(id):  
    estado = request.json['estado']
    estadoanterior = mongo.db.Factura.find_one({'codigoFactura': id})
    #Envio del correo
    setEmail(estadoanterior, estado)
    #Actualizar los datos en la base de datos
    client = mongo.db.Factura.update_one({'codigoFactura': id}, {'$set':{ 'estado': estado}})
    response = jsonify({'message': 'La Factura ' + id + ' fue actualizado satisfactiriamente'})
    return response

def setEmail(estadoanterior, estado):
    #Iniciar sesion en el correo
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    #Creacion del cuerpo del correo: Cuerpo, De, Para. Asunto
    msg = MIMEText("Su factura cambio de: " + estadoanterior['estado'] + " a " + estado)
    msg['To'] = email.utils.formataddr(('Recipient',
                                    'noesspamdecuenta8@outlook.com'))
    msg['From'] = email.utils.formataddr(('Factura',
                                      'noesspamdecuenta0@gmail.com'))
    msg['Subject'] = 'Estado de su factura cambio'
    #envia el correo y cierra la sesion
    server.sendmail(from_addr, to, msg.as_string())
    server.quit()

if __name__ == "__main__":
    app.run(debug=True)