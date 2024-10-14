import pymongo
from datetime import datetime
import uuid
import re
from bson import ObjectId

cliente = pymongo.MongoClient("mongodb+srv://eulauragabriel:12345@eulauragabriel.cmphovu.mongodb.net/?retryWrites=true&w=majority&appName=eulauragabriel")

db = cliente['mercado_livre']

clientes_collection = db["clientes"]
vendedores_collection = db["vendedores"]
produtos_collection = db["produtos"]
compras_collection = db["compras"]

def tudo_ok():
    input("\nOperação realizada com sucesso! Pressione Enter para continuar...")

def voltar_opcoes():
    input("\nPressione Enter para voltar ao menu...")
    menu()

def exibir_mensagem_sucesso(mensagem):
    print(f"\n{mensagem}")
    tudo_ok()
    voltar_opcoes()

def exibir_mensagem_erro(mensagem):
    print(f"\nErro: {mensagem}")
    voltar_opcoes()

def validar_email(email):
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(padrao, email) is not None

def validar_telefone(telefone):
    padrao = r'^\+?[1-9]\d{1,14}$'
    return re.match(padrao, telefone) is not None

def validar_preco(preco):
    try:
        float(preco)
        return True
    except ValueError:
        return False

def obter_endereco():
    return {
        "rua": input("Rua: "),
        "numero": input("Número: "),
        "bairro": input("Bairro: "),
        "cidade": input("Cidade: "),
        "estado": input("Estado: "),
        "cep": input("CEP: ")
    }

def obter_data_nascimento():
    while True:
        data_nascimento_str = input("Data de nascimento (dd/mm/yyyy): ")
        try:
            data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
            return data_nascimento
        except ValueError:
            print("Data inválida. Por favor, insira no formato dd/mm/yyyy.")

def cadastro_usuario():
    nome = input("Nome do usuário: ")
    sobrenome = input("Sobrenome: ")
    email = input("Email: ")
    if not validar_email(email):
        exibir_mensagem_erro("Email inválido.")
        return
    telefone = input("Telefone: ")
    if not validar_telefone(telefone):
        exibir_mensagem_erro("Telefone inválido.")
        return
    senha = input("Senha: ")

    enderecos = []
    while True:
        enderecos.append(obter_endereco())
        adicionar_mais = input("Deseja adicionar outro endereço? (s/n): ").strip().lower()
        if adicionar_mais != 's':
            break

    data_nascimento = obter_data_nascimento()

    usuario = {
        "nome": nome,
        "sobrenome": sobrenome,
        "email": email,
        "telefone": telefone,
        "senha": senha,
        "enderecos": enderecos,
        "data_nascimento": data_nascimento.strftime("%d/%m/%Y")
    }
    add_usuario(usuario)

def add_usuario(usuario):
    if clientes_collection.find_one({"email": usuario["email"]}):
        exibir_mensagem_erro("O email já está cadastrado.")
    else:
        clientes_collection.insert_one(usuario)
        exibir_mensagem_sucesso("Usuário cadastrado com sucesso!")

def cadastro_vendedor():
    nome = input("Nome do vendedor: ")
    sobrenome = input("Sobrenome: ")
    email = input("Email: ")
    if not validar_email(email):
        exibir_mensagem_erro("Email inválido.")
        return
    telefone = input("Telefone: ")
    if not validar_telefone(telefone):
        exibir_mensagem_erro("Telefone inválido.")
        return
    reputacao = float(input("Reputação (0 a 5): "))

    enderecos = []
    while True:
        enderecos.append(obter_endereco())
        adicionar_mais = input("Deseja adicionar outro endereço? (s/n): ").strip().lower()
        if adicionar_mais != 's':
            break

    data_nascimento = obter_data_nascimento()

    vendedor = {
        "nome": nome,
        "sobrenome": sobrenome,
        "email": email,
        "telefone": telefone,
        "reputacao": reputacao,
        "enderecos": enderecos,
        "data_nascimento": data_nascimento.strftime("%d/%m/%Y")
    }
    add_vendedor(vendedor)

