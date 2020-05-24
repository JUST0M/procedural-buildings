# ================================
# module: model
#
# description:
#     Provides the model class for represeting the structure we are generating
#     This will most likely disappear when Blender comes into play
#
# ================================


__all__ = ['Model']

from .geometry import Scope

class Model(Scope):
    # Some blender stuff to actually change the model...

    def recolour(self, area, colour):
        print(f"Recoloured area:\n{area}\n with colour {colour}")
