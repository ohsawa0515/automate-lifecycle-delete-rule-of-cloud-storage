# Automate lifecycle delete rule of Google Cloud Storage

This repository creates architecture which add automatically [lifecycle delete of rules](https://cloud.google.com/storage/docs/lifecycle) of Google Cloud Storage (GCS)'s bucket when it is created.

## Installtion

The architecture is created by [Cloud Deployment Manager](https://cloud.google.com/deployment-manager) (CDM).

### 1. Enable necessary services.

```bash
gcloud services enable compute.googleapis.com \
  deploymentmanager.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudfunctions.googleapis.com
```

### 2. Add the required permissions in the CDM.

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects list --filter="${PROJECT_ID}" --format="value(PROJECT_NUMBER)")

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role roles/editor

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role roles/logging.configWriter

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role roles/resourcemanager.organizationAdmin
```

### 3. Change the properties in `deployment.yml` as needed.

```yaml
properties:
  location: us-east1
  bucketLocation: US
  lifecycleExpire: 365
```

#### location

Location where Cloud Functions are deployed. Default is `us-east1`.

#### bucketLocation

GCS bucket location required for Cloud Functions to deploy. Default is `US` (Multi regions).

#### lifecycleExpire

The number of days a GCS object is held. It will be automatically deleted after this number of days.
Default is `365` days.

### 4. Deploy

```bash
DEPLOY_NAME='setting-gcs-bucket'

gcloud deployment-manager deployments create $DEPLOY_NAME --config deployment.yml --preview
gcloud deployment-manager deployments update $DEPLOY_NAME
```

## Deletion

```bash
gsutil rm -r gs://${DEPLOY_NAME}-for-cfn-deploying-${PROJECT_NUMBER}
gcloud deployment-manager deployments delete $DEPLOY_NAME
```

