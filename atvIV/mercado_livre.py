from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid

# Initialize the client
cloud_config = {
    'secure_connect_bundle': './secure-connect-mercado-livre.zip'
}
auth_provider = PlainTextAuthProvider('veKhwEcxAbIOWCSgjFoguAte', 'faLs3FMtivGLk_MojyfovCDFwCQZ3+ySTKn5FLMc_gLFEIaleLw6ZwYUOk6vtDP6CEU.LZT4EFgb4IFCgfCgo6nHPx2n2shFie3b-rv6rJmHxb,D7Z+wqvX01SlDajJ0')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

keyspace = "mercado_livre"

# criar a tabela favoritos
def create_favoritos_table():
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {keyspace}.favoritos (
            id UUID,
            usuario_id UUID,
            produto_id UUID,
            PRIMARY KEY (usuario_id, id)
        );
        """
    )
    print("Tabela favoritos recriada com sucesso!")

create_favoritos_table()

# Create tables
def create_tables():
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {keyspace}.usuarios (
            id UUID PRIMARY KEY,
            nome TEXT,
            email TEXT,
            senha TEXT,
            enderecos LIST<TEXT>
        );
        """
    )
    
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {keyspace}.vendedores (
            id UUID PRIMARY KEY,
            nome_loja TEXT,
            usuario_id UUID,
            reputacao DECIMAL
        );
        """
    )
    
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {keyspace}.produtos (
            id UUID PRIMARY KEY,
            nome TEXT,
            descricao TEXT,
            preco DECIMAL,
            estoque INT,
            vendedor_id UUID
        );
        """
    )
    
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {keyspace}.compras (
            id UUID PRIMARY KEY,
            quantidade INT,
            data_compra TIMESTAMP,
            usuario_id UUID,
            produto_id UUID
        );
        """
    )
    
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {keyspace}.favoritos (
            id UUID,
            usuario_id UUID,
            produto_id UUID,
            PRIMARY KEY (usuario_id, id)
        );
        """
    )

create_tables()

# Functions to manipulate data
def inserir_usuario(nome, email, senha, enderecos):
    user_id = uuid.uuid4()
    enderecos_list = enderecos.split(';')  # Assuming addresses are separated by semicolons
    session.execute(
        f"""
        INSERT INTO {keyspace}.usuarios (id, nome, email, senha, enderecos)
        VALUES ({user_id}, '{nome}', '{email}', '{senha}', {enderecos_list});
        """
    )
    print("Usuário inserido com sucesso!")

def exibir_usuarios():
    rows = session.execute(f"SELECT * FROM {keyspace}.usuarios;")
    for row in rows:
        print(row)

def excluir_usuario(user_id):
    session.execute(
        f"""
        DELETE FROM {keyspace}.usuarios
        WHERE id = {user_id};
        """
    )
    print("Usuário excluído com sucesso!")

def atualizar_usuario(user_id, nome, email, senha, enderecos):
    enderecos_list = enderecos.split(';')  # Assuming addresses are separated by semicolons
    session.execute(
        f"""
        UPDATE {keyspace}.usuarios
        SET nome = '{nome}', email = '{email}', senha = '{senha}', enderecos = {enderecos_list}
        WHERE id = {user_id};
        """
    )
    print("Usuário atualizado com sucesso!")

def inserir_vendedor(nome_loja, usuario_id, reputacao):
    vendedor_id = uuid.uuid4()
    session.execute(
        f"""
        INSERT INTO {keyspace}.vendedores (id, nome_loja, usuario_id, reputacao)
        VALUES ({vendedor_id}, '{nome_loja}', {usuario_id}, {reputacao});
        """
    )
    print("Vendedor inserido com sucesso!")

def exibir_vendedores():
    rows = session.execute(f"SELECT * FROM {keyspace}.vendedores;")
    for row in rows:
        print(row)

def excluir_vendedor(vendedor_id):
    session.execute(
        f"""
        DELETE FROM {keyspace}.vendedores
        WHERE id = {vendedor_id};
        """
    )
    print("Vendedor excluído com sucesso!")

