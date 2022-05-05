from .base import Base, sg

class Concat(Base):
    def __init__(self):
        super().__init__()
        self.layout = self.create_layout()
        self.window = sg.Window('Concat', self.layout)
        self.handle_events()

    def create_layout(self):
        sg.theme('SystemDefault')
        return [
            [
                sg.Text('Input folder:', size=(12,1)), 
                sg.In(size=(75,1), enable_events=True ,key='input_folder'), 
                sg.FolderBrowse(),
            ],
            [
                sg.Text('Output folder:', size=(12,1)), 
                sg.In(size=(75,1), enable_events=True ,key='output_folder'), 
                sg.FolderBrowse(), 
            ],
            [
                sg.Frame('Setting', [[
                    sg.Text('No files'), sg.In('5', key='files_number', size=(4,1)), 
                    sg.Text('Threads'), sg.In('4', key='threads', size=(4,1)),
                    sg.Text('Music insert:'),  sg.In(size=(30,1), enable_events=True ,key='music_file'),  sg.FolderBrowse(), 
                    sg.Text('Position'), sg.In('3', key='position_insert_music', size=(4,1)),
                ]])
            ],
            [sg.Button('Start', size=(20,1), button_color='violet', key='start')],
            [
                sg.Frame('Logs', [
                    [
                        sg.Multiline(size=(97, 10), key='logs',)
                    ]
                ])
            ]
        ]

    def handle_events(self):
        while True:
            event, values = self.window.read(1)
            if event is None or event == sg.WIN_CLOSED:
                break