# -*- coding: utf-8 -*-
import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
import logging


Base = declarative_base()


class Usuario(Base):
    """Classe que representa a tabela 'usuarios' no banco de dados."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    idade = Column(Integer)
    email = Column(String)
    telefone = Column(String)

    enderecos = relationship("Endereco", back_populates="usuario")


class Endereco(Base):
    """Classe que representa a tabela 'enderecos' no banco de dados."""

    __tablename__ = "enderecos"

    id = Column(Integer, primary_key=True)
    logradouro = Column(String)
    numero = Column(Integer)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    cep = Column(String)
    user_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="enderecos")


def criar_tabelas(user: str, password: str, host: str, port: int, db: str) -> None:
    """Cria as tabelas no banco de dados se elas não existirem.

    Args:
        user (str): Nome de usuário para a conexão com o banco de dados.
        password (str): Senha para a conexão com o banco de dados.
        host (str): Endereço do host do banco de dados.
        port (int): Número da porta do banco de dados.
        db (str): Nome do banco de dados.
    """

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    Base.metadata.create_all(engine)
    logging.info("Tabelas criadas com sucesso!")


def inserir_dados(
    user: str, password: str, host: str, port: int, db: str, json_file: str
) -> None:
    """Insere dados do arquivo JSON no banco de dados postgres.

    Args:
        user (str): Nome de usuário para a conexão com o banco de dados.
        password (str): Senha para a conexão com o banco de dados.
        host (str): Endereço do host do banco de dados.
        port (int): Número da porta do banco de dados.
        db (str): Nome do banco de dados.
        json_file (str): Caminho para o arquivo JSON contendo os dados a serem inseridos.
    """
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    Session = sessionmaker(bind=engine)

    try:
        with open(json_file) as file:
            data = json.load(file)

        session = Session()
        logging.info("Conexão estabelecida com sucesso, inserindo dados...")

        for item in data:
            usuario = session.query(Usuario).filter_by(id=item["id"]).first()
            if usuario is None:
                logging.info("Usuário não existe, criando novo usuário")
                usuario = Usuario(
                    nome=item["nome"],
                    idade=item["idade"],
                    email=item["email"],
                    telefone=item["telefone"],
                )
                session.add(usuario)

            endereco = (
                session.query(Endereco)
                .filter_by(
                    cep=item["endereco"]["cep"], numero=item["endereco"]["numero"]
                )
                .first()
            )
            if endereco is None:
                logging.info("Endereço não existe, criando novo endereço")
                endereco = Endereco(
                    logradouro=item["endereco"]["logradouro"],
                    numero=item["endereco"]["numero"],
                    bairro=item["endereco"]["bairro"],
                    cidade=item["endereco"]["cidade"],
                    estado=item["endereco"]["estado"],
                    cep=item["endereco"]["cep"],
                    usuario=usuario,
                )
                session.add(endereco)

        session.commit()
        logging.info("Inserção de dados concluída com sucesso!")
    except (IntegrityError, Exception) as e:
        session.rollback()
        logging.error(f"Erro ao inserir dados: {e}")
        raise e
    finally:
        session.close()
