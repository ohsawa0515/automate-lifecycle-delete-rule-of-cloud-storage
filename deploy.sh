#!/bin/bash

REGION='asia-northeast1'
FUNCTION_NAME='setting-gcs-bucket'
TOPIC='create_gcs_bucket'

gcloud functions deploy $FUNCTION_NAME \
    --entry-point=main_handler \
    --runtime=python38 \
    --trigger-topic=$TOPIC \
    --memory=128MB \
    --region=$REGION
