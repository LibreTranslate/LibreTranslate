import os

_prefix = 'LT_'


def _get_value_str(name, default_value):
    env_value = os.environ.get(name)
    return default_value if env_value is None else env_value


def _get_value_int(name, default_value):
    try:
        return int(os.environ[name])
    except:
        return default_value


def _get_value_bool(name, default_value):
    env_value = os.environ.get(name)
    if env_value in ['FALSE', 'False', 'false', '0']:
        return False
    if env_value in ['TRUE', 'True', 'true', '1']:
        return True
    return default_value


def _get_value(name, default_value, value_type):
    env_name = _prefix + name
    if value_type == 'str':
        return _get_value_str(env_name, default_value)
    if value_type == 'int':
        return _get_value_int(env_name, default_value)
    if value_type == 'bool':
        return _get_value_bool(env_name, default_value)
    return default_value


_default_options_objects = [
    {
        'name': 'HOST',
        'default_value': '127.0.0.1',
        'value_type': 'str'
    },
    {
        'name': 'PORT',
        'default_value': 5000,
        'value_type': 'int'
    },
    {
        'name': 'CHAR_LIMIT',
        'default_value': -1,
        'value_type': 'int'
    },
    {
        'name': 'REQ_LIMIT',
        'default_value': -1,
        'value_type': 'int'
    },
    {
        'name': 'REQ_LIMIT_STORAGE',
        'default_value': 'memory://',
        'value_type': 'str'
    },
    {
        'name': 'DAILY_REQ_LIMIT',
        'default_value': -1,
        'value_type': 'int'
    },
    {
        'name': 'REQ_FLOOD_THRESHOLD',
        'default_value': -1,
        'value_type': 'int'
    },
    {
        'name': 'BATCH_LIMIT',
        'default_value': -1,
        'value_type': 'int'
    },
    {
        'name': 'GA_ID',
        'default_value': None,
        'value_type': 'str'
    },
    {
        'name': 'DEBUG',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'SSL',
        'default_value': None,
        'value_type': 'bool'
    },
    {
        'name': 'FRONTEND_LANGUAGE_SOURCE',
        'default_value': 'auto',
        'value_type': 'str'
    },
    {
        'name': 'FRONTEND_LANGUAGE_TARGET',
        'default_value': 'locale',
        'value_type': 'str'
    },
    {
        'name': 'FRONTEND_TIMEOUT',
        'default_value': 500,
        'value_type': 'int'
    },
    {
        'name': 'API_KEYS',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'API_KEYS_DB_PATH',
        'default_value': 'db/api_keys.db',
        'value_type': 'str'
    },
    {
        'name': 'API_KEYS_REMOTE',
        'default_value': '',
        'value_type': 'str'
    },
    {
        'name': 'GET_API_KEY_LINK',
        'default_value': '',
        'value_type': 'str'
    },
    {
        'name': 'REQUIRE_API_KEY_ORIGIN',
        'default_value': '',
        'value_type': 'str'
    },
    {
        'name': 'REQUIRE_API_KEY_SECRET',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'SHARED_STORAGE',
        'default_value': 'memory://',
        'value_type': 'str'
    },
    {
        'name': 'LOAD_ONLY',
        'default_value': None,
        'value_type': 'str'
    },
    {
        'name': 'THREADS',
        'default_value': 4,
        'value_type': 'int'
    },
    {
        'name': 'SUGGESTIONS',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'DISABLE_FILES_TRANSLATION',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'DISABLE_WEB_UI',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'UPDATE_MODELS',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'FORCE_UPDATE_MODELS',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'METRICS',
        'default_value': False,
        'value_type': 'bool'
    },
    {
        'name': 'METRICS_AUTH_TOKEN',
        'default_value': '',
        'value_type': 'str'
    },
    {
        'name': 'URL_PREFIX',
        'default_value': '',
        'value_type': 'str'
    },
]


DEFAULT_ARGUMENTS = {obj['name']: _get_value(**obj) for obj in _default_options_objects}
