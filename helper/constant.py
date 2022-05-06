import enum

CONFIG_FILE = 'config.json'
VERSION = "1.0"

NEED_LOGIN = True
USERNAME = 'hieudv3'
PASSWORD = '123'

class ConcatOptions(enum.Enum):
    CONCAT_DEMUXER = "concat demuxer (same codecs)"
    CONCAT_FILTER = "concat filter (diff codecs)"