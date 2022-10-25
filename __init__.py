# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Mesh Volume Calculator",
    "author" : "Davide Mazzitelli",
    "description" : '''Calculate the volume of the active object and show the result in the
                    'Volume' panel, than stores this data, the object name, reder images from multiple viewpoints
                    and the date of acquisition in a database file (Volumes.db); the db file is generated if not already exists''',
    "blender" : (3, 10, 0),
    "version" : (1, 0),
    "location" : "3D Viewport ‣ Sidebar",
    "warning" : "",
    "category" : "Mesh"
}

import bpy
from . import (
    operators,
    ui
)


class CustomProp(bpy.types.PropertyGroup):
    backgroundMenu : bpy.props.EnumProperty(
            name = "",
            description="Select background",
            items=[
                ("wooden lounge", 'wooden lounge', ""),
                ("lebombo", 'lebombo', ""),
                ("christmas photo studio", 'christmas photo studio',""),
                ("tv studio", 'tv studio', ""),
                ("clourful studio", 'clourful studio', "")
            ]
        )

classes = [CustomProp, 
    ui.VolumePanel,
    ui.BackgroundPanel,
    operators.MeshVolume,
    operators.SaveInfo,
    operators.UnionOp,
    operators.ChooseBackground,
    operators.Export
    ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.volume = bpy.props.FloatProperty()
    bpy.types.Scene.background = bpy.props.PointerProperty(type=CustomProp)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Object.volume
    del bpy.types.Scene.background

if __name__ == "__main__":
    register()
