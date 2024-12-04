from neo4j import GraphDatabase

# Conexão com o Neo4j
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]
        
# Conectar ao Neo4j
uri = "neo4j+s://1e7a7db5.databases.neo4j.io"  
user = "neo4j"  
password = "n53xGytuUNxbuWtIq487JIFvfDYHDhUrRZJNpX2NBts" 

conn = Neo4jConnection(uri, user, password)

# Função para inserir usuário
def inserir_usuario(conn, nome, email):
    # Verificar se o usuário já existe
    query = """
    MATCH (u:Usuario {email: $email})
    RETURN u
    """
    parameters = {"email": email}
    result = conn.query(query, parameters)
    if result:
        print("Erro: Usuário com este email já existe.")
        return

    # Inserir novo usuário
    query = """
    CREATE (u:Usuario {id: apoc.create.uuid(), nome: $nome, email: $email})
    RETURN u
    """
    result = conn.query(query, {"nome": nome, "email": email})
    print("Usuário inserido com sucesso!")
    for record in result:
        print(record)

# Função para buscar usuário por email
def buscar_usuario(conn, email):
    query = """
    MATCH (u:Usuario {email: $email})
    RETURN u
    """
    parameters = {"email": email}
    result = conn.query(query, parameters)
    print("Usuário encontrado:")
    for record in result:
        print(record)

# Função para inserir vendedor
def inserir_vendedor(conn, nome_loja, email, reputacao):
    # Verificar se o vendedor já existe
    query = """
    MATCH (v:Vendedor {email: $email})
    RETURN v
    """
    parameters = {"email": email}
    result = conn.query(query, parameters)
    if result:
        print("Erro: Vendedor com este email já existe.")
        return

    # Verificar se o usuário existe
    query = """
    MATCH (u:Usuario {email: $email})
    RETURN u
    """
    result = conn.query(query, parameters)
    if not result:
        print("Erro: Usuário com este email não existe.")
        return

    # Inserir novo vendedor
    query = """
    MATCH (u:Usuario {email: $email})
    CREATE (v:Vendedor {id: apoc.create.uuid(), nome_loja: $nome_loja, email: $email, reputacao: $reputacao})-[:PERTENCE_A]->(u)
    RETURN v
    """
    result = conn.query(query, {"nome_loja": nome_loja, "email": email, "reputacao": reputacao})
    print("Vendedor inserido com sucesso!")
    for record in result:
        print(record)

# Função para buscar vendedor por email
def buscar_vendedor(conn, email):
    query = """
    MATCH (v:Vendedor {email: $email})
    RETURN v
    """
    parameters = {"email": email}
    result = conn.query(query, parameters)
    print("Vendedor encontrado:")
    for record in result:
        print(record)

# Função para inserir produto
def inserir_produto(conn, nome, descricao, preco, estoque, vendedor_email):
    query = """
    MATCH (v:Vendedor {email: $vendedor_email})
    CREATE (p:Produto {id: apoc.create.uuid(), nome: $nome, descricao: $descricao, preco: $preco, estoque: $estoque})-[:VENDIDO_POR]->(v)
    RETURN p
    """
    parameters = {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "vendedor_email": vendedor_email}
    result = conn.query(query, parameters)
    print("Produto inserido com sucesso!")
    for record in result:
        print(record)

# Função para buscar produto por ID
def buscar_produto(conn, produto_id):
    query = """
    MATCH (p:Produto {id: $produto_id})
    RETURN p
    """
    parameters = {"produto_id": produto_id}
    result = conn.query(query, parameters)
    print("Produto encontrado:")
    for record in result:
        print(record)

# Função para inserir compra
def inserir_compra(conn, quantidade, data_compra, usuario_email, produto_id):
    # Verificar o estoque atual do produto
    query = """
    MATCH (p:Produto {id: $produto_id})
    RETURN p.estoque AS estoque
    """
    parameters = {"produto_id": produto_id}
    result = conn.query(query, parameters)
    if not result:
        print("Erro: Produto não encontrado.")
        return

    estoque_atual = result[0]['estoque']
    if estoque_atual < quantidade:
        print("Erro: Estoque insuficiente.")
        return

    # Inserir a compra
    query = """
    MATCH (u:Usuario {email: $usuario_email}), (p:Produto {id: $produto_id})
    CREATE (c:Compra {id: apoc.create.uuid(), quantidade: $quantidade, data_compra: $data_compra})-[:COMPRADO_POR]->(u),
           (c)-[:COMPRA_DE]->(p)
    RETURN c
    """
    parameters = {"quantidade": quantidade, "data_compra": data_compra, "usuario_email": usuario_email, "produto_id": produto_id}
    result = conn.query(query, parameters)
    print("Compra inserida com sucesso!")
    for record in result:
        print(record)

    # Atualizar o estoque do produto
    novo_estoque = estoque_atual - quantidade
    query = """
    MATCH (p:Produto {id: $produto_id})
    SET p.estoque = $novo_estoque
    RETURN p
    """
    parameters = {"produto_id": produto_id, "novo_estoque": novo_estoque}
    result = conn.query(query, parameters)
    print("Estoque do produto atualizado com sucesso!")
    for record in result:
        print(record)

