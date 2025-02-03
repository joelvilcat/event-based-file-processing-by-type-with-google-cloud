import json
import csv
from google.cloud import storage
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

def process_txt_files(request):
    # Esta función se activa por un POST HTTP (Push endpoint) desde Pub/Sub
    request_json = request.get_json()
    if not request_json:
        print("No Pub/Sub message received")
        return ("Bad Request", 400)

    pubsub_message = request_json.get("message")
    if not pubsub_message:
        print("No message field in request")
        return ("Bad Request", 400)

    # Atributos metadata
    attributes = pubsub_message.get("attributes", {})
    object_id = attributes.get("objectId", "")
    bucket_id = attributes.get("bucketId", "")

    # Ajusta estos valores según tu proyecto
    project_id = "project-learning-gcp-data"            # Reemplaza con tu Project ID
    dataset_id = "users"                                # Reemplaza con el dataset donde guardarás la tabla
    table_id   = "personal_information_of_users"        # Reemplaza con el nombre de tu tabla

    # Detectar la extensión del archivo
    extension = object_id.split('.')[-1].lower()  # Extrae la extensión (csv, txt, etc.)
    
    if extension in ["csv", "txt"]:
        print(f"Procesando archivo {object_id} (extensión: {extension})")

        # 1. Descarga el contenido del archivo desde GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_id)
        blob = bucket.blob(object_id)
        content = blob.download_as_text()

        
        # Asumimos CSV/TXT con cabeceras en la primera fila
        data_rows = []
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            data_rows.append(row)
        print("Contenido CSV/TXT:", data_rows)

        # 3. Inicializa cliente de BigQuery
        bq_client = bigquery.Client(project=project_id)

        # 4. Verifica si existe el dataset, si no, lo crea
        dataset_ref = bq_client.dataset(dataset_id)
        try:
            bq_client.get_dataset(dataset_ref)
            print(f"El dataset '{dataset_id}' ya existe.")
        except NotFound:
            print(f"El dataset '{dataset_id}' no existe. Creando dataset...")
            dataset = bigquery.Dataset(dataset_ref)
            # Opcional: define la ubicación y descripción
            dataset.location = "US"
            dataset.description = "Dataset creado por la función Cloud."
            dataset = bq_client.create_dataset(dataset)
            print(f"Dataset '{dataset_id}' creado exitosamente.")

        # 5. Verifica si existe la tabla, si no, la crea
        table_ref = dataset_ref.table(table_id)
        try:
            bq_client.get_table(table_ref)
            print(f"La tabla '{table_id}' ya existe.")
        except NotFound:
            print(f"La tabla '{table_id}' no existe. Creándola...")
            # Define el schema. Debe coincidir con las columnas que tengas en el CSV/JSON
            schema = [
                bigquery.SchemaField("id",         "STRING", mode="NULLABLE"),
                bigquery.SchemaField("first_name", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("last_name",  "STRING", mode="NULLABLE"),
                bigquery.SchemaField("email",      "STRING", mode="NULLABLE"),
                bigquery.SchemaField("gender",     "STRING", mode="NULLABLE"),
                bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE")
            ]
            table = bigquery.Table(table_ref, schema=schema)
            table = bq_client.create_table(table)
            print(f"Tabla '{table_id}' creada exitosamente.")

        # 6. Inserta los datos en BigQuery
        # data_rows debe ser una lista de diccionarios con llaves que coincidan con las columnas
        errors = bq_client.insert_rows_json(table_ref, data_rows)
        if errors:
            print(f"Errores al insertar filas en BigQuery: {errors}")
        else:
            print("Datos insertados correctamente en BigQuery.")

    else:
        print(f"No se procesan archivos con extensión: {extension}. Ignorando {object_id}")

    return ("OK", 200)
