from flask import Flask, request, jsonify #Importa o FLask
from flask_sqlalchemy import SQLAlchemy #Importa a biblioteca que cuidara do banco de dados, permitindo troca de DB para escalar

app= Flask(__name__) #Instancia o flask

#Cria o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

#Classe responsável para os itens do banco de dados
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable= False)
    price = db.Column(db.Float, nullable= False)
    description = db.Column(db.Text, nullable = True)

@app.route('/api/product/add', methods=['POST'])
def add_product():
    try:
        data = request.json
        product = Product(
            name=data['name'],
            price=data['price'],
            description=data.get('description', '')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(f'error in {e}')})

#Definindo rota raíz
@app.route('/')
def hello_word():
    return 'Hello Word!'
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco/tabelas se não existirem
    app.run(debug=True)
