from flask import Flask, request, jsonify #Importa o FLask
from flask_sqlalchemy import SQLAlchemy #Importa a biblioteca que cuidara do banco de dados, permitindo troca de DB para escalar
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user


app= Flask(__name__) #Instancia o flask
app.config['SECRET_KEY'] = 'minha_chave_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

#login manager serve para autenticar o usuário, só o usuário autenticado tem permissão de mexer em determinadas rotas
login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

#Classe de usuário, com nome e senha
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(80), nullable= False, unique=True)
    password = db.Column(db.String(80), nullable = False)

#Classe responsável para os itens do banco de dados
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable= False)
    price = db.Column(db.Float, nullable= False)
    description = db.Column(db.Text, nullable = True)

#Autenticação de usuário
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Rota de Login e autenticação de usuário
@app.route('/login', methods= ['POST'])
def login():
    data = request.json
    
    user = User.query.filter_by(user_name = data.get("user_name")).first()
    
    if user and data.get('password') == user.password:
        login_user(user)
        return jsonify({"message": "Logged is succesfully"})
    
    return jsonify({"message": "Unauthorized. Invalid credentials"}) ,401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message:" "Logout succesfully"})
    

#Método para adicionar produto com Try/except, caso de algum erro de chave e valor, retornara erro de BAD REQUEST
@app.route('/api/product/add', methods=['POST'])
@login_required
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
@login_required
def delete_product(product_id):
    
    product = Product.query.get(product_id)
    
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted succesfully"})
    
    return jsonify({"message": "Product not found"},404)

#Método de retorno para dados dos produtos
@app.route('/api/products/<int:product_id>', methods=['Get'])
@login_required
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

#Rota de update
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

#Rota para mostrar todos os produtos do banco de dados
@app.route('/api/products')
def products():
    
    products = Product.query.all()
    products_list = []
    
    for product in products:
        all_product = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description
            }
        products_list.append(all_product)
        
    return jsonify(products_list)

#Caso necessário fazer alteração no banco de dados sem rota use o Witch app.app_context para criar um contexto no código
        
app.run(debug=True)