def add_vendedor(vendedor):
    if vendedores_collection.find_one({"email": vendedor["email"]}):
        exibir_mensagem_erro("O email já está cadastrado.")
    else:
        vendedores_collection.insert_one(vendedor)
        exibir_mensagem_sucesso("Vendedor cadastrado com sucesso!")

def cadastro_produto():
    nome = input("Nome do produto: ")
    preco = input("Preço: ")
    if not validar_preco(preco):
        exibir_mensagem_erro("Preço inválido.")
        return
    preco = float(preco)
    descricao = input("Descrição: ")
    id_vendedor = input("ID do vendedor: ")
    estoque = int(input("Estoque: "))
    categoria = input("Categoria: ")
    data_adicao_favoritos = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    id_produto = str(uuid.uuid4())
    status_disponibilidade = "Disponível" if estoque > 0 else "Indisponível"

    produto = {
        "id_produto": id_produto,
        "nome": nome,
        "preco": preco,
        "descricao": descricao,
        "id_vendedor": id_vendedor,
        "estoque": estoque,
        "categoria": categoria,
        "status_disponibilidade": status_disponibilidade,
        "data_adicao_favoritos": data_adicao_favoritos
    }
    add_produto(produto)

def add_produto(produto):
    produtos_collection.insert_one(produto)
    exibir_mensagem_sucesso("Produto cadastrado com sucesso!")

def cadastro_compra():
    usuario_email = input("Email do usuário: ")
    id_produto = input("ID do produto: ") 
    quantidade = int(input("Quantidade: "))
    
    produto = produtos_collection.find_one({"_id": ObjectId(id_produto)})
    if not produto:
        exibir_mensagem_erro("Produto não encontrado!")
        return
    
    preco_unitario = produto["preco"]
    preco_total = preco_unitario * quantidade
    data_compra = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    status_compra = "Pendente"
    id_vendedor = produto["id_vendedor"]
    id_usuario = input("ID do usuário: ")

    compra = {
        "usuario_email": usuario_email,
        "produto_nome": produto["nome"],  
        "quantidade": quantidade,
        "preco_unitario": preco_unitario,
        "preco_total": preco_total,
        "data_compra": data_compra,
        "status_compra": status_compra,
        "id_vendedor": id_vendedor,
        "id_usuario": id_usuario,
        "id_produto": ObjectId(id_produto) 
    }
    add_compra(compra)

def add_compra(compra):
    compras_collection.insert_one(compra)
    exibir_mensagem_sucesso("Compra registrada com sucesso!")

def listagem_clientes():
    clientes = clientes_collection.find()
    for cliente in clientes:
        print(cliente)
    voltar_opcoes()

def listagem_vendedores():
    vendedores = vendedores_collection.find()
    for vendedor in vendedores:
        print(vendedor)
    voltar_opcoes()

def listagem_produtos():
    produtos = produtos_collection.find()
    for produto in produtos:
        print(produto)
    voltar_opcoes()

def listagem_compras():
    compras = compras_collection.find()
    for compra in compras:
        print(compra)
    voltar_opcoes()

def delecao_usuario(email):
    clientes_collection.delete_one({"email": email})
    exibir_mensagem_sucesso("Usuário deletado com sucesso!")

def delecao_vendedor(email):
    vendedores_collection.delete_one({"email": email})
    exibir_mensagem_sucesso("Vendedor deletado com sucesso!")

def delecao_produto(nome):
    produtos_collection.delete_one({"nome": nome})
    exibir_mensagem_sucesso("Produto deletado com sucesso!")

def delecao_compra(id_compra):
    compras_collection.delete_one({"_id": ObjectId(id_compra)})
    exibir_mensagem_sucesso("Compra deletada com sucesso!")

