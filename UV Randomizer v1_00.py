# UV RAMDOMIZER
# V. 1.00

# IMPLEMENTACIONES DE LA VERSION 1.0:
#   COMPATIBILIDAD CON VERSION 2.90 DE BLENDER EN ADELANTE (POR LO MENOS HASTA LA 3.1)
#   QUE TENGA EN CUENTA LAS UV ISLANDS PARA LAS FUNCIONES TRANSLATE-ROTATE-SCALE

bl_info = {
    "name": "UV Randomizer",
    "author": "Gonzalo Lopez Borghello",
    "version": (1, 00),
    "blender": (2, 90, 0),
    "location": "UV EDITOR > Tabs (N Key) > UV Randomizer",
    "description": "Randomizes the UV faces",
    "doc_url": "https://github.com/gonzalo-lb/blender-uvrandomizer",
    "category": "UV",
}

import bpy
import bmesh
import random
from math import radians
import textwrap

def CompareListsAndRemoveElements(listDeEntrada, elOtroList):
    """Agarra el list de entrada y lo compara con el otro. Si alguno de los valores del list de entrada est�n en el otro, el valor se borra. Devuelve el list de entrada sin los que se repitan en el otro list."""
    toReturn = listDeEntrada.copy()
    for i in range(len(listDeEntrada)):
        if listDeEntrada[i] in elOtroList:
            toReturn.remove(listDeEntrada[i])
    return toReturn

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

def GetFaceInfo_EditMode(bmeshref, uvlayer, selectedFaces, returnCentroids=True, returnFaceOrder=False, returnBBLenght=False):
    """Calcula los centroides de las caras del bmesh que se ingresen como parámetro; El orden de las caras seleccionadas; Arma un bounding box y calcula sus extremos. Se devuelven según en el orden de los parámetros
    :Parámetros
    :bmeshref = The bmesh representation
    :uvlayer = Suele ser bm.loops.layers.uv.active
    :selectedFaces = List con los índices de las caras seleccionadas. Si se ingresa 0, utiliza todas las caras
    :returnCentroids = Boolean. Habilita la opción de calcular los centroides
    :returnFaceOrder = Boolean. Habilita la opción de calcular el orden de las caras utilizadas
    :returnBBLenght = Boolean. Habilita la opción de calcular los extremos del bounding box
    :Si los 3 booleans están en False, la función no hace nada
    :Retornos (Centroids)
    :xcentroid --> List con los centroides de cada cara, en coordenada X
    :ycentroid --> List con los centroides de cada cara, en coordenada Y
    :Retornos (FaceOrder)
    :faceOrder --> List con el orden de las caras. El index coincide con el de cada centroide
    :Retornos (BBLenght)
    :xminface --> List con el extremo menor de la cara, eje X
    :xmaxface --> List con el extremo mayor de la cara, eje X
    :yminface --> List con el extremo menor de la cara, eje Y
    :ymaxface --> List con el extremo mayor de la cara, eje Y"""
    if returnCentroids == False and returnFaceOrder == False and returnBBLenght == False:
        return
    
    if selectedFaces == 0:
        selectedFaces = []
        for cont in range(len(bmeshref.faces)):
            selectedFaces.append(cont)
            cont +=1

    facenumber = 0
    selectedUvFaceIndex = 0

    xminlist = []
    xmaxlist = []
    yminlist = []
    ymaxlist = []
    xcentroid = []
    ycentroid = []
    faceOrder = []

    xminface = []
    yminface = []
    xmaxface = []
    ymaxface = []
    faceOrder = []

    for face in bmeshref.faces:

        if facenumber in selectedFaces:

            xminlist.append(face.loops[0][uvlayer].uv[0])
            xmaxlist.append(face.loops[0][uvlayer].uv[0])
            yminlist.append(face.loops[0][uvlayer].uv[1])
            ymaxlist.append(face.loops[0][uvlayer].uv[1])
            
            for vert in face.loops:
                if vert[uvlayer].uv[0] <= xminlist[selectedUvFaceIndex]:
                    xminlist[selectedUvFaceIndex] = vert[uvlayer].uv[0]
                if vert[uvlayer].uv[0] >= xmaxlist[selectedUvFaceIndex]:
                    xmaxlist[selectedUvFaceIndex] = vert[uvlayer].uv[0]
                if vert[uvlayer].uv[1] <= yminlist[selectedUvFaceIndex]:
                    yminlist[selectedUvFaceIndex] = vert[uvlayer].uv[1]
                if vert[uvlayer].uv[1] >= ymaxlist[selectedUvFaceIndex]:
                    ymaxlist[selectedUvFaceIndex] = vert[uvlayer].uv[1]

            if returnBBLenght == True:
                xminface.append(xminlist[selectedUvFaceIndex])
                yminface.append(yminlist[selectedUvFaceIndex])
                xmaxface.append(xmaxlist[selectedUvFaceIndex])
                ymaxface.append(ymaxlist[selectedUvFaceIndex])
            if returnCentroids == True:
                xCentroidTemp = (xminlist[selectedUvFaceIndex] + xmaxlist[selectedUvFaceIndex]) / 2
                yCentroidTemp = (yminlist[selectedUvFaceIndex] + ymaxlist[selectedUvFaceIndex]) / 2
                xcentroid.append(xCentroidTemp)
                ycentroid.append(yCentroidTemp)
            if returnFaceOrder == True:
                faceOrder.append(selectedUvFaceIndex)

            selectedUvFaceIndex += 1

        facenumber += 1

    if returnBBLenght == False and returnFaceOrder == False and returnCentroids == True:
        return xcentroid, ycentroid
    elif returnBBLenght == False and returnFaceOrder == True and returnCentroids == False:
        return faceOrder
    elif returnBBLenght == False and returnFaceOrder == True and returnCentroids == True:
        return xcentroid, ycentroid, faceOrder
    elif returnBBLenght == True and returnFaceOrder == False and returnCentroids == False:
        return xminface, xmaxface, yminface, ymaxface
    elif returnBBLenght == True and returnFaceOrder == False and returnCentroids == True:
        return xcentroid, ycentroid, xminface, xmaxface, yminface, ymaxface
    elif returnBBLenght == True and returnFaceOrder == True and returnCentroids == False:
        return faceOrder, xminface, xmaxface, yminface, ymaxface
    elif returnBBLenght == True and returnFaceOrder == True and returnCentroids == True:
        return xcentroid, ycentroid, faceOrder, xminface, xmaxface, yminface, ymaxface

