from controller import BaseHandler, setup_custom_logger
from controller.config import Config
from typing import List
from multiprocessing import Process, Queue
import glob
import queue
import os
import re
import sys


class ConcatHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__(service='concat')
        self.processes: List[Process] = []
        self.logs = Queue()
        self.tasks_done = Queue()

    def start(self, config: Config) -> None:
        self._logger.info('----------------------------------------------------------------')
        if not config.input_folder or not config.output_folder:
            self.logs.put(f"No input folder or output folder")
            self.tasks_done.put(1)
            return
        # get files from input folder
        files = glob.glob(config.input_folder + "/*")
        files.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
        if not files:
            self.logs.put(f"No files in input folder")
            self.tasks_done.put(1)
            return
        self._logger.info(f'start concat each {config.files_number} files in total {len(files)} files in folder {config.input_folder}...')
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
                config: Config = config
            except queue.Empty:
                break
            else:
                files_splited = [files[i:i + config.files_number] for i in range(0, len(files), config.files_number)]
                for files_ in files_splited:
                    _, tail = os.path.split(files_[0])
                    try:
                        with open(f"configs/{tail}.txt", "w") as f:
                            for file in files_:
                                f.write(f"file '{file}'\n")
                        os.system(f"ffmpeg -y -f concat -safe 0 -i configs/{tail}.txt -c copy {config.output_folder}/{tail}")
                        os.remove(f"configs/{tail}.txt")
                        custom_log(f'#Thread {index+1}: concates {tail} successfully!')
                    except Exception as e:
                        custom_log(f'#Thread {index+1}: concates {tail} failed!')
                        _, _, exc_tb = sys.exc_info()
                        custom_log(f'#Thread {index+1}: line: {exc_tb.tb_lineno}, error: {e}')
                self.tasks_done.put(1)
                custom_log(f'#Thread {index+1}: Done')
                return
                