def atualizar_vendedor(vendedor_id, nome_loja, usuario_id, reputacao):
    session.execute(
        f"""
        UPDATE {keyspace}.vendedores
        SET nome_loja = '{nome_loja}', usuario_id = {usuario_id}, reputacao = {reputacao}
        WHERE id = {vendedor_id};
        """
    )
    print("Vendedor atualizado com sucesso!")

def inserir_produto(nome, descricao, preco, estoque, vendedor_id):
    produto_id = uuid.uuid4()
    session.execute(
        f"""
        INSERT INTO {keyspace}.produtos (id, nome, descricao, preco, estoque, vendedor_id)
        VALUES ({produto_id}, '{nome}', '{descricao}', {preco}, {estoque}, {vendedor_id});
        """
    )
    print("Produto inserido com sucesso!")

def exibir_produtos():
    rows = session.execute(f"SELECT * FROM {keyspace}.produtos;")
    for row in rows:
        print(row)

def excluir_produto(produto_id):
    session.execute(
        f"""
        DELETE FROM {keyspace}.produtos
        WHERE id = {produto_id};
        """
    )
    print("Produto excluído com sucesso!")

def atualizar_produto(produto_id, nome, descricao, preco, estoque, vendedor_id):
    session.execute(
        f"""
        UPDATE {keyspace}.produtos
        SET nome = '{nome}', descricao = '{descricao}', preco = {preco}, estoque = {estoque}, vendedor_id = {vendedor_id}
        WHERE id = {produto_id};
        """
    )
    print("Produto atualizado com sucesso!")

def inserir_compra(quantidade, data_compra, usuario_id, produto_id):
    compra_id = uuid.uuid4()
    
    # Verificar o estoque atual do produto
    produto = session.execute(
        f"SELECT estoque FROM {keyspace}.produtos WHERE id = {produto_id};"
    ).one()
    
    if produto and produto.estoque >= quantidade:
        # Inserir a compra
        session.execute(
            f"""
            INSERT INTO {keyspace}.compras (id, quantidade, data_compra, usuario_id, produto_id)
            VALUES ({compra_id}, {quantidade}, '{data_compra}', {usuario_id}, {produto_id});
            """
        )
        
        # Atualizar o estoque do produto
        novo_estoque = produto.estoque - quantidade
        session.execute(
            f"""
            UPDATE {keyspace}.produtos
            SET estoque = {novo_estoque}
            WHERE id = {produto_id};
            """
        )
        print("Compra inserida com sucesso!")
    else:
        print("Estoque insuficiente para realizar a compra.")

def exibir_compras():
    rows = session.execute(f"SELECT * FROM {keyspace}.compras;")
    for row in rows:
        print(row)

def excluir_compra(compra_id):
    session.execute(
        f"""
        DELETE FROM {keyspace}.compras
        WHERE id = {compra_id};
        """
    )
    print("Compra excluída com sucesso!")

def atualizar_compra(compra_id, quantidade, data_compra, usuario_id, produto_id):
    session.execute(
        f"""
        UPDATE {keyspace}.compras
        SET quantidade = {quantidade}, data_compra = '{data_compra}', usuario_id = {usuario_id}, produto_id = {produto_id}
        WHERE id = {compra_id};
        """
    )
    print("Compra atualizada com sucesso!")

def inserir_favorito(usuario_id, produto_id):
    favorito_id = uuid.uuid4()
    session.execute(
        f"""
        INSERT INTO {keyspace}.favoritos (id, usuario_id, produto_id)
        VALUES ({favorito_id}, {usuario_id}, {produto_id});
        """
    )
    print("Favorito inserido com sucesso!")

def exibir_favoritos(usuario_id):
    rows = session.execute(f"SELECT * FROM {keyspace}.favoritos WHERE usuario_id = {usuario_id} ALLOW FILTERING;")
    for row in rows:
        print(row)

def excluir_favorito(favorito_id, usuario_id):
    session.execute(
        f"""
        DELETE FROM {keyspace}.favoritos
        WHERE usuario_id = {usuario_id} AND id = {favorito_id};
        """
    )
    print("Favorito excluído com sucesso!")

