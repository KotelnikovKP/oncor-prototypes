from pyorient import OrientSerialization
from pyorient.ogm import Config, Graph, declarative

from backend.settings import ORIENTDB_HOST, ORIENTDB_PORT, ORIENTDB_NAME, ORIENTDB_USER, ORIENTDB_PASSWORD

# Config.from_url('plocal://' + DATABASES['orientdb']['HOST'] + ':' + str(DATABASES['orientdb']['PORT']) + '/' +
#                 DATABASES['orientdb']['NAME'] + '',
#                 '' + DATABASES['orientdb']['USER'] + '',
#                 '' + DATABASES['orientdb']['PASSWORD'] + '',
#                 initial_drop=False,
#                 serialization_type=OrientSerialization.Binary)

# graph = Graph(Config.from_url('' + DATABASES['orientdb']['HOST'] + '/' + DATABASES['orientdb']['NAME'] + '',
#                               '' + DATABASES['orientdb']['USER'] + '',
#                               '' + DATABASES['orientdb']['PASSWORD'] + '',
#                               initial_drop=False))

graph = Graph(
    Config.from_url(
        'plocal://' + ORIENTDB_HOST + ':' + str(ORIENTDB_PORT) + '/' + ORIENTDB_NAME,
        ORIENTDB_USER,
        ORIENTDB_PASSWORD,
        initial_drop=False,
        # serialization_type=OrientSerialization.Binary
    )
)

Node = declarative.declarative_node()

Relationship = declarative.declarative_relationship()
