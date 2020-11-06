import base64
import json
import os
import sys
import re
from logging import getLogger, StreamHandler, INFO
from google.cloud import storage

age = os.environ.get('LIFECYCLE_EXPIRE')
ignorePatterns = os.environ.get('IGNORE_PATTERNS')

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

def get_gcs_bucket_name(pubsub_message):
    proto_payload = pubsub_message.get(u'protoPayload')
    if proto_payload is None or len(proto_payload) == 0:
        return None
    resource_name = proto_payload.get(u'resourceName')
    if resource_name is None or len(resource_name) == 0:
        return None
    return resource_name.split('/')[3]

def get_project_id(pubsub_message):
    resource = pubsub_message.get(u'resource')
    if resource is None or len(resource) == 0:
        return None
    labels = resource.get(u'labels')
    if labels is None or len(labels) == 0:
        return None
    project_id = labels.get(u'project_id')
    if project_id is None or len(project_id) == 0:
        return None
    return project_id

# Add lifecycle rule which deletes object after 365 days
def enable_bucket_lifecycle(bucket_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    bucket.add_lifecycle_delete_rule(age=age)
    bucket.patch()
    logger.info("Lifecycle addition is complete.")

def main_handler(event, context):
    pubsub_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    bucket_name = get_gcs_bucket_name(pubsub_message)
    if bucket_name is None:
        logger.error("Could not get the bucket name from the event data.")
        return
    logger.info("Bucket: %s" % bucket_name)

    project_id = get_project_id(pubsub_message)
    if project_id is None:
        logger.warning("Could not get the project id from the event data.")
    logger.info("Project id: %s" % project_id)

    for ignorePattern in ignorePatterns.split('###'):
        try:
            if re.match(ignorePattern, bucket_name):
                logger.info("Since it is included in ignorePattern '%s', it does not set the life cycle." % ignorePattern)
                return
        except re.error as regex_error:
            logger.warning("The grammar expression '%s' has an error : %s" % (ignorePattern, regex_error))

    enable_bucket_lifecycle(bucket_name)

# debug
if __name__ == '__main__':
    f = open("event_sample.json", "r", encoding="utf-8")
    event = json.load(f)
    f.close()
    context = ''
    age = '365'
    ignorePatterns = '.*.appspot.com###gcf-sources*'
    main_handler(event, context)