# Função para buscar compra por email do usuário
def buscar_compra(conn, usuario_email):
    query = """
    MATCH (u:Usuario {email: $usuario_email})<-[:COMPRADO_POR]-(c:Compra)-[:COMPRA_DE]->(p:Produto)
    RETURN c, p
    """
    parameters = {"usuario_email": usuario_email}
    result = conn.query(query, parameters)
    print("Compras encontradas:")
    for record in result:
        print(record)

# Função para inserir favorito
def inserir_favorito(conn, usuario_email, produto_id):
    query = """
    MATCH (u:Usuario {email: $usuario_email}), (p:Produto {id: $produto_id})
    CREATE (u)-[:FAVORITA]->(p)
    RETURN u, p
    """
    parameters = {"usuario_email": usuario_email, "produto_id": produto_id}
    result = conn.query(query, parameters)
    print("Favorito inserido com sucesso!")
    for record in result:
        print(record)

# Função para buscar favoritos por email do usuário
def buscar_favoritos(conn, usuario_email):
    query = """
    MATCH (u:Usuario {email: $usuario_email})-[:FAVORITA]->(p:Produto)
    RETURN p
    """
    parameters = {"usuario_email": usuario_email}
    result = conn.query(query, parameters)
    print("Favoritos encontrados:")
    for record in result:
        print(record)

# Função para buscar todos os usuários
def buscar_todos_usuarios(conn):
    query = """
    MATCH (u:Usuario)
    RETURN u
    """
    result = conn.query(query)
    print("Usuários encontrados:")
    for record in result:
        print(record)

# Função para buscar todos os vendedores
def buscar_todos_vendedores(conn):
    query = """
    MATCH (v:Vendedor)
    RETURN v
    """
    result = conn.query(query)
    print("Vendedores encontrados:")
    for record in result:
        print(record)

# Função para buscar todos os produtos
def buscar_todos_produtos(conn):
    query = """
    MATCH (p:Produto)
    RETURN p
    """
    result = conn.query(query)
    print("Produtos encontrados:")
    for record in result:
        print(record)
def menu():
    print("\n--- Menu Principal ---")
    print("1. Inserir usuário")
    print("2. Buscar usuário")
    print("3. Inserir vendedor")
    print("4. Buscar vendedor")
    print("5. Inserir produto")
    print("6. Buscar produto")
    print("7. Inserir compra")
    print("8. Buscar compras de um usuário")
    print("9. Inserir favorito")
    print("10. Buscar favoritos de um usuário")
    print("11. Buscar todos os usuários")
    print("12. Buscar todos os vendedores")
    print("13. Buscar todos os produtos")
    print("0. Sair")

    opcao = int(input("Escolha uma opção: "))
    
    if opcao == 1:
        nome = input("Nome do usuário: ")
        email = input("Email do usuário: ")
        inserir_usuario(conn, nome, email)
    elif opcao == 2:
        email = input("Email do usuário: ")
        buscar_usuario(conn, email)
    elif opcao == 3:
        nome_loja = input("Nome da loja: ")
        email = input("Email do usuário: ")
        reputacao = float(input("Reputação: "))
        inserir_vendedor(conn, nome_loja, email, reputacao)
    elif opcao == 4:
        email = input("Email do vendedor: ")
        buscar_vendedor(conn, email)
    elif opcao == 5:
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco = float(input("Preço do produto: "))
        estoque = int(input("Estoque do produto: "))
        vendedor_email = input("Email do vendedor: ")
        inserir_produto(conn, nome, descricao, preco, estoque, vendedor_email)
    elif opcao == 6:
        produto_id = input("ID do produto: ")
        buscar_produto(conn, produto_id)
    elif opcao == 7:
        quantidade = int(input("Quantidade: "))
        data_compra = input("Data da compra (YYYY-MM-DD): ")
        usuario_email = input("Email do usuário: ")
        produto_id = input("ID do produto: ")
        inserir_compra(conn, quantidade, data_compra, usuario_email, produto_id)
    elif opcao == 8:
        email = input("Email do usuário: ")
        buscar_compra(conn, email)
    elif opcao == 9:
        usuario_email = input("Email do usuário: ")
        produto_id = input("ID do produto: ")
        inserir_favorito(conn, usuario_email, produto_id)
    elif opcao == 10:
        email = input("Email do usuário: ")
        buscar_favoritos(conn, email)
    elif opcao == 11:
        buscar_todos_usuarios(conn)
    elif opcao == 12:
        buscar_todos_vendedores(conn)
    elif opcao == 13:
        buscar_todos_produtos(conn)
    elif opcao == 0:
        print("Saindo...")
        conn.close()
        return
    else:
        print("Opção inválida!")
    
    menu()

menu()