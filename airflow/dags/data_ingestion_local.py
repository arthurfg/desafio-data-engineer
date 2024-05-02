# -*- coding: utf-8 -*-
import os

from datetime import datetime

from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from ingestion_script import criar_tabelas, inserir_dados, validar_dados



PG_HOST = os.getenv('PG_HOST')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')

workflow = DAG(
    "CompleteIngestionDag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2024, 4, 29),
)


JSON_URL = "https://file.notion.so/f/f/94b34e22-0d51-4e8e-bb6f-7062c3c60ee4/78abfe9b-caf1-436c-ac60-5d61fe61cb6b/json_for_case.json?id=1cc9ec60-a871-421a-84a5-ef6952989582&table=block&spaceId=94b34e22-0d51-4e8e-bb6f-7062c3c60ee4&expirationTimestamp=1714629600000&signature=elDBlY49AsjuJOsxBJZPyzc1CXs0P_GSJXdYkUiw3F8&downloadName=json_for_case.json"
AIRFLOW_HOME = "/opt/airflow/"
OUTPUT_FILE_TEMPLATE = '/opt/airflow/data.json'
TABLE_NAME_TEMPLATE = 'clients'

with workflow:
    download_json = BashOperator(
        task_id='download_json',
        bash_command=f"curl '{JSON_URL}' > /opt/airflow/data.json"
    )
    create_tables = PythonOperator(
        task_id="create_tables",
        python_callable=criar_tabelas,
        op_kwargs=dict(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            db=PG_DATABASE,
        ),
    )

    validation_task = PythonOperator(
        task_id="validate",
        python_callable=validar_dados,
        op_kwargs=dict(
            json_file=OUTPUT_FILE_TEMPLATE,
        ),
    )
    ingest_task = PythonOperator(
        task_id="ingest",
        python_callable=inserir_dados,
        op_kwargs=dict(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            db=PG_DATABASE,
            json_file=OUTPUT_FILE_TEMPLATE,
        ),
    )

    download_json >> validation_task >> create_tables >> ingest_task