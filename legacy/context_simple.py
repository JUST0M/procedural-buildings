#from .geometry import Scope

class ContextSimple():
    def getStartObj(self):
        return 0

    def split(self, obj):
        print("hello")
        print(obj)
        return (obj, obj+1)

    def colour(self, obj, colour):
        print("yo")
        print(obj)
        print(colour)
