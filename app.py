from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/flaskmysql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Finca(db.Model):
    nit = db.Column(db.String(20), primary_key = True, unique = True)
    nombre  = db.Column(db.String(20))
    contacto  = db.Column(db.String(20))
    direccion = db.Column(db.String(20))
    correo  = db.Column(db.String(20))
    propietario = db.Column(db.String(20))

    def __init__(self, nit, nombre,contacto, direccion, correo , propietario) :
        self.nit = nit
        self.nombre = nombre
        self.contacto = contacto
        self.direccion = direccion
        self.correo = correo
        self.propietario = propietario

class Lote(db.Model):
    id = db.Column(db.Integer, primary_key = True, unique = True)
    numero = db.Column(db.String(20))
    nit_finca = db.Column(db.String(20))
    responsable = db.Column(db.String(20))
    cultivo = db.Column(db.String(20))
    existencias = db.Column(db.Integer)

    def __init__(self, id, numero, nit_finca,responsable , cultivo,existencias ) :
        self.id = id
        self.numero = numero
        self.nit_finca = nit_finca
        self.responsable = responsable
        self.cultivo = cultivo
        self.existencias = existencias

    def serialize(self):
        return {
        "id" : self.id ,
        "numero" : self.numero,
        "nit_finca" : self.nit_finca,
        "responsable" : self.responsable,
        "cultivo" : self.cultivo,
        "existencias" : self.existencias,
        }


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key = True, unique = True)
    nit_finca = db.Column(db.String(20))
    id_Lote = db.Column(db.Integer)
    cantidad_Compra = db.Column(db.Integer)

    def __init__(self, id, nit_finca,id_Lote, cantidad_Compra  ) :
        self.id = id
        self.nit_finca = nit_finca
        self.id_Lote = id_Lote
        self.cantidad_Compra = cantidad_Compra


with app.app_context():
    db.create_all()


class FincaSchema(ma.Schema):
    class Meta:
        fields = ("nit","nombre","contacto","direccion","correo","propietario")

class LoteSchema(ma.Schema):
    class Meta:
        fields = ("id","numero","nit_finca","responsable","cultivo","existencias")

class VentaSchema(ma.Schema):
    class Meta:
        fields = ("id","nit_finca","id_Lote","cantidad_Compra")



finca_schema = FincaSchema()
fincas_schema = FincaSchema(many=True)

lote_schema = LoteSchema()
lotes_schema = LoteSchema(many=True)

venta_schema = VentaSchema()
ventas_schema = VentaSchema(many=True)



# Rutas Finca
@app.route('/finca', methods=['POST'])
def create_finca():
    finca_data = request.json
    new_finca = Finca(**finca_data)
    db.session.add(new_finca)
    db.session.commit()
    return finca_schema.jsonify(new_finca)

@app.route('/fincas', methods=['GET'])
def getFincas():
    all_Fincas = Finca.query.all()
    result = fincas_schema.dump(all_Fincas)
    
    return jsonify(result)

@app.route('/finca/<nit>', methods=['GET'])
def getFinca(nit):
    finca = Finca.query.get(nit)

    return finca_schema.jsonify(finca)

@app.route('/finca/<nit>', methods=['PUT'])
def updateFinca(nit):
    finca = Finca.query.get(nit)

    if not finca:
        return "No se encontró la finca", 404

    finca.nombre = request.json.get("nombre", finca.nombre)
    finca.contacto = request.json.get("contacto", finca.contacto)
    finca.direccion = request.json.get("direccion", finca.direccion)
    finca.correo = request.json.get("correo", finca.correo)
    finca.propietario = request.json.get("propietario", finca.propietario)

    db.session.commit()

    return finca_schema.jsonify(finca)


@app.route('/finca/<nit>', methods=['DELETE'])
def deteleFinca(nit):
   finca = Finca.query.get(nit)

   db.session.delete(finca)
   db.session.commit()

   return finca_schema.jsonify(finca)


# Rutas Lote
@app.route('/lote', methods=['POST'])
def create_lote():
    try:
        lote_data = request.json

        # Extraemos los datos necesarios para crear el nuevo lote
        numero = lote_data["numero"]
        nit_finca = lote_data["nit_finca"]
        responsable = lote_data["responsable"]
        cultivo = lote_data["cultivo"]
        existencias = lote_data["existencias"]

        # Verificamos que la finca exista antes de crear el lote
        finca = Finca.query.filter_by(nit=nit_finca).first()
        if not finca:
            return f"El NIT de la finca asignada no es válido o no existe: {nit_finca}", 400

        # Creamos el nuevo lote
        new_lote = Lote(numero=numero, nit_finca=nit_finca, responsable=responsable,
                        cultivo=cultivo, existencias=existencias)

        # Guardamos el nuevo lote en la base de datos
        db.session.add(new_lote)
        db.session.commit()

        # Retornamos el nuevo lote creado
        return lote_schema.jsonify(new_lote), 201

    except Exception as e:
        print(e)
        return "Ocurrió un error al crear el lote", 500

    
@app.route('/lotes', methods=['GET'])
def getLotes():
    all_Lotes = Lote.query.all()
    result = lotes_schema.dump(all_Lotes)
    
    return jsonify(result)

@app.route('/lote/<id>', methods=['GET'])
def getLote(id):
    lote = Lote.query.get(id)

    return lote_schema.jsonify(lote)

@app.route('/lote/<id>', methods=['PUT'])
def updateLote(id):
    lote = Lote.query.get(id)

    numero = request.json["numero"]
    nit_finca = request.json["nit_finca"]
    responsable = request.json["responsable"]
    cultivo = request.json["cultivo"]
    existencias = request.json["existencias"]

    lote.numero = numero
    lote.nit_finca = nit_finca
    lote.responsable = responsable
    lote.cultivo = cultivo
    lote.existencias = existencias

    db.session.commit()

    return lote_schema.jsonify(lote)

@app.route('/lote/<id>', methods=['DELETE'])
def deteleLote(id):
    lote = Lote.query.get(id)

    db.session.delete(lote)
    db.session.commit()

    return lote_schema.jsonify(lote)


# Rutas Combinadas
@app.route('/Inventario/<nit>', methods=['GET'])
def getInventario(nit):
    finca = Finca.query.get(nit)

    if not finca:
        return "Esta Finca no existe"

    lotes = Lote.query.filter_by(nit_finca=nit).all()

    inventario = []
    for lote in lotes:
        inventario.append(lote.serialize())

    return jsonify(inventario)

    

# Ruta Ventas
@app.route('/venta', methods=['POST'])
def create_venta():
    nit_finca = request.json["nit_finca"]
    id_lote = request.json["id_lote"]
    cantidad_compra = request.json["cantidad_compra"]

    # Verifica que la finca y el lote existan
    finca = Finca.query.filter_by(nit=nit_finca).first()
    lote = Lote.query.filter_by(id=id_lote).first()

    if not finca:
        return jsonify({"message": f"No existe una finca con el NIT {nit_finca}"}), 400
    
    if not lote:
        return jsonify({"message": f"No existe un lote con el ID {id_lote}"}), 400

    # Verifica que existan suficientes existencias en el lote
    if cantidad_compra > lote.existencias:
        return jsonify({"message": "No hay suficientes existencias en el lote"}), 400

    # Crea la venta
    venta = Venta(nit_finca=nit_finca, id_Lote=id_lote, cantidad_Compra=cantidad_compra)
    db.session.add(venta)

    # Actualiza las existencias del lote
    lote.existencias -= cantidad_compra

    db.session.commit()

    return venta_schema.jsonify(venta), 201



if __name__ == "__main__":
    app.run(debug=True)
