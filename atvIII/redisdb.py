import json
from datetime import datetime
import pymongo
import redis
import uuid  # Importando o módulo UUID
from bson import ObjectId, Decimal128

# Conexão com MongoDB
try:
    cliente = pymongo.MongoClient("mongodb+srv://eulauragabriel:12345@eulauragabriel.cmphovu.mongodb.net/?retryWrites=true&w=majority&appName=eulauragabriel")
    db = cliente.mercado_livre
    clientes_collection = db["clientes"]
    produtos_collection = db["produtos"] 
    compras_collection = db["compras"] 
    print("Conexão com MongoDB estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao conectar com MongoDB: {e}")

# Conexão com Redis
conR = redis.Redis(host='redis-11437.c98.us-east-1-4.ec2.redns.redis-cloud.com', port=11437, password='sf0toLWQNBrIf5zZZ3I73t1Fy1jEW6U3')

# Função para serializar JSON
def json_serializer(obj):
    if isinstance(obj, uuid.UUID):  # Serializando UUID
        return str(obj)
    elif isinstance(obj, Decimal128):
        return str(obj.to_decimal())
    else:
        return json.JSONEncoder().default(obj)

# Função para salvar no Redis
def salvar_redis(emailI, valores, tipo):
    StringObjeto = json.dumps(valores, default=json_serializer)
    conR.set(f'{emailI}:{tipo}', StringObjeto, ex=60)
    print(f"Salvo no Redis como {emailI}:{tipo}!")

# Função para retirar itens do MongoDB e colocar no Redis
def retirar_do_mongo_para_redis(email):
    try:
        cliente = clientes_collection.find_one({"email": email})
        
        if cliente:
            favoritos = cliente.get("favoritos", [])

            itens = []
            ids_adicionados = set() 

            for produto_id in favoritos[:3]:  
                try:
                    produto = produtos_collection.find_one({"_id": ObjectId(produto_id)})
                    
                    if produto and produto_id not in ids_adicionados:
                        print(f"Produto encontrado: {produto}") 
                        itens.append({
                            "id_produto": str(produto.get("_id")),
                            "nome_produto": produto.get("nome", "Produto sem nome"),
                            "preco": produto.get("preco", 0)  
                        })
                        ids_adicionados.add(produto_id)
                    else:
                        print(f"Produto não encontrado ou já adicionado com ID: {produto_id}")
                except Exception as e:
                    print(f"Erro ao buscar produto com ID {produto_id}: {e}")
            
            salvar_redis(email, itens, "itens")
        else:
            print("Cliente não encontrado!")
    except Exception as e:
        print(f"Erro ao retirar do MongoDB para Redis: {e}")

# Função para manipular itens no Redis
def manipular_itens_no_redis(email):
    chave = f'{email}:itens'
    
    if conR.exists(chave):
        itens_json = conR.get(chave)
        itens = json.loads(itens_json)
        
        if itens:
            print("Itens carregados:")
            for idx, item in enumerate(itens):
                print(f"{idx + 1}. ID: {item['id_produto']}, Nome: {item['nome_produto']}, Preço: {item['preco']}")
            
            escolha = int(input("Digite o número do item que deseja alterar o preço (0 para cancelar): "))
            if 1 <= escolha <= len(itens):
                novo_preco = float(input("Novo preço: "))
                itens[escolha - 1]["preco"] = novo_preco
                conR.set(chave, json.dumps(itens, default=json_serializer))
                print(f"Item atualizado: {itens[escolha - 1]}")
            else:
                print("Operação cancelada.")
        else:
            print("Nenhum item encontrado no Redis.")
    else:
        print("Não há itens armazenados no Redis!")

# Função para devolver os itens manipulados de volta ao MongoDB
def devolver_para_mongo(email):
    chave = f'{email}:itens'
    
    if conR.exists(chave):
        itens_json = conR.get(chave)
        itens = json.loads(itens_json)
        
        cliente = clientes_collection.find_one({"email": email})
        if cliente:
            favoritos = cliente.get("favoritos", [])
            
            novos_favoritos = favoritos[:3] + [item['id_produto'] for item in itens if item['id_produto'] not in favoritos]
            
            clientes_collection.update_one({"email": email}, {"$set": {"favoritos": novos_favoritos}})
            
            for item in itens:
                produtos_collection.update_one(
                    {"_id": ObjectId(item['id_produto'])},  
                    {"$set": {"preco": item['preco']}},
                    upsert=False 
                )
            
            print("Itens devolvidos ao MongoDB!")
        else:
            print("Cliente não encontrado no MongoDB!")
    else:
        print("Não há itens armazenados no Redis para devolver!")
        
# Função para exibir o menu de opções
def opcoes_usuario(email):
    while True:
        print("Qual opção deseja?")
        print("01 - Retirar itens do MongoDB para o Redis")
        print("02 - Manipular itens no Redis")
        print("03 - Devolver itens ao MongoDB")
        print("00 - Sair")
        opcao = int(input("Opção: "))

        if opcao == 0:
            print("Beijos :)")
            break
        elif opcao == 1:
            retirar_do_mongo_para_redis(email)
        elif opcao == 2:
            manipular_itens_no_redis(email)
        elif opcao == 3:
            devolver_para_mongo(email)
        else:
            print("Opção inválida, tente novamente.")

# Função de login
def login():
    print("Login:")
    email = input("Email: ")
    senha = input("Senha: ")

    if cliente:
        data_e_hora_atuais = datetime.now()
        data = data_e_hora_atuais.strftime('%d-%m-%Y %H:%M')
        conR.set(f'{email}:sessao', f"senha:{senha}")
        conR.expire(f'{email}:sessao', 120)
        print("Login realizado!")
        return email
    else:
        print("Email ou senha incorretos!")
        return None

# Verificar se o usuário está logado
def verificar_sessao(email):
    return conR.exists(f'{email}:sessao')

# Executando o login e verificando a sessão
email = login()
if email:
    if verificar_sessao(email):
        opcoes_usuario(email)
    else:
        print("Sessão expirada. Faça login novamente.")
else:
    print("Falha no login.")