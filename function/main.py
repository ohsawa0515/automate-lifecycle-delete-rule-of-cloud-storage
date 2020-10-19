import base64, json, os
from google.cloud import storage

age = os.environ.get('LIFECYCLE_EXPIRE')

# Add lifecycle rule which deletes object after 365 days
def enable_bucket_lifecycle(bucket_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    bucket.add_lifecycle_delete_rule(age=age)
    bucket.patch()

def main_handler(event, context):
    pubsub_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    resource_name = pubsub_message[u'protoPayload'][u'resourceName']
    bucket_name = resource_name.split('/')[3]
    print("Bucket: %s" % bucket_name)
    enable_bucket_lifecycle(bucket_name)

