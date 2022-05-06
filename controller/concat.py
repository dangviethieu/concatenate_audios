from controller import BaseHandler, setup_custom_logger
from controller.config import Config, ConcatOptions
from typing import List
from multiprocessing import Process, Queue
import glob
import queue
import os
import re
import sys
import subprocess
import time


class ConcatHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__(service='concat')
        self.processes: List[Process] = []
        self.logs = Queue()
        self.tasks_done = Queue()

    def start(self, config: Config) -> None:
        custom_log = lambda x: (self.logs.put(x), self._logger.info(x))
        custom_log('----------------------------------------------------------------')
        if not config.input_folder or not config.output_folder:
            self.logs.put(f"No input folder or output folder")
            self.tasks_done.put(1)
            return
        if config.position_insert_music_first > config.position_insert_music_second:
            self.logs.put(f"Position insert music first must be less than position insert music second")
            self.tasks_done.put(1)
            return
        # get files from input folder
        files = glob.glob(os.path.join(config.input_folder, "*.*"))
        files.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
        if not files:
            self.logs.put(f"No files in input folder")
            self.tasks_done.put(1)
            return
        custom_log(f'Start concat each {config.files_number} files in total {len(files)} files in folder {config.input_folder}...')
        tasks_to_accomplish = Queue()
        split_point = int(len(files) / config.threads)
        split_point = split_point if split_point > config.files_number else config.files_number
        for index in range(config.threads):
            if index != config.threads - 1:
                tasks_to_accomplish.put((index, config ,files[split_point*index:split_point*(index+1)]))
            else:
                tasks_to_accomplish.put((index, config, files[split_point*index:]))
        for _ in range(config.threads):
            p = ConcatTask(tasks_to_accomplish, self.logs, self.tasks_done)
            self.processes.append(p)
            p.start()

    def stop(self):
        for process in self.processes:
            process.terminate()

class ConcatTask(Process):
    def __init__(self, tasks_to_accomplish: Queue, logs: Queue, tasks_done: Queue) -> None:
        Process.__init__(self)
        self.tasks_to_accomplish = tasks_to_accomplish
        self.logs = logs
        self.tasks_done = tasks_done

    def run(self):
        self._logger = setup_custom_logger('concat')
        custom_log = lambda x: (self.logs.put(x), self._logger.info(x))
        while True:
            try:
                index, config, files = self.tasks_to_accomplish.get_nowait()
                time.sleep(0.1)
                config: Config = config
            except Exception as e:
                print(f"error {e}")
                break
            else:
                files_splited = [files[i:i + config.files_number] for i in range(0, len(files), config.files_number)]
                for files_ in files_splited:
                    _, tail = os.path.split(files_[0])
                    _, tail_end = os.path.split(files_[-1])
                    try:
                        # option 1: concat demuxer
                        if config.concat_option == ConcatOptions.CONCAT_DEMUXER.value:
                            with open(f"configs/{tail}.txt", "w", encoding='utf-8') as f:
                                for index_file, file in enumerate(files_):
                                    if config.music_file_first and index_file == config.position_insert_music_first:
                                        if config.music_file_first.split('.')[-1] == file.split('.')[-1]:
                                            f.write(f"file '{config.music_file_first}'\n")
                                        else:
                                            custom_log(f'#Thread {index+1}: ---> need music file first format same with input files format!')
                                    if config.music_file_second and index_file == config.position_insert_music_second:
                                        if config.music_file_second.split('.')[-1] == file.split('.')[-1]:
                                            f.write(f"file '{config.music_file_second}'\n")
                                        else:
                                            custom_log(f'#Thread {index+1}: ---> need music file second format same with input files format!')
                                    f.write(f"file '{file}'\n")
                            cmd = f"ffmpeg -y -loglevel quiet -f concat -safe 0 -i \"configs/{tail}.txt\" -c copy \"{config.output_folder}/{tail}\""
                            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                            for _ in process.stdout:
                                pass
                            os.remove(f"configs/{tail}.txt")
                            custom_log(f'#Thread {index+1}: concates {tail} successfully!')
                        # option 2: concat filter
                        else:
                            custom_log(f'#Thread {index+1}: concating {config.files_number} files {tail}->{tail_end} ...')
                            cmd = "ffmpeg -y "
                            for index_file, file in enumerate(files_):
                                if config.music_file_first and index_file == config.position_insert_music_first:
                                    cmd += "-i \"" + config.music_file_first + "\" "
                                if config.music_file_second and index_file == config.position_insert_music_second:
                                    cmd += "-i \"" + config.music_file_second + "\" "
                                cmd += "-i \"" + file + "\" "
                            cmd += "-filter_complex \""
                            for index_file in range(len(files_)):
                                cmd += "[" + str(index_file) + ":a]"
                            cmd += f" concat=n={len(files_)}:v=0:a=1 [a]\" -map [a] \"{config.output_folder}/{tail}\""
                            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                            for _ in process.stdout:
                                pass
                            custom_log(f'#Thread {index+1}: concates {tail} successfully!')
                    except Exception as e:
                        custom_log(f'#Thread {index+1}: concates {tail} failed!')
                        _, _, exc_tb = sys.exc_info()
                        custom_log(f'#Thread {index+1}: line: {exc_tb.tb_lineno}, error: {e}')
                self.tasks_done.put(1)
                custom_log(f'#Thread {index+1}: Done')
                return
                