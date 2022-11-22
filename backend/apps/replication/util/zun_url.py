import os

__ZUN_URL_REPLICATION__ = 'http://127.0.0.1:5000/api/replication'


def get_zun_url():
    return os.getenv('ZUN_URL_REPLICATION', __ZUN_URL_REPLICATION__)
