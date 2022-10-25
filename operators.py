import datetime
import math
import os
import random as rand
import sqlite3
import csv
import bmesh
import bpy

# operatore MeshVolume
def calculate_volume():                        # calcolo volume della mesh
    obj = bpy.context.active_object
    bmeshObj = create_mesh(obj)                                 # creazione mesh e calcolo volume
    vol = bmeshObj.calc_volume() 
    bmeshObj.free()
    return vol

def create_mesh(obj):                                       # creazione della mesh a partire dall'oggetto
    assert obj.type == 'MESH'

    if obj.mode == 'EDIT':
        bm_edit = bmesh.from_edit_mesh(obj.data)
        bm = bm_edit.copy()
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

    bm.transform(obj.matrix_world)          # trasforma i punti da Object space a World space
    bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm

class MeshVolume(bpy.types.Operator):
    bl_idname = "object.mesh_volume"
    bl_label = "Mesh Volume"
    bl_description = "Calculate the volume measure of the active_object"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and context.active_object.type == 'MESH')
    

    def execute(self, context):

        bpy.context.object.volume = calculate_volume()

        self.report({'INFO'}, "Volume: " + "%.6f" % (bpy.context.object.volume)+ " m\u00b3")

        return {'FINISHED'}

# operatore SaveInfo
def create_db():                                            # creazione database
    con = sqlite3.connect('Volumes_dataset.db')                     
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS data(    
               id integer PRIMARY KEY,
               date datetime,
               objName text,
               volume real,
               panoramic BLOB,
               front BLOB,
               l1 BLOB,
               behind BLOB,
               l2 BLOB,
               top BLOB)
               ''')                                        
               
    con.commit()
    con.close()

def randomFrontBack():
    pivot = bpy.data.objects["Empty"]
    randZ = rand.randrange(-30, 30)
    randX = rand.randrange(-6, 4)
    pivot.rotation_euler[0] += math.radians(randX)
    pivot.rotation_euler[2] += math.radians(randZ)

def randomLateral():
    pivot = bpy.data.objects["Empty"]
    randZ = rand.randrange(-45, 45)
    randY = rand.randrange(-5, 5)
    pivot.rotation_euler[1] += math.radians(randY)
    pivot.rotation_euler[2] += math.radians(randZ)

def randomTop():
    pivot = bpy.data.objects["Empty"]
    bpy.data.objects["Camera"].location[2] = 0
    pivot.rotation_euler[0] += math.radians(-90)
    pivot.rotation_euler[1] += math.radians(rand.randrange(-60, 60))

def render_obj(output_dir):                                 # render della scena con salvataggio file jpg

    camera = bpy.context.scene.camera
    obj = bpy.context.active_object
    name = obj.name
    
    x = bpy.data.objects["Camera"].location[0]
    y = bpy.data.objects["Camera"].location[1]
    z = bpy.data.objects["Camera"].location[2]

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_VOLUME")

    bpy.data.scenes["Scene"].cursor.location[0] = obj.location[0]
    bpy.data.scenes["Scene"].cursor.location[1] = obj.location[1]
    bpy.data.scenes["Scene"].cursor.location[2] = obj.location[2]

    bpy.ops.object.empty_add(type="PLAIN_AXES")
    bpy.data.objects["Empty"].hide_render = True

    cam_lock = camera.constraints.get("LOCKTOOBJ")
    if cam_lock is None:
        cam_lock = camera.constraints.new('TRACK_TO')
        cam_lock.name = "LOCKTOOBJ"
        cam_lock.track_axis = 'TRACK_NEGATIVE_Z'
        cam_lock.up_axis = 'UP_Y'
        cam_lock.use_target_z = True
    
    cam_lock.target = obj

    # panoramic
    bpy.data.objects["Camera"].location[0] = 1.85
    bpy.data.objects["Camera"].location[1] = -2.25
    bpy.data.objects["Camera"].location[2] = 1
    pivot = bpy.data.objects["Empty"]
    c = bpy.data.objects["Camera"]
    c.parent = pivot
    pivot.rotation_euler[2] = math.radians(rand.uniform(0, 360))
    bpy.context.scene.render.filepath = output_dir + '0'
    bpy.ops.render.render(write_still = True)
    c.parent = None

    d = math.sqrt(x**2 + y**2 + z**2)
    bpy.data.objects["Camera"].location[0] = 0
    bpy.data.objects["Camera"].location[1] = -d
    bpy.data.objects["Camera"].location[2] = 0.65
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    c.parent = pivot

    for i in range(1,6):
        if i == 5:
            randomTop()
            bpy.context.scene.render.filepath = output_dir + str(i)
            bpy.ops.render.render(write_still = True)
        else:
            if i == 1 or i == 3:
                randomFrontBack()
                bpy.context.scene.render.filepath = output_dir + str(i)
                bpy.ops.render.render(write_still = True)
                pivot.rotation_euler[0] = 0
                pivot.rotation_euler[2] = 0
            if i == 2 or i == 4:
                randomLateral()
                bpy.context.scene.render.filepath = output_dir + str(i)
                bpy.ops.render.render(write_still = True)
                pivot.rotation_euler[1] = 0
                pivot.rotation_euler[2] = 0

            pivot.rotation_euler[2] += math.radians(90)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    bpy.ops.object.delete(use_global=False)
    bpy.context.view_layer.objects.active = bpy.data.objects[name]

    bpy.data.objects["Camera"].location[0] = x
    bpy.data.objects["Camera"].location[1] = y
    bpy.data.objects["Camera"].location[2] = z

def binarizeData(file):                                     # lettura dell'immagine in formato binario
    with open(file,'rb') as f:
        bd = f.read()
    return bd

def store_info(imgs):                                  # salvataggio delle informazioni nel database
    name = bpy.context.active_object.name
    con = sqlite3.connect('Volumes_dataset.db')             # connessione a database
    cur = con.cursor()
    dt = datetime.datetime.now()
    dateTime = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    cur.execute("INSERT INTO data (date, objName, volume, panoramic, front, l1, behind, l2, top) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (dateTime, name, float("%.6f" % bpy.context.object.volume), imgs[0], imgs[1], imgs[2], imgs[3], imgs[4], imgs[5]))
    con.commit()                                       
    con.close() 

class SaveInfo(bpy.types.Operator):
    bl_idname = "object.save_info"
    bl_label = "Save info"
    bl_description = "Store the object id, datetime info, object name, volume measure and multiple point of view renders in Volumes_dataset.db file (created if not exists)"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'MESH' and
                bpy.context.active_object.volume !=0 )
    
    def execute(self, context):
        create_db()
        name = bpy.context.active_object.name
        path = bpy.data.scenes["Scene"].render.filepath
        fname = path + name                                              
        render_obj(fname)                               # render della scena
        bpy.data.scenes["Scene"].render.filepath = path
        imgs = []
        for i in range(6):
            img = binarizeData(fname + str(i) + '.png') # lettura immagine
            imgs.append(img)

        store_info(imgs)

        # for i in range(6) : 
        #     os.remove(fname + str(i) + '.png')
        
        self.report({'INFO'}, "Info stored")
        return {'FINISHED'}

# operatore UnionOP
class UnionOp(bpy.types.Operator):
    bl_idname = "object.union_operator"
    bl_label = "Union"
    bl_description = "Apply the Boolean Union modifier to the selected objects"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'MESH' and
                len(context.selected_objects) == 2)
    
    def execute(self, context):
        obj = bpy.context.active_object

        if obj != context.selected_objects[0]:
            obj_target = context.selected_objects[0]
            obj_other = context.selected_objects[1]
        else:
            obj_target = context.selected_objects[1]
            obj_other = context.selected_objects[0]

        for mat in obj_target.data.materials: # aggiunta materiali all' active object
            obj.data.materials.append(mat)

        obj.modifiers.new(name='union', type='BOOLEAN')
        obj.modifiers["union"].operation = "UNION"
        obj.modifiers["union"].object = obj_target
        bpy.ops.object.modifier_apply(modifier = "union")

        bpy.context.view_layer.objects.active = obj_target
        bpy.data.objects[obj_other.name].select_set(False)
        bpy.ops.object.delete(use_global=False)

        return {'FINISHED'} 

# operatore selezione sfondo
class ChooseBackground(bpy.types.Operator):
    bl_idname = "background.choose_background"
    bl_label = "Choose Background"
    bl_description = "Change the background HDR image of the Environment Texture node"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        scene = context.scene
        menu = scene.background
        background1 = bpy.data.images.load("//background/wooden_lounge_16k.hdr")
        background2 = bpy.data.images.load("//background/lebombo_16k.hdr")
        background3 = bpy.data.images.load("//background/christmas_photo_studio_01_16k.hdr")
        background4 = bpy.data.images.load("//background/tv_studio_16k.hdr")
        background5 = bpy.data.images.load("//background/colorful_studio_16k.hdr")

        if menu.backgroundMenu == 'wooden lounge':
            bpy.context.scene.world.node_tree.nodes['Environment Texture'].image = background1
        if menu.backgroundMenu == 'lebombo':
            bpy.context.scene.world.node_tree.nodes['Environment Texture'].image = background2
        if menu.backgroundMenu == 'christmas photo studio':
            bpy.context.scene.world.node_tree.nodes['Environment Texture'].image = background3
        if menu.backgroundMenu == 'tv studio':
            bpy.context.scene.world.node_tree.nodes['Environment Texture'].image = background4
        if menu.backgroundMenu == 'clourful studio':
            bpy.context.scene.world.node_tree.nodes['Environment Texture'].image = background5


        return {'FINISHED'} 

# operatore Export
def convert_data(img, path):
    with open(path, 'wb') as file:
        file.write(img)

class Export(bpy.types.Operator):
    bl_idname = "db.export_operator"
    bl_label = "Export"
    bl_description = "Export the data stored in Volumes_dataset.db in CSV format and an image folder"

    @classmethod
    def poll(cls, context):
        return os.path.exists("Volumes_dataset.db")

    def execute(self, context):
        conn = sqlite3.connect('Volumes_dataset.db')
        cursor = conn.cursor()
        path = bpy.data.scenes["Scene"].render.filepath
        cursor.execute("select * from data;")
        with open(path + "obj_volumes.csv", 'w',newline='') as csv_file: 
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description]) 
            cursor.execute("select id, date, objName, volume from data;")
            for j in cursor:
                name = j[2] 
                for x in range(6):
                    fname = path + "obj_dataset\\" + name + str(x) + ".png"
                    j += (fname,)
                csv_writer.writerow(j)

        if not os.path.exists(path + "obj_dataset"):
            os.makedirs(path + "obj_dataset")
        path += "obj_dataset"
        cursor.execute("select objName, panoramic, front, l1, behind, l2, top from data;")
        for j in cursor:
            name = j[0]
            fname = path + "\\" + name
            for x in range(1, 7):
                img = j[x]
                convert_data(img, fname + str(x-1) + ".png")

        conn.close()

        self.report({'INFO'}, "Data exported")
        return {'FINISHED'} 
