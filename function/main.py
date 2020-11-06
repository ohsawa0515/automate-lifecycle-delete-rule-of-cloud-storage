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
