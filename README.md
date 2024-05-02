# Desafio Data Engineer 2024 - Capim
### Arthur Gusmão

## Objetivo
Resolver os problemas propostos pelo desafio utilizando uma arquitetura simples, resiliente e escalável.

## Visão Geral
### Modelagem
Por existir a possibilidade de uma relação _1:n_ entre a entidade `usuário` e a entidade `endereço`, decidi modelar os dados em duas tabelas, uma para usuários e outra para endereços. Ao alterar a modelagem dos dados, as tabelas ficam na Terceira Forma Normal, melhorando a estrutura do banco de dados.

<img src="https://github.com/arthurfg/desafio-capim/assets/62671380/3f4890f5-b14f-4538-8fa8-1319b8972919" width="600" height="600">

### Infraestrutura

- **Docker**: Conteinerização

- **Airflow**: Orquestração

- **Postgres**: Banco de Dados

- **PgAdmin**: Interface gráfica/administrador do banco de dados

- **Metabase**: Dashboard

Todos os serviços utilizados no desafio estão dockerizados, garantindo reprodutibilidade e escalabilidade. O ambiente é simples e está dividido em dois elementos principais: o **banco de dados** e o **orquestrador**. A divisão dos ambientes foi feita através dos arquivos `docker-compose.yaml`, o primeiro arquivo, referente ao ambiente do Airflow, centraliza todos os serviços necessários para a sua execução (banco de dados, variáveis de ambiente, requirements, webserver e etc) e o segundo, referente ao ambiente do Postgres, centraliza os serviços necessários para a sua execução além de criar as conexões necessárias entre o banco, o PgAdmin e o Metabase.

Uma observação importante é que precisa haver uma conexão ativa entre os dois _docker composes_, para que o Airflow consiga se comunicar com o banco Postgres e vice-versa. Para isso, foi criado um arquivo `.env` contendo as variáveis de ambiente necessárias para o Airflow se comunicar com o Postgres, além da criação da conexão entre o contêiner do banco e o contêiner do worker do Airflow (que é responsável por executar as DAGs).

Exemplo do arquivo `.env`:
```
AIRFLOW_UID=501
PG_HOST=pgdatabase
PG_USER=root
PG_PASSWORD=root
PG_PORT=5432
PG_DATABASE=capim
```

Exemplo da conexão no arquivo `postgres/docker-compose.yaml`:
```yml

networks:
  airflow:
    external:
      name: airflow_default
```
### Diagrama

![diagram-export-01-05-2024-22_51_28](https://github.com/arthurfg/desafio-capim/assets/62671380/d841e880-b9e7-4af0-a1c6-06b4b4c50ab6)

### Fluxo dos dados

O airflow executa a DAG com o nome de `CompleteIngestionDag`, que está no arquivo `./airflow/data_ingestion_local.py`. Ela possui 4 tasks que fazem o processo de extração -> validação -> criação das tabelas -> carregamento dos dados no banco. Os dados brutos são extraídos da URL e salvos em um arquivo `data.json`, em seguida passam pela validação feita através do `pydantic`, que verifica o tipo dos dados, o schema e outras condições específicas (como o formato dos dados da coluna `cep`, por exemplo). Caso passem na validação, as tabelas são criadas -- caso não existam --  e os dados são carregados.

Visando resolver o problema do desafio, uma lógica foi criada para impossibilitar o carregamento de dados duplicados no banco. O fluxo confere a existência da chave única na tabela de usuários e a existência do conjunto `cep ~ logradouro ~ número` na tabela de endereços, para todas as observações, e só insere os novos dados se eles forem únicos e se não existirem previamente no banco. Esse processo garante a integridade e a atomicidade dos dados.

<img width="1385" alt="Captura de Tela 2024-05-01 às 23 42 03" src="https://github.com/arthurfg/desafio-capim/assets/62671380/70dc31c9-07ac-4ef5-a6a4-f17ffa0af37f">

### Dashboard
<img width="1074" alt="Captura de Tela 2024-05-01 às 23 47 55" src="https://github.com/arthurfg/desafio-capim/assets/62671380/690561e8-02ed-417e-902c-89608a76b334">
<img width="1094" alt="Captura de Tela 2024-05-01 às 23 48 04" src="https://github.com/arthurfg/desafio-capim/assets/62671380/c973a227-2949-4a9e-8576-440858d5bb12">