def atualizacao_usuario():
    emailI = input("Email do usuário à atualizar: ")
    print("Quais campos irá atualizar?")
    print("01 - Nome")
    print("02 - Sobrenome")
    print("03 - Email")
    print("04 - Telefone")
    print("05 - Endereços")
    print("06 - Data de Nascimento")
    print("07 - Senha")
    campos = input("Quais os campos? *modelo: 01,02,03: ")
    campos = campos.split(",")
    novosValores = {}
    for campo in campos:
        campo = int(campo)
        if campo == 1:
            nome = input("Novo nome: ")
            novosValores["nome"] = nome
        elif campo == 2:
            sobrenome = input("Novo sobrenome: ")
            novosValores["sobrenome"] = sobrenome
        elif campo == 3:
            email = input("Novo email: ")
            if not validar_email(email):
                exibir_mensagem_erro("Email inválido.")
                return
            novosValores["email"] = email
        elif campo == 4:
            telefone = input("Novo telefone: ")
            if not validar_telefone(telefone):
                exibir_mensagem_erro("Telefone inválido.")
                return
            novosValores["telefone"] = telefone
        elif campo == 5:
            enderecos = []
            while True:
                enderecos.append(obter_endereco())
                adicionar_mais = input("Deseja adicionar outro endereço? (s/n): ").strip().lower()
                if adicionar_mais != 's':
                    break
            novosValores["enderecos"] = enderecos
        elif campo == 6:
            data_nascimento = obter_data_nascimento()
            novosValores["data_nascimento"] = data_nascimento.strftime("%d/%m/%Y")
        elif campo == 7:
            senha = input("Nova senha: ")
            novosValores["senha"] = senha
    update_usuario(emailI, novosValores)

def update_usuario(emailI, novosValores):
    usuario_existente = clientes_collection.find_one({"email": emailI})
    if usuario_existente:
        clientes_collection.update_one({"email": emailI}, {"$set": novosValores})
        exibir_mensagem_sucesso("Usuário atualizado com sucesso!")
    else:
        exibir_mensagem_erro("Usuário não encontrado!")

def atualizacao_vendedor():
    emailI = input("Email do vendedor à atualizar: ")
    print("Quais campos irá atualizar?")
    print("01 - Nome")
    print("02 - Sobrenome")
    print("03 - Email")
    print("04 - Telefone")
    print("05 - Endereços")
    print("06 - Data de Nascimento")
    print("07 - Reputação")
    campos = input("Quais os campos? *modelo: 01,02,03: ")
    campos = campos.split(",")
    novosValores = {}
    for campo in campos:
        campo = int(campo)
        if campo == 1:
            nome = input("Novo nome: ")
            novosValores["nome"] = nome
        elif campo == 2:
            sobrenome = input("Novo sobrenome: ")
            novosValores["sobrenome"] = sobrenome
        elif campo == 3:
            email = input("Novo email: ")
            if not validar_email(email):
                exibir_mensagem_erro("Email inválido.")
                return
            novosValores["email"] = email
        elif campo == 4:
            telefone = input("Novo telefone: ")
            if not validar_telefone(telefone):
                exibir_mensagem_erro("Telefone inválido.")
                return
            novosValores["telefone"] = telefone
        elif campo == 5:
            enderecos = []
            while True:
                enderecos.append(obter_endereco())
                adicionar_mais = input("Deseja adicionar outro endereço? (s/n): ").strip().lower()
                if adicionar_mais != 's':
                    break
            novosValores["enderecos"] = enderecos
        elif campo == 6:
            data_nascimento = obter_data_nascimento()
            novosValores["data_nascimento"] = data_nascimento.strftime("%d/%m/%Y")
        elif campo == 7:
            reputacao = float(input("Nova reputação (0 a 5): "))
            novosValores["reputacao"] = reputacao
    update_vendedor(emailI, novosValores)

def update_vendedor(emailI, novosValores):
    vendedor_existente = vendedores_collection.find_one({"email": emailI})
    if vendedor_existente:
        vendedores_collection.update_one({"email": emailI}, {"$set": novosValores})
        exibir_mensagem_sucesso("Vendedor atualizado com sucesso!")
    else:
        exibir_mensagem_erro("Vendedor não encontrado!")

