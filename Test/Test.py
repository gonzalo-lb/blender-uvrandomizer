bl_info = {
    "name": "Test Script",
    "author": "Gonzalo Lopez Borghello",
    "version": (1, 0),
    "blender": (3, 10, 0),
    "location": "UV EDITOR > Tabs (N Key) > UV Randomizer",
    "description": "Test",
    "doc_url": "",
    "category": "UV",
}

import bpy
import bmesh
import random
from math import radians

def GetSelectedUVFaces_InEditMode(bmeshref, uvlayer):
    """Devuelve un list con las caras seleccionadas.
    :bmeshref = The bmesh representation
    :uvlayer = Suele ser bm.loops.layers.uv.active"""
    cont = 0
    selecteduvfaces = []
    for face in bmeshref.faces:
        thisFaceSelected = True
        for vert in face.loops:
            if vert[uvlayer].select == False:
                thisFaceSelected = False
        
        if thisFaceSelected == True:
            selecteduvfaces.append(cont)
        cont += 1
    return selecteduvfaces

def SetSelectedFaces_InEditMode(bmeshref, uvlayer, selectedFaces):
    """Selecciona las caras indicadas en la referencia.
    :bmeshref = The bmesh representation
    :uvlayer = Suele ser bm.loops.layers.uv.active
    :selectedFaces = List con la indicación de las caras a seleccionar"""
    bpy.ops.uv.select_all(action='DESELECT')        
    facenumber = 0
    for face in bmeshref.faces:
        if facenumber in selectedFaces:
            for vert in face.loops:
                vert[uvlayer].select = True
        facenumber += 1

def QuitarDatosDelList(listDeEntrada, elOtroList):
    """Agarra el list de entrada y lo compara con el otro. Si alguno de los valores del list de entrada est�n en el otro, el valor se borra. Devuelve el list de entrada sin los que se repitan en el otro list."""
    listToReturn = listDeEntrada
    iterator = 0
    x = 0
    while x < len(listDeEntrada):
        if listDeEntrada[x] in elOtroList:
            listToReturn.remove(iterator)
            iterator-=1
        iterator+=1
        x+=1
    return listToReturn        

class TESTADDON_OT_StandardRotateAndResize(bpy.types.Operator):
    """Rotate selected faces"""
    bl_idname = "uv.testaddon_rotate_selected_uv"
    bl_label = "Selected UV Faces"
    
    def execute(self, context):
        
        bpy.ops.transform.rotate(value=0.591742, orient_axis='Z', orient_type='VIEW', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='VIEW', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.transform.resize(value=(0.605485, 0.605485, 0.605485), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        testSelectedFaces = [1, 3, 9]
        linkedFaces = [1, 2, 3, 4, 5, 6]
        print("Selected Faces: ")
        print(testSelectedFaces)
        print("Island: ")
        print(linkedFaces)        
        lasCarasQueQuedan = QuitarDatosDelList(testSelectedFaces, linkedFaces)
        print("Las caras que quedan: ")
        print(lasCarasQueQuedan)


        return {'FINISHED'}

class TESTADDON_OT_RandomRotateSelected(bpy.types.Operator):
    """Rotate selected faces"""
    bl_idname = "uv.testaddon_rotate_selected_uv"
    bl_label = "Rotate Selected UV Faces"
    
    def execute(self, context):
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            self.report({'WARNING'}, "Random Rotation only works in Edit Mode")
            return {'FINISHED'}
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        rot_min = UVRandomTranslateProps.rotMin
        rot_max = UVRandomTranslateProps.rotMax
        
        sameRandom = UVRandomTranslateProps.applySameRandomRot
        
        clampEnabled = UVRandomTranslateProps.clampValueRotEnabled
        clampValue = UVRandomTranslateProps.clampValue

        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active

        # Indexa las caras seleccionadas
        selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)

        bpy.ops.uv.select_all(action='DESELECT')
        
        # Establece una rotaci�n para aplicar a todas las caras, para el caso de que se haya seleccionado esa opci�n (sameRandom == True)
        if clampEnabled:
            tempVar1 = 360 / clampValue
            randTimes = int(random.uniform(0, int(tempVar1)))
            currentRot =  radians(randTimes * clampValue)            
        else:
            currentRot = radians(random.uniform(rot_min, rot_max))

        # Rota las caras
        facenumber = 0
        for face in bm.faces:
            if facenumber in selected_uv_faces:
                bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
                for vert in face.loops:
                    vert[uv_layer].select = True                    

                bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                if sameRandom == False:
                    if clampEnabled:
                        tempVar1 = 360 / clampValue
                        randTimes = int(random.uniform(0, int(tempVar1)))
                        currentRot =  radians(randTimes * clampValue)            
                    else:
                        currentRot = radians(random.uniform(rot_min, rot_max))
                bpy.ops.transform.rotate(value=currentRot, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                bpy.ops.uv.select_all(action='DESELECT')
            facenumber += 1

        # Se asegura de que queden seleccionados solo los v�rtices de las caras utilizadas
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces)

        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, "RANDOM ROTATION: Done!")
        return {'FINISHED'}
    
class TESTADDON_PT_UVRandomizer(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Test"
    bl_label = "Test"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        
        obj = context.object
        
        row = layout.row()
        row.label(text="TRANSLATE FACES")
                
        row.operator("uv.testaddon_rotate_selected_uv", icon= 'CON_TRANSLIKE')
        

classes = [TESTADDON_PT_UVRandomizer, TESTADDON_OT_StandardRotateAndResize]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()