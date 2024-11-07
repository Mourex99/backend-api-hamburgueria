from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import make_response
from dotenv import load_dotenv
import os

load_dotenv()  # Lê as variáveis de ambiente do arquivo.env

app = Flask(__name__)

CORS(app, resources={r"/clientes/*": {"origins": "*"}})


# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Definindo o modelo de dados
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    sobrenome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cep = db.Column(db.String(10), nullable=False)

    # Função para converter o modelo em dicionário
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'sobrenome': self.sobrenome,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'cep': self.cep
        }

# Criar o banco de dados
with app.app_context():
    db.create_all()

#Inicio da API CRUD
@app.route('/clientes', methods=['GET'])
def get_clientes():
    clientes = Cliente.query.all()
    return jsonify([cliente.to_dict() for cliente in clientes])

@app.route('/clientes', methods=['POST'])
def add_cliente():
    data = request.get_json()
    novo_cliente = Cliente(
        nome=data['nome'],
        sobrenome=data['sobrenome'],
        telefone=data['telefone'],
        endereco=data['endereco'],
        cep=data['cep']
    )
    db.session.add(novo_cliente)
    db.session.commit()
    return jsonify(novo_cliente.to_dict()), 201

@app.route('/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    data = request.get_json()
    cliente = db.session.get(Cliente, id)
    if cliente:
        cliente.nome = data.get('nome', cliente.nome)
        cliente.sobrenome = data.get('sobrenome', cliente.sobrenome)
        cliente.telefone = data.get('telefone', cliente.telefone)
        cliente.endereco = data.get('endereco', cliente.endereco)
        cliente.cep = data.get('cep', cliente.cep)
        db.session.commit()
        return jsonify(cliente.to_dict()), 200
    return jsonify({"error": "Cliente não encontrado"}), 404

@app.route('/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    cliente = db.session.get(Cliente, id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({"message": "Cliente deletado"}), 200
    return jsonify({"error": "Cliente não encontrado"}), 404    

if __name__ == '__main__':
    app.run()