def menu():
    print("\n--- Menu Principal ---")
    print("1. Inserir usuário")
    print("2. Inserir vendedor")
    print("3. Inserir produto")
    print("4. Inserir compra")
    print("5. Inserir favorito")
    print("6. Exibir usuários")
    print("7. Exibir vendedores")
    print("8. Exibir produtos")
    print("9. Exibir compras")
    print("10. Exibir favoritos")
    print("11. Excluir usuário")
    print("12. Excluir vendedor")
    print("13. Excluir produto")
    print("14. Excluir compra")
    print("15. Remover favorito")
    print("16. Atualizar usuário")
    print("17. Atualizar vendedor")
    print("18. Atualizar produto")
    print("19. Atualizar compra")
    print("0. Sair")

    opcao = int(input("Escolha uma opção: "))
    
    if opcao == 1:
        nome = input("Nome do usuário: ")
        email = input("Email do usuário: ")
        senha = input("Senha do usuário: ")
        enderecos = input("Endereços do usuário (separados por ponto e vírgula): ")
        inserir_usuario(nome, email, senha, enderecos)
    elif opcao == 2:
        nome_loja = input("Nome da loja: ")
        usuario_id = input("ID do usuário: ")
        reputacao = float(input("Reputação: "))
        inserir_vendedor(nome_loja, usuario_id, reputacao)
    elif opcao == 3:
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco = float(input("Preço do produto: "))
        estoque = int(input("Estoque do produto: "))
        vendedor_id = input("ID do vendedor: ")
        inserir_produto(nome, descricao, preco, estoque, vendedor_id)
    elif opcao == 4:
        quantidade = int(input("Quantidade: "))
        data_compra = input("Data da compra (YYYY-MM-DD): ")
        usuario_id = input("ID do usuário: ")
        produto_id = input("ID do produto: ")
        inserir_compra(quantidade, data_compra, usuario_id, produto_id)
    elif opcao == 5:
        usuario_id = input("ID do usuário: ")
        produto_id = input("ID do produto: ")
        inserir_favorito(usuario_id, produto_id)
    elif opcao == 6:
        exibir_usuarios()
    elif opcao == 7:
        exibir_vendedores()
    elif opcao == 8:
        exibir_produtos()
    elif opcao == 9:
        exibir_compras()
    elif opcao == 10:
        usuario_id = input("ID do usuário: ")
        exibir_favoritos(usuario_id)
    elif opcao == 11:
        user_id = input("ID do usuário: ")
        excluir_usuario(user_id)
    elif opcao == 12:
        vendedor_id = input("ID do vendedor: ")
        excluir_vendedor(vendedor_id)
    elif opcao == 13:
        produto_id = input("ID do produto: ")
        excluir_produto(produto_id)
    elif opcao == 14:
        compra_id = input("ID da compra: ")
        excluir_compra(compra_id)
    elif opcao == 15:
        favorito_id = input("ID do favorito: ")
        usuario_id = input("ID do usuário: ")
        excluir_favorito(favorito_id, usuario_id)
    elif opcao == 16:
        user_id = input("ID do usuário: ")
        nome = input("Nome do usuário: ")
        email = input("Email do usuário: ")
        senha = input("Senha do usuário: ")
        enderecos = input("Endereços do usuário (separados por ponto e vírgula): ")
        atualizar_usuario(user_id, nome, email, senha, enderecos)
    elif opcao == 17:
        vendedor_id = input("ID do vendedor: ")
        nome_loja = input("Nome da loja: ")
        usuario_id = input("ID do usuário: ")
        reputacao = float(input("Reputação: "))
        atualizar_vendedor(vendedor_id, nome_loja, usuario_id, reputacao)
    elif opcao == 18:
        produto_id = input("ID do produto: ")
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco = float(input("Preço do produto: "))
        estoque = int(input("Estoque do produto: "))
        vendedor_id = input("ID do vendedor: ")
        atualizar_produto(produto_id, nome, descricao, preco, estoque, vendedor_id)
    elif opcao == 19:
        compra_id = input("ID da compra: ")
        quantidade = int(input("Quantidade: "))
        data_compra = input("Data da compra (YYYY-MM-DD): ")
        usuario_id = input("ID do usuário: ")
        produto_id = input("ID do produto: ")
        atualizar_compra(compra_id, quantidade, data_compra, usuario_id, produto_id)
    elif opcao == 0:
        print("Saindo...")
        return
    else:
        print("Opção inválida!")
    
    menu()

menu()