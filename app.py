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
        id = request.form.get('id')
        nombre = request.form.get('nombre')
        sexo = request.form.get('sexo')
        if sexo not in ['H', 'M']:
            return {"message": "Sexo must be 'H' or 'M'"}, 400
        
        edad = request.form.get('edad')
        peso = request.form.get('peso')
        talla = request.form.get('talla')
        if not id or not nombre or not sexo or not edad or not peso or not talla:
            return {"message": "All fields are required"}, 400
        
        # Obtener los datos 
        infante_id = id
        imagen_path = request.files['imagen_path'] # Obtener el archivo de imagen enviado en la solicitud
        
        # Validar el archivo de imagen
        if imagen_path and allowed_file(imagen_path.filename):
            # Guardar el archivo de imagen en el directorio de uploads
            filename = secure_filename(imagen_path.filename)
            imagen_path.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Obtener la fecha actual
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Calcular el grado de desnutrición
            grado_desnutricion_red = 0
            grado_desnutricion_icbf = 0 

            try:
                cur = mysql.connection.cursor()
                
                # Verificar si el infante ya existe
                cur.execute("SELECT * FROM infante WHERE id = %s", (id,))
                infante_exists = cur.fetchone()
                
                if not infante_exists:
                    # Insertar datos en la tabla 'infante'
                    query = "INSERT INTO infante (id, nombre, sexo) VALUES (%s, %s, %s)"
                    cur.execute(query, (id, nombre, sexo))
                    mysql.connection.commit()

                # Insertar datos en la tabla 'estado'
                query = "INSERT INTO estado (infante_id, fecha, peso, talla, edad, grado_desnutricion_icbf, grado_desnutricion_red, imagen_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(query, (infante_id, fecha, peso, talla, edad, grado_desnutricion_icbf, grado_desnutricion_red, filename))
                estado_id = cur.lastrowid  # Obtener el id generado
                mysql.connection.commit()
                cur.close() 

            except Exception as e:
                return {"message": f"Error inserting datos: {str(e)}"}, 500

            return {"message": "Infante added successfully", "estado_id": estado_id}, 201
    
        else:
            return {"message": "Invalid file or file extension not allowed"}, 400

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
                    'fecha': estado.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if estado.get('fecha') else None,
                }
                response.append(estado_dict)

            return jsonify(response)
        except Exception as e:
            return jsonify({"message": f"Error retrieving estados for infante_id {infante_id}: {str(e)}"}), 500

api.add_resource(Infantes, '/infantes', '/infantes/estados/<int:infante_id>')

class Estado(Resource):
        
    def get(self, id):
        try:
            cur = mysql.connection.cursor()
            # Realizar una consulta JOIN para obtener los datos del estado y del infante
            query = """
                SELECT 
                    estado.id AS estado_id, 
                    estado.infante_id, 
                    estado.fecha, 
                    estado.peso,
                    estado.talla,
                    estado.edad,
                    estado.grado_desnutricion_icbf, 
                    estado.grado_desnutricion_red,
                    estado.imagen_path,
                    infante.nombre AS infante_nombre,
                    infante.sexo AS infante_sexo
                FROM estado
                JOIN infante ON estado.infante_id = infante.id
                WHERE estado.id = %s
            """
            cur.execute(query, (id,))
            estado = cur.fetchone()
            cur.close()

            if not estado:
                return {"message": f"Estado with id {id} not found"}, 404

            estado_dict = {
                'id': estado['estado_id'],
                'infante_id': estado['infante_id'],
                'fecha': estado['fecha'].strftime('%Y-%m-%d %H:%M:%S') if estado['fecha'] else None,
                'peso': estado['peso'],
                'talla': estado['talla'],
                'edad': estado['edad'],
                'grado_desnutricion_icbf': estado['grado_desnutricion_icbf'],
                'grado_desnutricion_red': estado['grado_desnutricion_red'],
                'imagen_path': f"{request.host_url}uploads/{estado['imagen_path']}" if estado['imagen_path'] else None,
                'infante_nombre': estado['infante_nombre'],
                'infante_sexo': estado['infante_sexo']
            }

            return estado_dict
        except Exception as e:
            return jsonify({"message": f"Error retrieving estado with id {id}: {str(e)}"}), 500
api.add_resource(Estado, '/estado/<int:id>')
        

if __name__ == '__main__':
    app.run(debug=True)