def atualizacao_produto():
    id_produto = input("ID do produto à atualizar: ") 
    print("Quais campos irá atualizar?")
    print("01 - Nome")
    print("02 - Preço")
    print("03 - Descrição")
    print("04 - ID do Vendedor")
    print("05 - Estoque")
    print("06 - Categoria")
    print("07 - Data de Adição aos Favoritos")
    campos = input("Quais os campos? *modelo: 01,02,03: ")
    campos = campos.split(",")
    novosValores = {}
    for campo in campos:
        campo = int(campo)
        if campo == 1:
            nome = input("Novo nome: ")
            novosValores["nome"] = nome
        elif campo == 2:
            preco = input("Novo preço: ")
            if not validar_preco(preco):
                exibir_mensagem_erro("Preço inválido.")
                return
            novosValores["preco"] = float(preco)
        elif campo == 3:
            descricao = input("Nova descrição: ")
            novosValores["descricao"] = descricao
        elif campo == 4:
            id_vendedor = input("Novo ID do vendedor: ")
            novosValores["id_vendedor"] = id_vendedor
        elif campo == 5:
            estoque = int(input("Novo estoque: "))
            novosValores["estoque"] = estoque
        elif campo == 6:
            categoria = input("Nova categoria: ")
            novosValores["categoria"] = categoria
        elif campo == 7:
            data_adicao_favoritos = input("Nova data de adição aos favoritos (dd/mm/yyyy hh:mm:ss): ")
            novosValores["data_adicao_favoritos"] = data_adicao_favoritos
    update_produto(id_produto, novosValores)

def update_produto(id_produto, novosValores):
    produto_existente = produtos_collection.find_one({"id_produto": id_produto})
    if produto_existente:
        produtos_collection.update_one({"id_produto": id_produto}, {"$set": novosValores})
        exibir_mensagem_sucesso("Produto atualizado com sucesso!")
    else:
        exibir_mensagem_erro("Produto não encontrado!")
        
def atualizacao_compra():
    id_compra = input("ID da compra à atualizar: ")  
    compra_existente = compras_collection.find_one({"_id": ObjectId(id_compra)})
    if not compra_existente:
        exibir_mensagem_erro("Compra não encontrada!")
        return

    print("Quais campos irá atualizar?")
    print("01 - Email do Usuário")
    print("02 - ID do Produto")
    print("03 - Quantidade")
    print("04 - Status da Compra")
    campos = input("Quais os campos? *modelo: 01,02,03: ")
    campos = campos.split(",")
    novosValores = {}
    for campo in campos:
        campo = int(campo)
        if campo == 1:
            usuario_email = input("Novo email do usuário: ")
            novosValores["usuario_email"] = usuario_email
        elif campo == 2:
            id_produto = input("Novo ID do produto: ")
            produto = produtos_collection.find_one({"_id": ObjectId(id_produto)})
            if not produto:
                exibir_mensagem_erro("Produto não encontrado!")
                return
            novosValores["id_produto"] = ObjectId(id_produto)
            novosValores["produto_nome"] = produto["nome"]
            novosValores["preco_unitario"] = produto["preco"]
        elif campo == 3:
            quantidade = int(input("Nova quantidade: "))
            novosValores["quantidade"] = quantidade
            novosValores["preco_total"] = compra_existente["preco_unitario"] * quantidade
        elif campo == 4:
            status_compra = input("Novo status da compra: ")
            novosValores["status_compra"] = status_compra
    update_compra(id_compra, novosValores)

def update_compra(id_compra, novosValores):
    compra_existente = compras_collection.find_one({"_id": ObjectId(id_compra)})
    if compra_existente:
        compras_collection.update_one({"_id": ObjectId(id_compra)}, {"$set": novosValores})
        exibir_mensagem_sucesso("Compra atualizada com sucesso!")
    else:
        exibir_mensagem_erro("Compra não encontrada!")

