from flask import Flask, jsonify, request, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from config import Config
from models import init_db
from datetime import datetime
from werkzeug.utils import secure_filename

import os

app = Flask(__name__)
app.config.from_object(Config)

mysql = init_db(app)
CORS(app)
api = Api(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

class Infantes(Resource):
    def post(self):
        data = request.get_json()
        id = data.get('id')
        nombre = data.get('nombre')
        edad = data.get('edad')
        sexo = data.get('sexo')
        if sexo not in ['M', 'F']:
            return {"message": "Sexo must be 'M' or 'F'"}, 400
        peso = data.get('peso')
        talla = data.get('talla')
        try:
            # Insertar datos en la tabla 'infante'
            query = "INSERT INTO infante (id, nombre, edad, sexo, peso, talla) VALUES (%s, %s, %s, %s, %s, %s)"
            cur = mysql.connection.cursor()
            cur.execute(query, (id, nombre, edad, sexo, peso, talla))
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            return {"message": f"Error inserting infante: {str(e)}"}, 500
        return {"message": "Infante added successfully"}, 201
   
    def get(self, infante_id):
        try:
            if not infante_id:
                return {"message": "infante_id is required"}, 400
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM estado WHERE infante_id = %s", (infante_id,))
            estados = cur.fetchall()
            cur.close()

            response = []
            for estado in estados:
                estado_dict = {
                    'id': estado.get('id'),
                    'infante_id': estado.get('infante_id'),
                    'fecha': estado.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if estado.get('fecha') else None,
                    'grado_desnutricion': estado.get('grado_desnutricion'),
                    'imagen_path': f"{request.host_url}uploads/{estado.get('imagen_path')}" if estado.get('imagen_path') else None
                }
                response.append(estado_dict)

            return jsonify(response)
        except Exception as e:
            return jsonify({"message": f"Error retrieving estados for infante_id {infante_id}: {str(e)}"}), 500

api.add_resource(Infantes, '/infantes', '/infantes/estados/<int:infante_id>')

class Estado(Resource):
    def post(self):
            # Obtener los datos 
        infante_id = request.form.get('infante_id')
        grado_desnutricion = request.form.get('grado_desnutricion')
        imagen_path = request.files['imagen_path'] # Obtener el archivo de imagen enviado en la solicitud
        
        # Validar el archivo de imagen
        if imagen_path and allowed_file(imagen_path.filename):
            # Guardar el archivo de imagen en el directorio de uploads
            filename = secure_filename(imagen_path.filename)
            imagen_path.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Obtener la fecha actual
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                # Insertar los datos en la tabla 'estado'
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO estado (infante_id, fecha, grado_desnutricion, imagen_path) VALUES (%s, %s, %s, %s)",
                            (infante_id, fecha, grado_desnutricion, filename))
                mysql.connection.commit()
                cur.close()
                
                return {"message": "Estado added successfully"}, 201
            except Exception as e:
                return {"message": f"Error adding estado: {str(e)}"}, 500
        else:
            return {"message": "Invalid file or file extension not allowed"}, 400

    def get(self, id):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM estado WHERE id = %s", (id,))
            estado = cur.fetchone()
            cur.close()

            if not estado:
                return {"message": f"Estado with id {id} not found"}, 404

            estado_dict = {
                'id': estado.get('id'),
                'infante_id': estado.get('infante_id'),
                'fecha': estado.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if estado.get('fecha') else None,
                'grado_desnutricion': estado.get('grado_desnutricion'),
                'imagen_path': f"{request.host_url}uploads/{estado.get('imagen_path')}" if estado.get('imagen_path') else None
            }

            return estado_dict
        except Exception as e:
            return {"message": f"Error retrieving estado with id {id}: {str(e)}"}, 500
api.add_resource(Estado, '/estado', '/estado/<int:id>')
        

if __name__ == '__main__':
    app.run(debug=True)