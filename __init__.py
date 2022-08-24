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
    "name" : "mesh volume calculator",
    "author" : "Davide Mazzitelli",
    "description" : "Calculate the volume of the active object and show the result in the 'Volume' panel, than stores this data, the object name, and reder images in a database file (Volumes.db); the db file is generated if not already exists",
    "blender" : (3, 10, 0),
    "version" : (0, 0, 1),
    "location" : "3D Viewport ‣ Sidebar",
    "warning" : "",
    "category" : "Import-Export"
}

import bpy
from . import (
    operators,
    ui
)

classes = (ui.VolumePanel,
    operators.MeshVolume,
    operators.SaveInfo
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.volume = bpy.props.FloatProperty(name = "Volume Property")


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Object.volume

if __name__ == "__main__":
    register()