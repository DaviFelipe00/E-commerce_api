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

#Método para adicionar produto com Try/except, caso de algum erro de chave e valor, retornara erro de BAD REQUEST
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

#Método para deletar um produto, uso o parametro de ID para excluir 
@app.route('/api/product/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted succesfully"})
    return jsonify({"message": "Product not found"},404)

#Método de retorno para dados dos produtos
@app.route('/api/product/<int:product_id>', methods=['Get'])
def product_description(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message": "Product not found"},404)

@app.route('/api/product/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"},400)
    
    data = request.json
    if 'name' in data:
        product.name = data['name']
        
    if 'price' in data:
        product.price = data['price']
        
    if 'description' in data:
        product.description = data['description']
        
    db.session.commit()
    return jsonify({"message": "Product updated succesfully"})

#Definindo rota raíz
@app.route('/')
def hello_word():
    return 'Hello Word!'
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco/tabelas se não existirem
    app.run(debug=True)
