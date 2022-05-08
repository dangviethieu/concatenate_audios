import enum

CONFIG_FILE = 'config.json'
VERSION = "1.3"

NEED_LOGIN = False
USERNAME = ''
PASSWORD = ''

class ConcatOptions(enum.Enum):
    CONCAT_DEMUXER = "concat demuxer (same codecs)"
    CONCAT_FILTER = "concat filter (diff codecs)"