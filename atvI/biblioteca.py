from pymongo import MongoClient
from datetime import datetime

import pymongo

cliente = pymongo.MongoClient("mongodb+srv://eulauragabriel:12345@eulauragabriel.cmphovu.mongodb.net/?retryWrites=true&w=majority&appName=eulauragabriel")

db = cliente['biblioteca']

usuarios = db['usuarios']
usuario_data = {
    "nome": "Laura",
    "email": "laura@gmail.com",
    "telefone": "123456789",
    "endereco": "Rua Cornelia, 22, São Paulo - SP"
}
usuario_id = usuarios.insert_one(usuario_data).inserted_id

autores = db['autores']
autor_data = {
    "nome": "Holly Black",
    "nacionalidade": "Americana"
}
autor_id = autores.insert_one(autor_data).inserted_id

editoras = db['editoras']
editora_data = {
    "nome": "Editora Blablabla",
}
editora_id = editoras.insert_one(editora_data).inserted_id

livros = db['livros']

livro_hp_data = {
    "titulo": "Harry Potter e a Pedra Filosofal",
    "isbn": "978-85-325-1110-8",
    "ano_publicacao": 1997,
    "genero": "Fantasia",
    "autor_id": autor_id,
    "editora_id": editora_id
}
livro_hp_id = livros.insert_one(livro_hp_data).inserted_id

livro_pc_data = {
    "titulo": "Príncipe Cruel",
    "isbn": "978-85-7683-357-0",
    "ano_publicacao": 2018,
    "genero": "Fantasia",
    "autor_id": autor_id, 
    "editora_id": editora_id 
}
livro_pc_id = livros.insert_one(livro_pc_data).inserted_id

exemplares = db['exemplares']

exemplar_hp_data = {
    "livro_id": livro_hp_id,
    "disponibilidade": True
}
exemplar_hp_id = exemplares.insert_one(exemplar_hp_data).inserted_id

exemplar_pc_data = {
    "livro_id": livro_pc_id,
    "disponibilidade": True
}
exemplar_pc_id = exemplares.insert_one(exemplar_pc_data).inserted_id

emprestimos = db['emprestimos']

emprestimo_hp_data = {
    "usuario_id": usuario_id,
    "exemplar_id": exemplar_hp_id,
    "data_emprestimo": datetime.now(),
    "data_devolucao": None,
    "status": "Em aberto"
}
emprestimo_hp_id = emprestimos.insert_one(emprestimo_hp_data).inserted_id

emprestimo_pc_data = {
    "usuario_id": usuario_id,
    "exemplar_id": exemplar_pc_id,
    "data_emprestimo": datetime.now(),
    "data_devolucao": None,
    "status": "Em aberto"
}
emprestimo_pc_id = emprestimos.insert_one(emprestimo_pc_data).inserted_id

print("Dados inseridos com sucesso na biblioteca!")
