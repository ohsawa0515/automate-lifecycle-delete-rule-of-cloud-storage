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

# Add lifecycle rule which deletes object after 365 days
def enable_bucket_lifecycle(bucket_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    bucket.add_lifecycle_delete_rule(age=age)
    bucket.patch()
    logger.info("Lifecycle addition is complete.")

def main_handler(event, context):
    pubsub_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    resource_name = pubsub_message[u'protoPayload'][u'resourceName']
    bucket_name = resource_name.split('/')[3]
    logger.info("Bucket: %s" % bucket_name)

    for ignorePattern in ignorePatterns.split('###'):
        try:
            if re.match(ignorePattern, bucket_name):
                logger.info("Since it is included in ignorePattern '%s', it does not set the life cycle." % ignorePattern)
                return
        except re.error as regex_error:
            logger.warn("The grammar expression '%s' has an error : %s" % (ignorePattern, regex_error))

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
