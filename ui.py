import bpy

class VolumePanel(bpy.types.Panel):
    bl_label = "volume"
    bl_idname = "OBJECT_PT_VolumePanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MeshVolume"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.label(text = "calculate  volume", icon ="META_CUBE")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.mesh_volume")
        row.operator("object.save_info")

        if float(bpy.context.object.volume) == 0:
            row.alignment = 'CENTER'
            row.label(text = "")
        if float(bpy.context.object.volume) > 0:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text = "%.6f" % bpy.context.object.volume +" m\u00b3")
        
        row = layout.row()
        row.operator("object.union_operator")
        row = layout.row()
        row.operator("db.export_operator")

class BackgroundPanel(bpy.types.Panel):
    bl_label = "background"
    bl_idname = "_PT_BackgroundPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MeshVolume"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        menu = scene.background

        row = layout.row()
        layout.prop(menu, "backgroundMenu")
        row = layout.row()
        row.operator("background.choose_background")

