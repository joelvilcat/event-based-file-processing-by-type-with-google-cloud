import base64
import json
from google.cloud import storage, vision

def process_image_files(request): 
    request_json = request.get_json()
    if not request_json:
        print("No Pub/Sub message received")
        return ("Bad Request", 400)

    pubsub_message = request_json.get("message")
    if not pubsub_message:
        print("No message field in request")
        return ("Bad Request", 400)

    attributes = pubsub_message.get("attributes", {})
    object_id = attributes.get("objectId", "")
    bucket_id = attributes.get("bucketId", "")

    # Filtrar por .png, .jpg, .jpeg
    if object_id.endswith((".png", ".jpg", ".jpeg")):
        print(f"[IMG] Procesando imagen: {object_id}")
        gcs_uri = f"gs://{bucket_id}/{object_id}"
        vision_client = vision.ImageAnnotatorClient()
        image = vision.Image()
        image.source.image_uri = gcs_uri

        response = vision_client.text_detection(image=image)
        texts = response.text_annotations
        if texts:
            print(f"Texto OCR: {texts[0].description}")
        else:
            print("No se detectó texto en la imagen.")
    else:
        print(f"No es imagen soportada. Ignorado: {object_id}")

    return ("OK", 200)
