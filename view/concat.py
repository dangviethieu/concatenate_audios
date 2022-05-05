from .base import Base, sg
from controller.config import Config, ConfigSetup
from controller.concat import ConcatHandler
from helper.constant import VERSION


class Concat(Base):
    def __init__(self):
        super().__init__()
        self.config_setup = ConfigSetup()
        self.concat_handler = ConcatHandler()
        self.layout = self.create_layout()
        self.window = sg.Window(f'Concat v{VERSION}', self.layout)
        self.handle_events()

    def create_layout(self):
        sg.theme('SystemDefault')
        return [
            [
                sg.Text('Input folder:', size=(11,1)), 
                sg.In(self.config_setup.config.input_folder, size=(75,1), enable_events=True ,key='input_folder'), 
                sg.FolderBrowse(),
            ],
            [
                sg.Text('Output folder:', size=(11,1)), 
                sg.In(self.config_setup.config.output_folder, size=(75,1), enable_events=True ,key='output_folder'), 
                sg.FolderBrowse(), 
            ],
            [
                sg.Frame('Setting', [[
                    sg.Text('No files'), sg.In(self.config_setup.config.files_number, key='files_number', size=(3,1)), 
                    sg.Text('Threads'), sg.In(self.config_setup.config.threads, key='threads', size=(3,1)),
                    sg.Text('Music insert:'),  sg.In(self.config_setup.config.music_file, size=(30,1), enable_events=True ,key='music_file'),  sg.FolderBrowse(), 
                    sg.Text('Position insert'), sg.In(self.config_setup.config.position_insert_music, key='position_insert_music', size=(3,1)),
                ]])
            ],
            [
                sg.Button('Start', size=(20,1), button_color='green', key='start'),
                sg.Button('Stop', size=(20,1), button_color='red', key='stop', visible=False),
            ],
            [
                sg.Frame('Logs', [
                    [
                        sg.Multiline(size=(95, 10), key='logs',)
                    ]
                ])
            ]
        ]

    def handle_events(self):
        while True:
            event, values = self.window.read(10)
            if event is None or event == sg.WIN_CLOSED:
                break
            if event == 'start':
                # update UI
                self.window['start'].update(visible=False)
                self.window['stop'].update(visible=True)
                # store config
                self.config_setup.store_config(
                    Config(
                        input_folder=self.window['input_folder'].get(),
                        output_folder=self.window['output_folder'].get(),
                        files_number=int(self.window['files_number'].get()),
                        threads=int(self.window['threads'].get()),
                        music_file=self.window['music_file'].get(),
                        position_insert_music=int(self.window['position_insert_music'].get()),
                    )
                )
                # run concat
                self.concat_handler.start(self.config_setup.config)
            if event == 'stop':
                # update UI
                self.window['start'].update(visible=True)
                self.window['stop'].update(visible=False)
                # stop concat
                self.concat_handler.stop()
            # update logs
            while not self.concat_handler.logs.empty():
                self.window['logs'].print(self.concat_handler.logs.get())
            while not self.concat_handler.tasks_done.empty():
                self.concat_handler.tasks_done.get()
                self.window['start'].update(visible=True)
                self.window['stop'].update(visible=False)