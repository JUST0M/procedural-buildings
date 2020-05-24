from Runner import Runner

class RunnerText(Runner):

    def __init__(self, startObj):
        super(RunnerText, self).__init__(startObj)
        self.finalObj = ''

    def split(self, obj):
        return(f'left half of ({obj})', f'right half of ({obj})')

    def colour(self, obj, colour):
        self.finalObj += f'Colour {colour}: {obj}\n'