def _label_multiline(context, text, parent):
    chars = int(context.region.width / 7)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)

class UVRANDOMIZER_PG_UvRandomizer(bpy.types.PropertyGroup):
        #Keep islands
        keepIslands: bpy.props.BoolProperty(name= "Keep islands", default= True, description="If checked, the changes will be aplied to the whole island, even if a single face is selected [FOR NOW, IT WORKS ONLY WITH THE TRANSLATE/ROTATE/SCALE FACES FUNCTION]")

        #Translate
        minX : bpy.props.FloatProperty(name= "Min X Translate", default= -0.1, description="Minimum amount of translation on X axis")
        maxX : bpy.props.FloatProperty(name= "Max X Translate", default= 0.1, description="Maximum amount of translation on X axis")
        minY : bpy.props.FloatProperty(name= "Min Y Translate", default= -0.1, description="Minimum amount of translation on Y axis")
        maxY : bpy.props.FloatProperty(name= "Max X Translate", default= 0.1, description="Maximum amount of translation on Y axis")
        useXAxis : bpy.props.BoolProperty(name= "On X Axis (Min/Max)", default= True, description="Allows translation on X axis")
        useYAxis : bpy.props.BoolProperty(name= "On Y Axis (Min/Max)", default= True, description="Allows translation on Y axis")
        
        #Rotation
        rotMin : bpy.props.FloatProperty(name= "Min Rotation", default= 0, description="Minimum amount of rotation")
        rotMax : bpy.props.FloatProperty(name= "Min Rotation", default= 180, description="Maximum amount of rotation")
        applySameRandomRot : bpy.props.BoolProperty(name= "Apply same random value", default= False, description="Applies the same random rotation value to each face or island")
        clampValueRotEnabled : bpy.props.BoolProperty(name= "Clamp", default= True, description="Clamps the value to a multiplier of the selected angle. If checked, the Min/Max Rotation values won't be used")
        clampValue : bpy.props.FloatProperty(name= "Clamp Value", default= 90, description="Clamp value")
        
        #Scale
        scaleMin : bpy.props.FloatProperty(name= "Min Scale", default= 0.75, description="Minimum scaling value")
        scaleMax : bpy.props.FloatProperty(name= "Min Scale", default= 1.25, description="Maximum scaling value")
        applySameRandomScale : bpy.props.BoolProperty(name= "Apply same random value", default= False, description="Applies the same random scaling value to each face or island")
        applyEvenScale : bpy.props.BoolProperty(name= "Even scale", default= True, description="Applies the same random value to both X and Y axis")
        
        #Todo
        doTranslate : bpy.props.BoolProperty(name= "Translate", default= True, description="Applies random translation")
        doRotation : bpy.props.BoolProperty(name= "Rotate", default= True, description="Applies random rotation")
        doScaling : bpy.props.BoolProperty(name= "Scale", default= True, description="Applies random scaling")
        doSwap : bpy.props.BoolProperty(name= "Swap", default= False, description="Swap the uv faces")
        doShuffle : bpy.props.BoolProperty(name= "Shuffle", default= False, description="Shuffle the uv faces along the uv map")

