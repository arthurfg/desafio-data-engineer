# -*- coding: utf-8 -*-
import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
import logging
from pydantic import BaseModel, constr, ValidationError
from typing import Optional


## 
# Classes pydantic
##

class ValidadorEndereco(BaseModel):
    logradouro: str
    numero: int
    bairro: str
    cidade: str
    estado: str
    cep: constr(pattern=r'^\d{5}-\d{3}$')

class ValidadorUsuario(BaseModel):
    id: int
    nome: str
    idade: int
    email: constr(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    telefone: str
    endereco: ValidadorEndereco
##
# Modelos
#

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


##
# Funções
##

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


def validar_dados(json_file: str) -> None:
    """Valida dados do arquivo JSON

    Args:
         json_file (str): Caminho para o arquivo JSON contendo os dados a serem validados.
    """


    with open(json_file) as file:
        data = json.load(file)
    for item in data:
        try:
            obs = ValidadorUsuario(**item)
            print("Dados válidos:", obs)
        except ValidationError as e:
            print("Erro de validação:", e)

def inserir_dados(user: str, password: str, host: str, port: int, db: str, json_file: str) -> None:
    """Insere dados do arquivo JSON no banco de dados postgres.

    Args:
        user (str): Nome de usuário para a conexão com o banco de dados.
        password (str): Senha para a conexão com o banco de dados.
        host (str): Endereço do host do banco de dados.
        port (int): Número da porta do banco de dados.
        db (str): Nome do banco de dados.
        json_file (str): Caminho para o arquivo JSON contendo os dados a serem inseridos.
    """
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    Session = sessionmaker(bind=engine)
    session = Session()
    logging.info('Conexão estabelecida com sucesso, inserindo dados...')

    with open(json_file) as file:
        data = json.load(file)

    try:
        with session.begin():
            for item in data:
                usuario = session.query(Usuario).filter_by(id=item['id']).first()
                if usuario is None:
                    logging.info("Usuário não existe, criando novo usuário")
                    usuario = Usuario(nome=item['nome'], idade=item['idade'], email=item['email'], telefone=item['telefone'])
                    session.add(usuario)
                else:
                    logging.info("Usuário já existe, utilizando usuário existente")

                endereco = session.query(Endereco).filter_by(cep=item['endereco']['cep'], numero=item['endereco']['numero'], logradouro=item['endereco']['logradouro']).first()
                if endereco is None:
                    logging.info("Endereço não existe, criando novo endereço")
                    endereco = Endereco(logradouro=item['endereco']['logradouro'], numero=item['endereco']['numero'],
                                        bairro=item['endereco']['bairro'], cidade=item['endereco']['cidade'],
                                        estado=item['endereco']['estado'], cep=item['endereco']['cep'], usuario=usuario)
                 
                    session.add(endereco)
                else:
                    logging.info("Endereço já existe, utilizando endereço existente")

            logging.info("Inserção de dados concluída com sucesso!")
    except IntegrityError as e:
        session.rollback()
        logging.error(f"Erro de integridade ao inserir dados: {e}")
        raise e
    finally:
        session.commit()
        session.close()