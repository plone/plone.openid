try:
    from openid.yadis import etxrd
    HAS_OPENID=True
except:
    HAS_OPENID=False

import socket
HAS_SSL=hasattr(socket, "ssl")
del socket