class UVRANDOMIZER_OT_UvRandomTranslateSelected(bpy.types.Operator):
    """Randomly translate each selected face"""
    bl_idname = "uv.uvrandomizer_random_translate_selected"
    bl_label = "Selected UV Faces"
    
    def execute(self, context):

        # Solo funciona en Edit Mode
        if bpy.context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Random Translate only works in Edit Mode")
            return {'FINISHED'}
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        x_min = UVRandomTranslateProps.minX
        x_max = UVRandomTranslateProps.maxX
        y_min = UVRandomTranslateProps.minY
        y_max = UVRandomTranslateProps.maxY
        use_xaxis = UVRandomTranslateProps.useXAxis
        use_yaxis = UVRandomTranslateProps.useYAxis
        keep_islands = UVRandomTranslateProps.keepIslands
        
        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active
        
        # Indexa las caras seleccionadas
        selected_uv_faces_before_applying_operator = GetSelectedUVFaces_InEditMode(bm, uv_layer)
        selected_uv_faces = selected_uv_faces_before_applying_operator.copy()

        # Mueve las caras
        facenumber = 0

        if keep_islands == False:
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    x_rand = random.uniform(x_min, x_max)
                    y_rand = random.uniform(y_min, y_max)
                    
                    for vert in face.loops:
                        if use_xaxis:
                            vert[uv_layer].uv[0] += x_rand
                        if use_yaxis:
                            vert[uv_layer].uv[1] += y_rand
                facenumber += 1        
        else:
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    # Primero des-selecciona todo
                    bpy.ops.uv.select_all(action='DESELECT')

                    # Selecciona la cara en la que está el iterador
                    for vert in face.loops:
                        vert[uv_layer].select = True

                    # Selecciona el resto de la Island
                    bpy.ops.uv.select_linked()

                    # Define los valores aleatorios
                    x_rand = random.uniform(x_min, x_max)
                    y_rand = random.uniform(y_min, y_max)
                    
                    # Mueve la Island
                    if bpy.app.version[0] >= 3:
                        bpy.ops.transform.translate(value=(x_rand, y_rand, 0), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    else:
                        bpy.ops.transform.translate(value=(x_rand, y_rand, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

                    # Quita las caras duplicadas del selected_uv_faces
                    temp_selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
                    selected_uv_faces = CompareListsAndRemoveElements(selected_uv_faces, temp_selected_uv_faces)

                facenumber += 1
        
        # Se asegura de que queden seleccionados solo los vértices de las caras utilizadas
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces_before_applying_operator)
        
        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, "RANDOM TRANSLATE: Done!")    
        return {'FINISHED'}

class UVRANDOMIZER_OT_RandomTranslateAll(bpy.types.Operator):
    """Randomly translate all the uv faces"""
    bl_idname = "uv.uvrandomizer_random_translate"
    bl_label = "All UV Faces"

    def execute(self, context):
        
        hasToReturn = False
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            hasToReturn = True
            bpy.ops.object.editmode_toggle()            
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
        
        x_min = UVRandomTranslateProps.minX
        x_max = UVRandomTranslateProps.maxX
        y_min = UVRandomTranslateProps.minY
        y_max = UVRandomTranslateProps.maxY    
        use_xaxis = UVRandomTranslateProps.useXAxis
        use_yaxis = UVRandomTranslateProps.useYAxis
        keep_islands = UVRandomTranslateProps.keepIslands
        
        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active
        
        # Consigue las caras seleccionadas, para dejarlas como estaban luego de finalizar
        selected_uv_faces_before_applying_operator = GetSelectedUVFaces_InEditMode(bm, uv_layer)

        bpy.ops.uv.select_all(action='DESELECT')
        
        # Mueve las caras
        if keep_islands == False:
            for face in bm.faces:
                x_rand = random.uniform(x_min, x_max)
                y_rand = random.uniform(y_min, y_max)
                for vert in face.loops:
                    if use_xaxis:
                        vert[uv_layer].uv[0] += x_rand
                    if use_yaxis:
                        vert[uv_layer].uv[1] += y_rand
        else:

            # ESTA PARTE LA TRATA COMO A UN RANDOM-TRNASLATE-SELECTED, PERO CON TODAS LAS CARAS SELECCIONADAS
            # PARA PODER HACER LAS COMPARACIONES Y NO MOVER MUCHAS VECES LA MISMA ISLAND

            facenumber = 0
            bpy.ops.uv.select_all(action='SELECT')
            selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)            
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    # Primero des-selecciona todo
                    bpy.ops.uv.select_all(action='DESELECT')

                    # Selecciona la cara en la que está el iterador
                    for vert in face.loops:
                        vert[uv_layer].select = True

                    # Selecciona el resto de la Island
                    bpy.ops.uv.select_linked()

                    # Define los valores aleatorios
                    x_rand = random.uniform(x_min, x_max)
                    y_rand = random.uniform(y_min, y_max)
                    
                    # Mueve la Island
                    if bpy.app.version[0] >= 3:
                        bpy.ops.transform.translate(value=(x_rand, y_rand, 0), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    else:
                        bpy.ops.transform.translate(value=(x_rand, y_rand, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

                    # Quita las caras duplicadas del selected_uv_faces
                    temp_selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
                    selected_uv_faces = CompareListsAndRemoveElements(selected_uv_faces, temp_selected_uv_faces)

                facenumber += 1
        
        # Vuelve a dejar las caras como estaban
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces_before_applying_operator)

        bmesh.update_edit_mesh(me)
        
        if hasToReturn == True:
            bpy.ops.object.editmode_toggle()
        
        self.report({'INFO'}, "RANDOM TRANSLATE: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_UvRandomSwapFaces(bpy.types.Operator):
    """Randomly swap all the mesh uv faces between each other"""
    bl_idname = "uv.uvrandomizer_random_swap_uv_faces"
    bl_label = "All UV Faces"

    def execute(self, context):
        
        # Solo funciona en Object Mode, pero el script lo acomoda
        bpy.context.area.type = 'VIEW_3D'
        facenumber = 0

        hasToReturn = False

        if bpy.context.mode != 'OBJECT':
            hasToReturn = True
            originalMode = bpy.context.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        #retrieve mesh in object mode
        mesh = bpy.context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_layer = bm.loops.layers.uv.active        
        
        # Consigue las caras seleccionadas, para dejarlas como estaban luego de finalizar
        bpy.ops.object.editmode_toggle()

        selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)

        bpy.ops.object.editmode_toggle()

        # Consigue los centroides
        xcentroid, ycentroid, randomFaceOrder = GetFaceInfo_EditMode(bm, uv_layer, 0, True, True, False)

        # Randomiza el orden de las caras
        random.shuffle(randomFaceOrder)
        
        # Mueve las caras en función de lo anterior
        facenumber = 0

        for face in bm.faces:
            tempMoveX = xcentroid[randomFaceOrder[facenumber]] - xcentroid[facenumber]
            tempMoveY = ycentroid[randomFaceOrder[facenumber]] - ycentroid[facenumber]

            for vert in face.loops:            
                vert[uv_layer].uv[0] += tempMoveX
                vert[uv_layer].uv[1] += tempMoveY

            facenumber += 1        
        
        # Vuelve a dejar las caras como estaban
        bpy.ops.object.editmode_toggle()
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces)
        bpy.ops.object.editmode_toggle()

        #write the mesh back if you changed the uvs
        bm.to_mesh(mesh)
        bm.free()

        if hasToReturn == True:
            if "EDIT" in originalMode:
                originalMode = "EDIT"
            elif "SCULPT" in originalMode:
                originalMode = "SCULPT"
            elif "VERTEX" in originalMode:
                originalMode = "VERTEX_PAINT"
            elif "WEIGHT" in originalMode:
                originalMode = "WEIGHT_PAINT"
            elif "TEXTURE" in originalMode:
                originalMode = "TEXTURE_PAINT"
            else:
                originalMode = "OBJECT"
            bpy.ops.object.mode_set(mode=originalMode)

        bpy.context.area.type = 'IMAGE_EDITOR'
        self.report({'INFO'}, "RANDOM SWAP: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_UvRandomSwapSelectedFaces(bpy.types.Operator):
    """Randomly swap the selected uv faces between each other"""
    bl_idname = "uv.uvrandomizer_random_swap_selected_uv_faces"
    bl_label = "Selected UV Faces"

    def execute(self, context):
        
        # Solo funciona en edit mode
        if "EDIT" not in bpy.context.mode:
            self.report({'WARNING'}, "Random Swap only works in Edit Mode")
            return {'FINISHED'}

        #  GET THE SELECTED UV FACES, AND STORE IT IN selected_uv_faces

        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active

        selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
            
        if selected_uv_faces == []:
            self.report({'WARNING'}, "No faces selected") 
            return {'FINISHED'}

        #  GET THE CENTROIDS
        xcentroid, ycentroid, randomFaceOrder = GetFaceInfo_EditMode(bm, uv_layer, selected_uv_faces, True, True, False)

        # Randomiza el orden de las caras a utilizar 
        random.shuffle(randomFaceOrder)

        # Mueve las caras en función de lo anterior
        facenumber = 0
        selectedUvFaceIndex = 0

        for face in bm.faces:
            if facenumber in selected_uv_faces:
                tempMoveX = xcentroid[randomFaceOrder[selectedUvFaceIndex]] - xcentroid[selectedUvFaceIndex]
                tempMoveY = ycentroid[randomFaceOrder[selectedUvFaceIndex]] - ycentroid[selectedUvFaceIndex]

                for vert in face.loops:            
                    vert[uv_layer].uv[0] += tempMoveX
                    vert[uv_layer].uv[1] += tempMoveY
                selectedUvFaceIndex += 1

            facenumber += 1

        #write the mesh back if you changed the uvs
        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, "RANDOM SWAP: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_UvRandomShuffleSelectedFaces(bpy.types.Operator):
    """Randomly shuffle the selected uv faces along the UV Map"""
    bl_idname = "uv.uvrandomizer_random_shuffle_selected_uv_faces"
    bl_label = "Selected UV Faces"

    def execute(self, context):
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            self.report({'WARNING'}, "Random Shuffle only works in Edit Mode")
            return {'FINISHED'}

        #  GET THE SELECTED UV FACES, AND STORE IT IN selected_uv_faces
        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active

        selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)

        # ARMA LOS BOUNDING BOX
        xminface, xmaxface, yminface, ymaxface = GetFaceInfo_EditMode(bm, uv_layer, selected_uv_faces, False, False, True)

        # CALCULA EL PUNTO 0.0 DE TODAS LAS CARAS, Y LE SUMA LA REDISTRIBUCIÓN
        facenumber = 0
        selectedUvFaceIndex = 0

        for face in bm.faces:
            if facenumber in selected_uv_faces:
                # CALCULA EL PUNTO 0.0 DE LA CARA
                tempMoveX = -xminface[selectedUvFaceIndex]
                tempMoveY = -yminface[selectedUvFaceIndex]

                # CALCULA EL BOUNDING BOX
                facexlenght = xmaxface[selectedUvFaceIndex] - xminface[selectedUvFaceIndex]
                faceylenght = ymaxface[selectedUvFaceIndex] - yminface[selectedUvFaceIndex]

                # CALCULA EL ESPACIO EN EL QUE PUEDE MOVERSE EL BOUNDING BOX SIN SALIR DEL UVMAP
                tempMaxXTranslate = 1 - facexlenght
                tempMaxYTranslate = 1 - faceylenght

                # SUMA EL LARGO DEL TRASLADO, EN FUNCIÓN DEL LARGO DE LA CARA
                tempMoveX += random.uniform(0, tempMaxXTranslate)
                tempMoveY += random.uniform(0, tempMaxYTranslate)

                # MUEVE LAS CARAS
                for vert in face.loops:            
                    vert[uv_layer].uv[0] += tempMoveX
                    vert[uv_layer].uv[1] += tempMoveY 
                
                selectedUvFaceIndex += 1      

            facenumber += 1

        #write the mesh back if you changed the uvs
        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, "RANDOM SHUFFLE: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_UvRandomShuffleFaces(bpy.types.Operator):
    """Randomly shuffle all the UV faces along the UV Map"""
    bl_idname = "uv.uvrandomizer_random_shuffle_uv_faces"
    bl_label = "All UV Faces"

    def execute(self, context):
        
        hasToReturn = False

        # SE USA EN OBJECT MODE        
        if bpy.context.mode != 'OBJECT':
            hasToReturn = True
            originalMode = bpy.context.mode
            bpy.ops.object.mode_set(mode='OBJECT')
        
        #retrieve mesh in object mode

        mesh = bpy.context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_layer = bm.loops.layers.uv.active
        
        # Consigue las caras seleccionadas, para dejarlas como estaban luego de finalizar
        bpy.ops.object.editmode_toggle()

        selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)

        bpy.ops.object.editmode_toggle()

        xminface, xmaxface, yminface, ymaxface = GetFaceInfo_EditMode(bm, uv_layer, 0, False, False, True)

        # CALCULA EL PUNTO 0.0 DE TODAS LAS CARAS, Y LE SUMA LA REDISTRIBUCIÓN
        facenumber = 0

        for face in bm.faces:
            # CALCULA EL PUNTO 0.0 DE LA CARA
            tempMoveX = -xminface[facenumber]
            tempMoveY = -yminface[facenumber]

            # CALCULA EL BOUNDING BOX
            facexlenght = xmaxface[facenumber] - xminface[facenumber]
            faceylenght = ymaxface[facenumber] - yminface[facenumber]

            # CALCULA EL ESPACIO EN EL QUE PUEDE MOVERSE EL BOUNDING BOX SIN SALIR DEL UVMAP
            tempMaxXTranslate = 1 - facexlenght
            tempMaxYTranslate = 1 - faceylenght

            # SUMA EL LARGO DEL TRASLADO, EN FUNCIÓN DEL LARGO DE LA CARA
            tempMoveX += random.uniform(0, tempMaxXTranslate)
            tempMoveY += random.uniform(0, tempMaxYTranslate)

            # MUEVE LAS CARAS
            for vert in face.loops:            
                vert[uv_layer].uv[0] += tempMoveX
                vert[uv_layer].uv[1] += tempMoveY         

            facenumber += 1
        
        # Vuelve a dejar las caras como estaban
        bpy.ops.object.editmode_toggle()
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces)
        bpy.ops.object.editmode_toggle()

        #write the mesh back if you changed the uvs
        bm.to_mesh(mesh)
        bm.free()

        if hasToReturn == True:
            if "EDIT" in originalMode:
                originalMode = "EDIT"
            elif "SCULPT" in originalMode:
                originalMode = "SCULPT"
            elif "VERTEX" in originalMode:
                originalMode = "VERTEX_PAINT"
            elif "WEIGHT" in originalMode:
                originalMode = "WEIGHT_PAINT"
            elif "TEXTURE" in originalMode:
                originalMode = "TEXTURE_PAINT"
            else:
                originalMode = "OBJECT"
            bpy.ops.object.mode_set(mode=originalMode)

        bpy.context.area.type = 'IMAGE_EDITOR'
        self.report({'INFO'}, "RANDOM SHUFFLE: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_RandomRotateSelected(bpy.types.Operator):
    """Rotate selected faces"""
    bl_idname = "uv.uvrandomizer_rotate_selected_uv"
    bl_label = "Selected UV Faces"
    
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

        keep_islands = UVRandomTranslateProps.keepIslands

        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active

        # Indexa las caras seleccionadas
        selected_uv_faces_before_applying_operator = GetSelectedUVFaces_InEditMode(bm, uv_layer)
        selected_uv_faces = selected_uv_faces_before_applying_operator.copy()

        bpy.ops.uv.select_all(action='DESELECT')
        
        # Establece una rotación para aplicar a todas las caras, para el caso de que se haya seleccionado esa opción (sameRandom == True)
        if clampEnabled:
            tempVar1 = 360 / clampValue
            randTimes = int(random.uniform(0, int(tempVar1)))
            currentRot =  radians(randTimes * clampValue)            
        else:
            currentRot = radians(random.uniform(rot_min, rot_max))

        # Rota las caras
        facenumber = 0

        if keep_islands == False:
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
        else:
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    # Primero des-selecciona todo
                    bpy.ops.uv.select_all(action='DESELECT')

                    # Selecciona la cara en la que está el iterador
                    for vert in face.loops:
                        vert[uv_layer].select = True

                    # Selecciona el resto de la Island
                    bpy.ops.uv.select_linked()

                    # Rota las islands
                    bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                    if sameRandom == False:
                        if clampEnabled:
                            tempVar1 = 360 / clampValue
                            randTimes = int(random.uniform(0, int(tempVar1)))
                            currentRot =  radians(randTimes * clampValue)            
                        else:
                            currentRot = radians(random.uniform(rot_min, rot_max))
                    bpy.ops.transform.rotate(value=currentRot, orient_axis='Z', orient_type='VIEW', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='VIEW', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

                    # Quita las caras duplicadas del selected_uv_faces
                    temp_selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
                    selected_uv_faces = CompareListsAndRemoveElements(selected_uv_faces, temp_selected_uv_faces)
                facenumber += 1

        # Se asegura de que queden seleccionados solo los vértices de las caras utilizadas
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces_before_applying_operator)

        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, "RANDOM ROTATION: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_RandomRotateAll(bpy.types.Operator):
    """Randomly rotate all the uv faces"""
    bl_idname = "uv.uvrandomizer_rotate_uv"
    bl_label = "All UV Faces"

    def execute(self, context):
        
        hasToReturn = False
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            hasToReturn = True
            bpy.ops.object.editmode_toggle()            
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        rot_min = UVRandomTranslateProps.rotMin
        rot_max = UVRandomTranslateProps.rotMax
        
        sameRandom = UVRandomTranslateProps.applySameRandomRot

        clampEnabled = UVRandomTranslateProps.clampValueRotEnabled
        clampValue = UVRandomTranslateProps.clampValue

        keep_islands = UVRandomTranslateProps.keepIslands

        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active
        
        # Consigue las caras seleccionadas, para dejarlas como estaban luego de finalizar
        selected_uv_faces_before_applying_operator = GetSelectedUVFaces_InEditMode(bm, uv_layer)
        selected_uv_faces = selected_uv_faces_before_applying_operator.copy()

        bpy.ops.uv.select_all(action='DESELECT')
        
        # Establece una rotación para aplicar a todas las caras, para el caso de que se haya seleccionado esa opción (sameRandom == True)
        if clampEnabled:
            tempVar1 = 360 / clampValue
            randTimes = int(random.uniform(0, int(tempVar1)))
            currentRot =  radians(randTimes * clampValue)            
        else:
            currentRot = radians(random.uniform(rot_min, rot_max))

        # Rota las caras       

        if keep_islands == False:
            for face in bm.faces:
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
        else:

            # ESTA PARTE LA TRATA COMO A UN RANDOM-ROTATE-SELECTED, PERO CON TODAS LAS CARAS SELECCIONADAS
            # PARA PODER HACER LAS COMPARACIONES Y NO MOVER MUCHAS VECES LA MISMA ISLAND

            facenumber = 0

            bpy.ops.uv.select_all(action='SELECT')
            selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    # Primero des-selecciona todo
                    bpy.ops.uv.select_all(action='DESELECT')

                    # Selecciona la cara en la que está el iterador
                    for vert in face.loops:
                        vert[uv_layer].select = True

                    # Selecciona el resto de la Island
                    bpy.ops.uv.select_linked()

                    # Rota las islands
                    bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                    if sameRandom == False:
                        if clampEnabled:
                            tempVar1 = 360 / clampValue
                            randTimes = int(random.uniform(0, int(tempVar1)))
                            currentRot =  radians(randTimes * clampValue)            
                        else:
                            currentRot = radians(random.uniform(rot_min, rot_max))
                    bpy.ops.transform.rotate(value=currentRot, orient_axis='Z', orient_type='VIEW', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='VIEW', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)                    
                    
                    # Quita las caras duplicadas del selected_uv_faces
                    temp_selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
                    selected_uv_faces = CompareListsAndRemoveElements(selected_uv_faces, temp_selected_uv_faces)
                facenumber += 1
        
        # Vuelve a dejar las caras como estaban
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces_before_applying_operator)

        bmesh.update_edit_mesh(me)
        
        if hasToReturn == True:
            bpy.ops.object.editmode_toggle()
        
        self.report({'INFO'}, "RANDOM ROTATION: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_RandomScaleSelected(bpy.types.Operator):
    """Randomly Scale selected faces"""
    bl_idname = "uv.uvrandomizer_scale_selected_uv"
    bl_label = "Selected UV Faces"
    
    def execute(self, context):
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            self.report({'WARNING'}, "Random Rotation only works in Edit Mode")
            return {'FINISHED'}
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        scale_min = UVRandomTranslateProps.scaleMin
        scale_max = UVRandomTranslateProps.scaleMax
        
        sameRandomScale = UVRandomTranslateProps.applySameRandomScale
        evenScale = UVRandomTranslateProps.applyEvenScale

        keep_islands = UVRandomTranslateProps.keepIslands

        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active

        # Indexa las caras seleccionadas
        selected_uv_faces_before_applying_operator = GetSelectedUVFaces_InEditMode(bm, uv_layer)
        selected_uv_faces = selected_uv_faces_before_applying_operator.copy()

        bpy.ops.uv.select_all(action='DESELECT')
        
        # Establece una escala para aplicar a todas las caras, para el caso de que se haya seleccionado esa opción (sameRandomScale == True)
        currentScale = random.uniform(scale_min, scale_max)
        currentScale2 = random.uniform(scale_min, scale_max)

        # Aplica el scaling las caras
        facenumber = 0

        if keep_islands == False:
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
                    for vert in face.loops:
                        vert[uv_layer].select = True                    

                    bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                    if sameRandomScale == False:
                        currentScale = random.uniform(scale_min, scale_max)
                        currentScale2 = random.uniform(scale_min, scale_max)
                    bpy.ops.transform.resize(value=(currentScale, currentScale, currentScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    if evenScale == False:
                        bpy.ops.transform.resize(value=(1, currentScale2, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    bpy.ops.uv.select_all(action='DESELECT')
                facenumber += 1
        else:
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    # Primero des-selecciona todo
                    bpy.ops.uv.select_all(action='DESELECT')

                    # Selecciona la cara en la que está el iterador
                    for vert in face.loops:
                        vert[uv_layer].select = True

                    # Selecciona el resto de la Island
                    bpy.ops.uv.select_linked()

                    # Aplica el Resize las islands
                    bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                    if sameRandomScale == False:
                        currentScale = random.uniform(scale_min, scale_max)
                        currentScale2 = random.uniform(scale_min, scale_max)
                    bpy.ops.transform.resize(value=(currentScale, currentScale, currentScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    if evenScale == False:
                        bpy.ops.transform.resize(value=(1, currentScale2, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    
                    # Quita las caras duplicadas del selected_uv_faces
                    temp_selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
                    selected_uv_faces = CompareListsAndRemoveElements(selected_uv_faces, temp_selected_uv_faces)
                facenumber += 1

        # Se asegura de que queden seleccionados solo los vértices de las caras utilizadas
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces_before_applying_operator)

        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, "RANDOM SCALING: Done!")
        return {'FINISHED'}
    
class UVRANDOMIZER_OT_RandomScaleAll(bpy.types.Operator):
    """Randomly scale all the uv faces"""
    bl_idname = "uv.uvrandomizer_scale_uv"
    bl_label = "All UV Faces"

    def execute(self, context):
        
        hasToReturn = False
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            hasToReturn = True
            bpy.ops.object.editmode_toggle()            
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        scale_min = UVRandomTranslateProps.scaleMin
        scale_max = UVRandomTranslateProps.scaleMax
        
        sameRandomScale = UVRandomTranslateProps.applySameRandomScale
        applyEvenScale = UVRandomTranslateProps.applyEvenScale

        keep_islands = UVRandomTranslateProps.keepIslands

        # Get a BMesh representation
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active
        
        # Consigue las caras seleccionadas, para dejarlas como estaban luego de finalizar
        selected_uv_faces_before_applying_operator = GetSelectedUVFaces_InEditMode(bm, uv_layer)
        selected_uv_faces = selected_uv_faces_before_applying_operator.copy()

        bpy.ops.uv.select_all(action='DESELECT')
        
        # Establece una escala para aplicar a todas las caras, para el caso de que se haya seleccionado esa opción (sameRandomScale == True)
        currentScale = random.uniform(scale_min, scale_max)
        currentScale2 = random.uniform(scale_min, scale_max)

        # Aplica el scaling a las caras
        if keep_islands == False:
            for face in bm.faces:
                bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
                for vert in face.loops:
                    vert[uv_layer].select = True
                bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                if sameRandomScale == False:
                    currentScale = random.uniform(scale_min, scale_max)
                    currentScale2 = random.uniform(scale_min, scale_max)
                bpy.ops.transform.resize(value=(currentScale, currentScale, currentScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                if applyEvenScale == False:
                    bpy.ops.transform.resize(value=(1, currentScale2, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                bpy.ops.uv.select_all(action='DESELECT')
        else:
            facenumber = 0
            bpy.ops.uv.select_all(action='SELECT')
            selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
            for face in bm.faces:
                if facenumber in selected_uv_faces:
                    # Primero des-selecciona todo
                    bpy.ops.uv.select_all(action='DESELECT')

                    # Selecciona la cara en la que está el iterador
                    for vert in face.loops:
                        vert[uv_layer].select = True

                    # Selecciona el resto de la Island
                    bpy.ops.uv.select_linked()

                    # Aplica el Resize las islands
                    bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
                    if sameRandomScale == False:
                        currentScale = random.uniform(scale_min, scale_max)
                        currentScale2 = random.uniform(scale_min, scale_max)
                    bpy.ops.transform.resize(value=(currentScale, currentScale, currentScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    if applyEvenScale == False:
                        bpy.ops.transform.resize(value=(1, currentScale2, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    
                    # Quita las caras duplicadas del selected_uv_faces
                    temp_selected_uv_faces = GetSelectedUVFaces_InEditMode(bm, uv_layer)
                    selected_uv_faces = CompareListsAndRemoveElements(selected_uv_faces, temp_selected_uv_faces)
                facenumber += 1
            
        
        # Vuelve a dejar las caras como estaban
        SetSelectedFaces_InEditMode(bm, uv_layer, selected_uv_faces_before_applying_operator)

        bmesh.update_edit_mesh(me)
        
        if hasToReturn == True:
            bpy.ops.object.editmode_toggle()
        
        self.report({'INFO'}, "RANDOM SCALING: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_DoEverythingAll(bpy.types.Operator):
    """Apply the selected functions to all the UV faces"""
    bl_idname = "uv.uvrandomizer_do_everything_all"
    bl_label = "All UV faces"

    def execute(self, context):
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        do_translate = UVRandomTranslateProps.doTranslate
        do_rotation = UVRandomTranslateProps.doRotation
        do_scaling = UVRandomTranslateProps.doScaling
        do_swap = UVRandomTranslateProps.doSwap
        do_shuffle = UVRandomTranslateProps.doShuffle
        
        if do_translate == True:
            bpy.ops.uv.uvrandomizer_random_translate()
        
        if do_rotation == True:
            bpy.ops.uv.uvrandomizer_rotate_uv()
        
        if do_scaling == True:
            bpy.ops.uv.uvrandomizer_scale_uv()
        
        if do_swap == True:
            bpy.ops.uv.uvrandomizer_random_swap_uv_faces()
        
        if do_shuffle == True:
            bpy.ops.uv.uvrandomizer_random_shuffle_uv_faces()

        
        self.report({'INFO'}, "DO EVERYTHING: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_OT_DoEverythingSelected(bpy.types.Operator):
    """Apply the selected functions to the selected the UV faces"""
    bl_idname = "uv.uvrandomizer_do_everything_selected"
    bl_label = "Selected UV faces"

    def execute(self, context):
        
        # Solo funciona en Edit Mode
        if "EDIT" not in bpy.context.mode:
            self.report({'WARNING'}, "Only works in Edit Mode!")
            return {'FINISHED'}
        
        # Consigue las variables desde el panel
        scene = context.scene
        UVRandomTranslateProps = scene.UVRandomTranslateProps        
            
        do_translate = UVRandomTranslateProps.doTranslate
        do_rotation = UVRandomTranslateProps.doRotation
        do_scaling = UVRandomTranslateProps.doScaling
        do_swap = UVRandomTranslateProps.doSwap
        do_shuffle = UVRandomTranslateProps.doShuffle
        
        if do_translate == True:
            bpy.ops.uv.uvrandomizer_random_translate_selected()
        
        if do_rotation == True:
            bpy.ops.uv.uvrandomizer_rotate_selected_uv()
        
        if do_scaling == True:
            bpy.ops.uv.uvrandomizer_scale_selected_uv()
            
        if do_swap == True:
            bpy.ops.uv.uvrandomizer_random_swap_selected_uv_faces()
        
        if do_shuffle == True:
            bpy.ops.uv.uvrandomizer_random_shuffle_selected_uv_faces()

        
        self.report({'INFO'}, "DO EVERYTHING: Done!")
        return {'FINISHED'}

class UVRANDOMIZER_PT_UVRandomizer(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "UV Ramdomizer"
    bl_label = "UV Randomizer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        UVRandomTranslateProps = scene.UVRandomTranslateProps
        obj = context.object
        
        row = layout.row()
        row.label(text="GENERAL SETTINGS")
        box = layout.box()
        mcol = box.column()
        mcol.prop(UVRandomTranslateProps, "keepIslands")
        keepIslandsText = "Only works with Translate, Rotate and Scale"
        _label_multiline(context=context, text=keepIslandsText, parent=mcol)
        #mcol.label(text="Only works with Translate, Rotate and Scale")

        row = layout.row()
        row.label(text="TRANSLATE FACES")
        
        box = layout.box()
        mcol = box.column(align=True)
        mcol.prop(UVRandomTranslateProps, "useXAxis")
        split = mcol.split(align=True)
        
        col1 = split.column(align=True)
        col1.prop(UVRandomTranslateProps, "minX")
        
        col2 = split.column(align=True)
        col2.prop(UVRandomTranslateProps, "maxX")
        
        row = mcol.row(align=True)
        mcol.prop(UVRandomTranslateProps, "useYAxis")
        split = mcol.split(align=True)
        
        col1 = split.column(align=True)
        col1.prop(UVRandomTranslateProps, "minY")
        
        col2 = split.column(align=True)
        col2.prop(UVRandomTranslateProps, "maxX")
        row = mcol.row(align=True)
        row.operator("uv.uvrandomizer_random_translate_selected", icon= 'CON_TRANSLIKE')
        row = mcol.row(align=True)
        row.operator("uv.uvrandomizer_random_translate", icon= 'CON_TRANSLIKE')        
        
        row = layout.row()
        row.label(text="SWAP FACES")
        
        box2 = layout.box()
        col = box2.column(align=True)
        row2 = col.row(align=True)        
        row2.operator("uv.uvrandomizer_random_swap_selected_uv_faces", icon= 'NODE_COMPOSITING')
        row2 = col.row(align=True)
        row2.operator("uv.uvrandomizer_random_swap_uv_faces", icon= 'NODE_COMPOSITING')        
        
        
        row = layout.row()
        row.label(text="SHUFFLE FACES")
        
        box2 = layout.box()
        col = box2.column(align=True)
        row2 = col.row(align=True)        
        row2.operator("uv.uvrandomizer_random_shuffle_selected_uv_faces", icon= 'NODE_COMPOSITING')
        row2 = col.row(align=True)
        row2.operator("uv.uvrandomizer_random_shuffle_uv_faces", icon= 'NODE_COMPOSITING')        
        
        row = layout.row()
        row.label(text="ROTATE FACES")
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Min/Max Rotation")
        split = col.split(align=True)
        col1 = split.column(align=True)
        col1.prop(UVRandomTranslateProps, "rotMin")
        
        col2 = split.column(align=True)
        col2.prop(UVRandomTranslateProps, "rotMax")
        
        row = box.row(align=True)
        row.prop(UVRandomTranslateProps, "applySameRandomRot")
        row = box.row(align=True)
        row.prop(UVRandomTranslateProps, "clampValueRotEnabled")
        row.prop(UVRandomTranslateProps, "clampValue")
        
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("uv.uvrandomizer_rotate_selected_uv", icon= 'DRIVER_ROTATIONAL_DIFFERENCE')
        row = col.row(align=True)
        row.operator("uv.uvrandomizer_rotate_uv", icon= 'DRIVER_ROTATIONAL_DIFFERENCE')
        
        row = layout.row()
        row.label(text="SCALE FACES")
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Min/Max Scaling")
        split = col.split(align=True)
        col1 = split.column(align=True)
        col1.prop(UVRandomTranslateProps, "scaleMin")
        
        col2 = split.column(align=True)
        col2.prop(UVRandomTranslateProps, "scaleMax")
        
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "applySameRandomScale")
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "applyEvenScale")
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("uv.uvrandomizer_scale_selected_uv", icon= 'ARROW_LEFTRIGHT')        
        row = col.row(align=True)
        row.operator("uv.uvrandomizer_scale_uv", icon= 'ARROW_LEFTRIGHT')
        
        row = layout.row()
        row.label(text="DO EVERYTHING")
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "doTranslate")
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "doRotation")
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "doScaling")
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "doSwap")
        row = col.row(align=True)
        row.prop(UVRandomTranslateProps, "doShuffle")
        row = col.row(align=True)
        row.label(text="Apply to:")
        row = col.row(align=True)
        row.operator("uv.uvrandomizer_do_everything_selected", icon= 'SHADERFX')
        row = col.row(align=True)
        row.operator("uv.uvrandomizer_do_everything_all", icon= 'SHADERFX') 

classes = [UVRANDOMIZER_PG_UvRandomizer, UVRANDOMIZER_OT_UvRandomTranslateSelected, UVRANDOMIZER_PT_UVRandomizer, UVRANDOMIZER_OT_UvRandomSwapFaces, UVRANDOMIZER_OT_UvRandomSwapSelectedFaces, UVRANDOMIZER_OT_UvRandomShuffleFaces, UVRANDOMIZER_OT_UvRandomShuffleSelectedFaces, UVRANDOMIZER_OT_RandomRotateSelected, UVRANDOMIZER_OT_RandomRotateAll, UVRANDOMIZER_OT_RandomScaleSelected, UVRANDOMIZER_OT_RandomScaleAll, UVRANDOMIZER_OT_DoEverythingAll, UVRANDOMIZER_OT_DoEverythingSelected, UVRANDOMIZER_OT_RandomTranslateAll]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
		bpy.types.Scene.UVRandomTranslateProps = bpy.props.PointerProperty(type= UVRANDOMIZER_PG_UvRandomizer)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
		bpy.types.Scene.UVRandomTranslateProps

if __name__ == "__main__":
    register()