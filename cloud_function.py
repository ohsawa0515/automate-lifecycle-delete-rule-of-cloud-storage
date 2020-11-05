import base64
import hashlib
from io import BytesIO
import zipfile

def GenerateConfig(context):
  in_memory_output_file = BytesIO()
  zip_file = zipfile.ZipFile(
      in_memory_output_file, mode='w', compression=zipfile.ZIP_DEFLATED)
  for imp in context.imports:
    if imp.startswith(context.properties['codeLocation']):
      zip_file.writestr(imp[len(context.properties['codeLocation']):],
                        context.imports[imp])
  zip_file.close()
  content = base64.b64encode(in_memory_output_file.getvalue())
  m = hashlib.md5()
  m.update(content)
  source_archive_url = 'gs://%s/%s' % (context.properties['codeBucket'],
                                       m.hexdigest() + '.zip')
  cmd = "echo '%s' | base64 -d > /function/function.zip;" % (content.decode('ascii'))
  volumes = [{'name': 'function-code', 'path': '/function'}]
  build_step = {
      'name': 'upload-function-code',
      'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
      'metadata': {
          'runtimePolicy': ['UPDATE_ON_CHANGE']
      },
      'properties': {
          'steps': [{
              'name': 'ubuntu',
              'args': ['bash', '-c', cmd],
              'volumes': volumes,
          }, {
              'name': 'gcr.io/cloud-builders/gsutil',
              'args': ['cp', '/function/function.zip', source_archive_url],
              'volumes': volumes
          }],
          'timeout':
              '120s'
      }
  }
  cloud_function = {
      'type': 'gcp-types/cloudfunctions-v1:projects.locations.functions',
      'name': context.properties['function'],
      'properties': {
          'parent':
              '/'.join([
                  'projects', context.env['project'], 'locations',
                  context.properties['location']
              ]),
          'function': context.properties['function'],
          'sourceArchiveUrl': source_archive_url,
          'environmentVariables': {
              'LIFECYCLE_EXPIRE': str(context.properties['lifecycleExpire']),
              'IGNORE_PATTERNS': '###'.join(context.properties['ignorePatterns'])
          },
          'entryPoint': context.properties['entryPoint'],
          'eventTrigger': context.properties['eventTrigger'],
          'timeout': context.properties['timeout'],
          'availableMemoryMb': context.properties['availableMemoryMb'],
          'runtime': context.properties['runtime'],
          'serviceAccountEmail': context.properties['serviceAccountEmail'],
      },
      'metadata': {
          'dependsOn': ['upload-function-code']
      }
  }

  return {
      'resources': [build_step, cloud_function]
  }

