import json
from google.cloud import storage
from google.cloud import firestore


def process_json_files(request):

    # 1. Obtenemos el contenido del request
    request_json = request.get_json()
    if not request_json:
        print("No Pub/Sub message received")
        return ("Bad Request", 400)

    pubsub_message = request_json.get("message")
    if not pubsub_message:
        print("No message field in request")
        return ("Bad Request", 400)

    # 2. Atributos de la notificación (nombre de archivo y bucket)
    attributes = pubsub_message.get("attributes", {})
    object_id = attributes.get("objectId", "")
    bucket_id = attributes.get("bucketId", "")

    # Validar si es un archivo JSON
    if not object_id.endswith(".json"):
        print(f"No es archivo .json. Ignorado: {object_id}")
        return ("OK", 200)

    print(f"[JSON] Procesando archivo: {object_id}")

    # 3. Descargar contenido desde GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_id)
    blob = bucket.blob(object_id)
    content = blob.download_as_text()
    
    # 4. Parsear el contenido JSON
    try:
        data_json = json.loads(content) 
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        return ("Bad Request", 400)

    print("Contenido JSON descargado:", data_json)

    # 5. Conectar a Firestore
    db = firestore.Client(database="database-users")

    # Nombre de la colección donde se guardarán los documentos
    collection_name = "users"


    batch = db.batch()

    # data_json asume un array/lista de dict. 
    for doc_data in data_json:
        # Supongamos que cada objeto tiene un campo 'id' que queremos usar como 
        # ID del documento en Firestore. Si no, puedes usar un auto-ID con .document().
        doc_id = str(doc_data.get("id", ""))  # convertimos a string por si es numérico
        if doc_id:
            doc_ref = db.collection(collection_name).document(doc_id)
        else:
            # Si no tiene ID, generamos un auto-ID
            doc_ref = db.collection(collection_name).document()
        
        batch.set(doc_ref, doc_data)

    # 7. Commit del batch para guardar todo de una vez
    batch.commit()
    print(f"Se han insertado {len(data_json)} documentos en la colección '{collection_name}'.")

    return ("OK", 200)
