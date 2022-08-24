import math
import sqlite3
import bmesh
import bpy

# operatore MeshVolume
def calculate_volume(self, context):                        # calcolo volume della mesh
    obj = context.active_object
    mesh = create_mesh(obj)                                 # creazione mesh e calcolo volume
    volume = mesh.calc_volume() 
    mesh.free()
    return volume

def create_mesh(obj):                                       # creazione della mesh a partire dall'oggetto
    assert obj.type == 'MESH'

    me = obj.data
    if obj.mode == 'EDIT':
        bm_edit = bmesh.from_edit_mesh(me)
        bm = bm_edit.copy()
    else:
        bm = bmesh.new()
        bm.from_mesh(me)

    bm.transform(obj.matrix_world)          # trasforma i punti da Object space a World space
    bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm

class MeshVolume(bpy.types.Operator):
    bl_idname = "object.mesh_volume"
    bl_label = "Mesh Volume"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and context.active_object.type == 'MESH')
    

    def execute(self, context):

        bpy.context.object.volume = calculate_volume(self, context)

        self.report({'INFO'}, "Volume: " + "%.4f" % bpy.context.object.volume + " m\u00b3")

        return {'FINISHED'}


# operatore SaveInfo
def create_db():                                            # creazione database
    con = sqlite3.connect('Volumes.db')                     
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS volumes(    
               id integer PRIMARY KEY,
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

def render_obj(output_dir):                                 # render della scena con salvataggio file jpg

    camera = bpy.context.scene.camera
    obj = bpy.context.active_object
    name = obj.name
    

    x = bpy.data.objects["Camera"].location[0]
    y = bpy.data.objects["Camera"].location[1]
    z = bpy.data.objects["Camera"].location[2]

    d = math.sqrt(x**2 + y**2 + z**2)

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_VOLUME")
    obj.location[0] = 0
    obj.location[1] = 0

    bpy.data.scenes["Scene"].cursor.location[0] = obj.location[0]
    bpy.data.scenes["Scene"].cursor.location[1] = obj.location[1]
    bpy.data.scenes["Scene"].cursor.location[2] = obj.location[2]

    bpy.ops.object.empty_add(type="PLAIN_AXES")

    cam_lock = camera.constraints.get("LOCKTOOBJ")
    if cam_lock is None:
        cam_lock = camera.constraints.new('TRACK_TO')
        cam_lock.name = "LOCKTOOBJ"
        cam_lock.track_axis = 'TRACK_NEGATIVE_Z'
        cam_lock.up_axis = 'UP_Y'
        cam_lock.use_target_z = True
    
    cam_lock.target = obj

    # panoramic
    bpy.context.scene.render.filepath = output_dir + '0'
    bpy.ops.render.render(write_still = True)


    hView = 0.65
    bpy.data.objects["Camera"].location[0] = 0
    bpy.data.objects["Camera"].location[1] = -d
    bpy.data.objects["Camera"].location[2] = hView

    a = bpy.data.objects["Empty"]
    b = bpy.data.objects["Camera"]
    b.parent = a

    for i in range(1,5):
        bpy.context.scene.render.filepath = output_dir + str(i)
        bpy.ops.render.render(write_still = True)

        bpy.data.objects["Empty"].rotation_euler[2] += math.radians(90)


    #top:
    bpy.data.objects["Camera"].location[0] = 0
    bpy.data.objects["Camera"].location[1] = 0
    bpy.data.objects["Camera"].location[2] = 2*d

    bpy.context.scene.render.filepath = output_dir + '5'
    bpy.ops.render.render(write_still = True)


    bpy.ops.object.delete(use_global=False)
    bpy.context.view_layer.objects.active = bpy.data.objects[name]

    bpy.data.objects["Camera"].location[0] = x
    bpy.data.objects["Camera"].location[1] = y
    bpy.data.objects["Camera"].location[2] = z

def binarizeData(file):                                     # lettura dell'immagine in formato binario
    with open(file,'rb') as f:
        bd = f.read()
    return bd

def store_info(name, imgs):                                  # salvataggio delle informazioni nel database
    con = sqlite3.connect('Volumes.db')             # connessione a database
    cur = con.cursor()
    cur.execute("INSERT INTO volumes (objName, volume, panoramic, front, l1, behind, l2, top) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
            (name, float("%.4f" % bpy.context.object.volume), imgs[0], imgs[1], imgs[2], imgs[3], imgs[4], imgs[5]))
    con.commit()                                       
    con.close() 

class SaveInfo(bpy.types.Operator):
    bl_idname = "object.save_info"
    bl_label = "Save info"

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

        store_info(name ,imgs)

        # for i in range(6) : 
        #     os.remove(fname + str(i) + '.png')
            
        self.report({'INFO'}, "Info stored")
        
        return {'FINISHED'}