def adicionar_favorito():
    email_usuario = input("Email do usuário: ")
    id_produto = input("ID do produto: ")

    usuario = clientes_collection.find_one({"email": email_usuario})

    if not usuario:
        exibir_mensagem_erro("Usuário não encontrado!")
        return

    favoritos = usuario.get("favoritos", [])
    if id_produto in favoritos:
        exibir_mensagem_erro("Produto já está nos favoritos!")
        return

    favoritos.append(id_produto)
    clientes_collection.update_one({"email": email_usuario}, {"$set": {"favoritos": favoritos}})
    
    produto = produtos_collection.find_one({"_id": ObjectId(id_produto)})
    if produto:
        print(f"Produto adicionado aos favoritos: Nome: {produto['nome']}, Detalhes: {produto}")
    exibir_mensagem_sucesso("Produto adicionado aos favoritos com sucesso!")

def remover_favorito():
    email_usuario = input("Email do usuário: ")
    id_produto = input("ID do produto: ")

    usuario = clientes_collection.find_one({"email": email_usuario})

    if not usuario:
        exibir_mensagem_erro("Usuário não encontrado!")
        return

    favoritos = usuario.get("favoritos", [])
    if id_produto not in favoritos:
        exibir_mensagem_erro("Produto não está nos favoritos!")
        return

    favoritos.remove(id_produto)
    clientes_collection.update_one({"email": email_usuario}, {"$set": {"favoritos": favoritos}})
    exibir_mensagem_sucesso("Produto removido dos favoritos com sucesso!")

def listar_favoritos():
    email_usuario = input("Email do usuário: ")

    usuario = clientes_collection.find_one({"email": email_usuario})

    if not usuario:
        exibir_mensagem_erro("Usuário não encontrado!")
        return

    favoritos = usuario.get("favoritos", [])
    if not favoritos:
        print("Nenhum produto nos favoritos.")
        return

    print("Produtos favoritos:")
    for id_produto in favoritos:
        produto = produtos_collection.find_one({"_id": ObjectId(id_produto)})
        if produto:
            print(f"ID: {produto['_id']}, Nome: {produto['nome']}, Detalhes: {produto}")
    voltar_opcoes()

def menu():
    print("1. Cadastrar Usuário")
    print("2. Cadastrar Vendedor")
    print("3. Cadastrar Produto")
    print("4. Cadastrar Compra") 
    print("5. Listar Usuários")
    print("6. Listar Vendedores")
    print("7. Listar Produtos")
    print("8. Listar Compras")
    print("9. Atualizar Usuário")
    print("10. Atualizar Vendedor")
    print("11. Atualizar Produto")
    print("12. Atualizar Compra")
    print("13. Deletar Usuário")
    print("14. Deletar Vendedor")
    print("15. Deletar Produto")
    print("16. Deletar Compra")
    print("17. Adicionar Produto aos Favoritos")
    print("18. Remover Produto dos Favoritos")
    print("19. Listar Favoritos")
    print("20. Sair")
    
    escolha = input("Escolha uma opção: ")
    
    if escolha == "1":
        cadastro_usuario()
    elif escolha == "2":
        cadastro_vendedor()
    elif escolha == "3":
        cadastro_produto()
    elif escolha == "4":
        cadastro_compra()  
    elif escolha == "5":
        listagem_clientes()
    elif escolha == "6":
        listagem_vendedores()
    elif escolha == "7":
        listagem_produtos()
    elif escolha == "8":
        listagem_compras()
    elif escolha == "9":
        atualizacao_usuario()
    elif escolha == "10":
        atualizacao_vendedor()
    elif escolha == "11":
        atualizacao_produto()
    elif escolha == "12":
        atualizacao_compra()
    elif escolha == "13":
        email = input("Email do usuário a ser deletado: ")
        delecao_usuario(email)
    elif escolha == "14":
        email = input("Email do vendedor a ser deletado: ")
        delecao_vendedor(email)
    elif escolha == "15":
        nome = input("Nome do produto a ser deletado: ")
        delecao_produto(nome)
    elif escolha == "16":
        id_compra = input("ID da compra a ser deletada: ")
        delecao_compra(id_compra)
    elif escolha == "17":
        adicionar_favorito()
    elif escolha == "18":
        remover_favorito()
    elif escolha == "19":
        listar_favoritos()
    elif escolha == "20":
        print("Saindo...")
        exit()
    else:
        print("Opção inválida!")
        menu()

menu()