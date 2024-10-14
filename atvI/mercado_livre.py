from pymongo import MongoClient
from datetime import datetime

import pymongo

cliente = pymongo.MongoClient("mongodb+srv://eulauragabriel:12345@eulauragabriel.cmphovu.mongodb.net/?retryWrites=true&w=majority&appName=eulauragabriel")

db = cliente['mercado_livre']

usuarios = db['usuarios']
usuario_data = {
    "nome": "Laura",
    "email": "laura@gmail.com",
    "senha": "12345",
    "enderecos": [
        {"tipo":"Casa", "rua": "Cornelia Street", "numero": 22, "cidade": "São Paulo", "estado": "SP", "cep": "12345-678"},
        {"tipo":"Trabalho", "rua": "5th Avenue", "numero": 5, "cidade": "São Paulo", "estado": "SP", "cep": "98765-432"}
    ]
}
usuario_id = usuarios.insert_one(usuario_data).inserted_id

vendedores = db['vendedores']
vendedor_data = {
    "nome_loja": "Coquette Electronics",
    "usuario_id": usuario_id,  
    "reputacao": 5.0
}
vendedor_id = vendedores.insert_one(vendedor_data).inserted_id

produtos = db['produtos']
produto_data = {
    "nome": "Notebook Gamer (Rosa) 🎀",
    "descricao": "Notebook para jogos de garota",
    "preco": 5000.00,
    "estoque": 10,
    "vendedor_id": vendedor_id 
}
produto_id = produtos.insert_one(produto_data).inserted_id

compras = db['compras']
compra_data = {
    "quantidade": 1,
    "data_compra": datetime.now(),
    "usuario_id": usuario_id,  
    "produto_id": produto_id 
}
compra_id = compras.insert_one(compra_data).inserted_id

favoritos = db['favoritos']
favorito_data = {
    "usuario_id": usuario_id,  
    "produto_id": produto_id  
}
favorito_id = favoritos.insert_one(favorito_data).inserted_id

print("Dados inseridos com sucesso!")
