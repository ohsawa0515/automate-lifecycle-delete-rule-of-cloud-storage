#!/bin/bash

gcloud services enable compute.googleapis.com deploymentmanager.googleapis.com cloudbuild.googleapis.com cloudresourcemanager.googleapis.com

PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects list --filter="${PROJECT_ID}" --format="value(PROJECT_NUMBER)")

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role roles/editor
 
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role roles/logging.configWriter

#gcloud projects add-iam-policy-binding ${PROJECT_ID} \
#  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
#  --role roles/iam.serviceAccountAdmin

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role roles/resourcemanager.organizationAdmin

# Deploy
gcloud deployment-manager deployments create setting-gcs-bucket --config deployment.yml --preview
gcloud deployment-manager deployments update setting-gcs-bucket

# Delete
# gsutil rm -r gs://setting-gcs-bucket-for-cfn-deploying
# gcloud deployment-manager deployments delete setting-gcs-bucket



#REGION='asia-northeast1'
#FUNCTION_NAME='setting-gcs-bucket'
#TOPIC='create_gcs_bucket'

#gcloud functions deploy $FUNCTION_NAME \
#    --entry-point=main_handler \
#    --runtime=python38 \
#    --trigger-topic=$TOPIC \
#    --memory=128MB \
#    --region=$REGION
