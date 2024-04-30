import os

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

JSON_URL = 'https://file.notion.so/f/f/94b34e22-0d51-4e8e-bb6f-7062c3c60ee4/78abfe9b-caf1-436c-ac60-5d61fe61cb6b/json_for_case.json?id=1cc9ec60-a871-421a-84a5-ef6952989582&table=block&spaceId=94b34e22-0d51-4e8e-bb6f-7062c3c60ee4&expirationTimestamp=1714536000000&signature=Ptcz-ETIFf_990qIMBZLKO_IXPPWf9gR0WRNPcLYy8o&downloadName=json_for_case.json'
AIRFLOW_HOME = "/opt/airflow/"
local_workflow = DAG(
    "LocalIngestionDag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2024, 4, 29)
)

with local_workflow:
    wget_task = BashOperator(
        task_id='wget',
        bash_command='echo "hello arthur gusmao"'
    )

    download_json = BashOperator(
        task_id='download_json',
        bash_command=f"curl '{JSON_URL}' > {AIRFLOW_HOME}data.json"
    )    

    ls_task = BashOperator(
        task_id='ls',
        bash_command='ls'
    )    

    wget_task >> download_json >> ls_task