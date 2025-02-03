# 📂 **Event-Based Streaming File Processing by Type with Google Cloud (GCS + Pub/Sub + Cloud Run Functions + Vision AI + Firestore + BigQuery + IAM)**

Automated file processing pipeline based on event-driven architecture using **Google Cloud Storage (GCS)**, **Pub/Sub**, **Cloud Functions**, **Vision AI**, **Firestore**, **BigQuery**, and **IAM**.

## 🚀 **Overview**
This project demonstrates how to process different file types (e.g., `.json`, `.csv`, `.png`) automatically using Google Cloud's event-based services. It leverages **Pub/Sub** for event management, **Cloud Functions** for processing logic, and integrates with **Firestore**, **BigQuery**, and **Vision AI** for data handling.

## 🗂️ **Architecture**
- **Cloud Storage (GCS):** Stores unstructured files.
- **Pub/Sub:** Triggers events when files are uploaded.
- **Cloud Functions:** Processes files based on type.
  - `.json` ➜ Stored in **Firestore**.
  - `.csv` ➜ Loaded into **BigQuery**.
  - `.png` ➜ Analyzed with **Vision AI** (OCR).
- **Dead Letter Topic (DLT):** Handles failed events.
- **IAM:** Manages permissions securely.

---

## ⚙️ **Setup Instructions**

### **1️⃣ Environment Variables**
```bash
export PROJECT_ID="project-learning-gcp-data"
export BUCKET_NAME="project-learning-gcp-data"
export TOPIC_NAME="project-learning-gcp-data"
export DEAD_LETTER_TOPIC_NAME="dead-letter-topic"
export REGION="us-central1"

export SERVICE_ACCOUNT_NAME="gcp-service-account"
export SERVICE_ACCOUNT_ID="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

export JSON_ENDPOINT="https://$REGION-$PROJECT_ID.cloudfunctions.net/processJsonFiles"
export TXT_ENDPOINT="https://$REGION-$PROJECT_ID.cloudfunctions.net/processTxtFiles"
export IMG_ENDPOINT="https://$REGION-$PROJECT_ID.cloudfunctions.net/processImageFiles"
```

### **2️⃣ Enable Required Services**
```bash
gcloud services enable \
    cloudfunctions.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    vision.googleapis.com \
    firestore.googleapis.com \
    firestoreadmin.googleapis.com \
    bigquery.googleapis.com \
    --project=$PROJECT_ID
```

### **3️⃣ Create Service Account**
```bash
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="Service Account for GCP" \
    --project=$PROJECT_ID
```

### **4️⃣ Assign IAM Roles**
```bash
# Cloud Functions Deployment
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_ID" \
  --role="roles/cloudfunctions.developer"

# Storage Access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_ID" \
  --role="roles/storage.objectAdmin"

# Pub/Sub Permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_ID" \
  --role="roles/pubsub.admin"

# Vision AI, Firestore, BigQuery, Logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_ID" \
  --role="roles/visionai.user"
  --role="roles/datastore.user" \
  --role="roles/bigquery.dataEditor" \
  --role="roles/logging.admin"
```

### **5️⃣ Create Buckets and Topics**
```bash
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION "gs://$BUCKET_NAME"
gcloud pubsub topics create $TOPIC_NAME --project=$PROJECT_ID
gcloud pubsub topics create $DEAD_LETTER_TOPIC_NAME --project=$PROJECT_ID
```

### **6️⃣ Deploy Cloud Functions**
```bash
# Deploy JSON Processor
gcloud functions deploy processJsonFiles \
  --runtime=python310 \
  --trigger-http \
  --entry-point=process_json_files \
  --region=$REGION \
  --service-account=$SERVICE_ACCOUNT_ID

# Deploy CSV Processor
gcloud functions deploy processTxtFiles \
  --runtime=python310 \
  --trigger-http \
  --entry-point=process_txt_files \
  --region=$REGION \
  --service-account=$SERVICE_ACCOUNT_ID

# Deploy Image Processor (Vision AI)
gcloud functions deploy processImageFiles \
  --runtime=python310 \
  --trigger-http \
  --entry-point=process_image_files \
  --region=$REGION \
  --service-account=$SERVICE_ACCOUNT_ID
```

### **7️⃣ Configure Pub/Sub Subscriptions**
```bash
# JSON Subscription
gcloud pubsub subscriptions create sub-json \
  --topic=$TOPIC_NAME \
  --push-endpoint=$JSON_ENDPOINT \
  --message-filter='attributes.objectId.endsWith(".json")'

# CSV Subscription
gcloud pubsub subscriptions create sub-txt \
  --topic=$TOPIC_NAME \
  --push-endpoint=$TXT_ENDPOINT \
  --message-filter='attributes.objectId.endsWith(".csv")'

# PNG Subscription
gcloud pubsub subscriptions create sub-img \
  --topic=$TOPIC_NAME \
  --push-endpoint=$IMG_ENDPOINT \
  --message-filter='attributes.objectId.endsWith(".png")'
```

---

## 📊 **Sample Data Upload**
```bash
# Upload sample files
gsutil cp data.json gs://$BUCKET_NAME/
gsutil cp data.csv gs://$BUCKET_NAME/
gsutil cp image.png gs://$BUCKET_NAME/
```

## ✅ **Verify Processing**
- Check logs via **Cloud Logging**
- Validate data in **Firestore**, **BigQuery**, and **Vision AI** results

## 🧹 **Cleanup Resources**
```bash
gsutil rm -r gs://$BUCKET_NAME
gcloud pubsub topics delete $TOPIC_NAME $DEAD_LETTER_TOPIC_NAME
gcloud functions delete processJsonFiles processTxtFiles processImageFiles --region=$REGION
```

---

## 💡 **Author**
**Joel Vilca** | [LinkedIn](https://www.linkedin.com/in/joelvilcat)

Feel free to fork, modify, and contribute to this repository. 🚀

