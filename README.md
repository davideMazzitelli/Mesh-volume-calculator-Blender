# Mesh volume calculator

> #### Reference
> - Category: Mesh
> - Description: Calcolo e immagazzinamento del volume di meshes
> - Location: 3D Viewport ‣ Sidebar
> - Blender version: 3.1.0 
> - File: Mesh_volume_calculator folder
> - Author: Mazzitelli Davide

### Installation
The addon is not bundled in Blender.

- Select add-ons tab in Blender preferences.
- Click on install and select Mesh_volume_calculator.zip
- Select now the add-on to enable the script.

### Description
Add-on for 3D modeling software Blender that allows you to calculate mesh volumes and collect their value along with rendered images and generic object information in a database.
The add-on is accompanied by a virtual environment called <b> Virtual_scene.blend </b> for the acquisition of mesh data and is also equipped with support features for exporting the generated database content, the creation of compound meshes and dynamic setting of the scene texture environment.

## GUI
### Panel volume:
#### - Mesh Volume
Active if the <i> active_object </i> is a non-null mesh.

The volume of the active_object is calculated and shown.
The value is saved in the custom property of the object named <i>volume<i>.

#### - Save info
Active if the custom property <i> volume </i> is instantiated.
The file <i>Volumes_dataset.db<i> is generated if not already existing.
By rotating the virtual camera around the mesh, 6 images of the scene are then acquired from different angles.
At this point the following information is entered in the database:

- id: integer, auto-incrementing primary key
- date: datetime
- objName: text, name of the mesh
- volume: real
- panoramic: BLOB
- front: BLOB
- l1: BLOB
- behind: BLOB
- l2: BLOB
- top: BLOB


#### - Union
Active if selected two non-null meshes.

Apply the <i>Boolean Union modifier<i> creating a compound mesh.

#### - Export
Active if exists the file <i>Volumes_dataset.db</i>.

Create in the path indicated by the Blender <i>render output path<i> the CSV file corresponding to the database content accompanied by a folder containing the images.


### Panel background
#### - backgroundMenu
Drop down menu containing five different HDR images that can be used as <b> Virtual_scene.blend </b> environment texture by clicking the <b> Choose Background </b> button

#### - Choose Background
Activates the HDR image selected in <b> backgroundmenu </b> as <i> Environment texture </i> node of the virtual scene <b> Virtual_scene.blend </b>
