import bpy

class VolumePanel(bpy.types.Panel):
    bl_label = "volume"
    bl_idname = "OBJECT_PT_VolumePanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Volume"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text = "calculate  volume", icon ="META_CUBE")

        row = layout.row(align=True)
        row.operator("object.mesh_volume")
        row.operator("object.save_info")

        if float(bpy.context.object.volume) == 0:
            row.alignment = 'CENTER'
            row.label(text = "")
        if float(bpy.context.object.volume) > 0:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text = "%.4f" % bpy.context.object.volume +" m\u00b3")