import os
import urllib.parse
from dotenv import load_dotenv


load_dotenv()

DATABASES = {
    'postgres': {
        'NAME': 'neotests',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': 5434,
    },
    'redis': {
        'HOST': 'localhost',
        'PORT': '6379/0',
    }
}

# if 'DATABASE_URL' in os.environ:
#     urllib.parse.uses_netloc.append("postgres")
#     url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
#     DATABASES['postgres'] = {
#         'NAME': url.path[1:],
#         'USER': url.username,
#         'PASSWORD': url.password,
#         'HOST': url.hostname,
#         'PORT': url.port,
#     }

if 'REDIS_URL' in os.environ:
    urllib.parse.uses_netloc.append("redis")
    url = urllib.parse.urlparse(os.environ['REDIS_URL'])
    DATABASES['redis'] = {
        'HOST': url.hostname,
        'PORT': url.port,
    }



if 'APP_SECRET_KEY' in os.environ:
    APP_SECRET_KEY = os.environ['APP_SECRET_KEY']

if 'NODE_ENDPOINT' in os.environ:
    NODE_ENDPOINT = os.environ['NODE_ENDPOINT']
else:
    NODE_ENDPOINT = 'http://localhost:9000/socket_server'

database_url = 'postgresql://'+DATABASES['postgres'].get('USER')+':'+ DATABASES['postgres'].get('PASSWORD') + '@'+ str(DATABASES['postgres'].get('HOST'))+':'+ str(DATABASES['postgres'].get('PORT')) +'/'+ DATABASES['postgres'].get('NAME')
print('database url: ', database_url)
database_url_tests = database_url + '_tests'
redis_url = 'redis://'+DATABASES['redis'].get('HOST')+':'+ str(DATABASES['redis'].get('PORT'))
