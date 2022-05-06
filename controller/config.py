import json
import os
from pydantic import BaseModel
from helper.constant import CONFIG_FILE, ConcatOptions


class Config(BaseModel):
    input_folder: str
    output_folder: str
    files_number: int
    threads: int
    music_file_first: str
    position_insert_music_first: int
    music_file_second: str
    position_insert_music_second: int
    concat_option: str

class ConfigSetup:
    def __init__(self) -> None:
        self.config_file = "configs/" + CONFIG_FILE
        if not os.path.exists('configs'):
            os.mkdir('configs')
        self.load_config()

    def store_config(self, config: Config):
        self.config = config
        with open(self.config_file, "w") as outfile:
            json.dump(self.config.dict(), outfile)

    def load_config(self):
        try:
            with open(self.config_file, "r") as infile:
                self.config = Config(**json.load(infile))
        except FileNotFoundError:
            self.config = Config(
                input_folder='',
                output_folder='',
                files_number=5,
                threads=4,
                music_file_first='',
                position_insert_music_first=0,
                music_file_second='',
                position_insert_music_second=3,
                concat_option=ConcatOptions.CONCAT_DEMUXER.value
            )