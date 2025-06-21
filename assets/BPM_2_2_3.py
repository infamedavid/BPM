import bpy
import os

bl_info = {
    "name": "Project Management (Core & External Data)",
    "author": "Tu Nombre/Gemini (Asistencia)",
    "version": (2, 2, 2), # Versión incrementada por corrección del operador Link.
    "blender": (4, 0, 0),
    "location": "File > Project Management & 3D Viewport > N-Panel > BPM Tab",
    "description": "Crea una estructura de carpetas de proyecto y gestiona datos externos (texturas y assets linkeados).",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

# --- Helper Function for Path Checking ---
def is_path_in_project_tree(filepath, project_root_path):
    """
    Checks if the given filepath is inside the project_root_path.
    Normalizes paths for robust comparison.
    """
    if not project_root_path:
        return False # No project root path defined
    
    # Normalize paths to handle different OS path separators and relative paths
    abs_filepath = os.path.abspath(bpy.path.abspath(filepath))
    abs_root_path = os.path.abspath(project_root_path)
    
    # Ensure root path ends with a separator for correct 'startswith' comparison
    if not abs_root_path.endswith(os.sep):
        abs_root_path += os.sep
        
    return abs_filepath.startswith(abs_root_path)

# --- Property Group for Addon Settings ---
class BPM_Props(bpy.types.PropertyGroup):
    save_file: bpy.props.BoolProperty(
        name="Save file",
        description="Guarda el archivo .blend después de desempaquetar las texturas.",
        default=True
    )
    project_root_path: bpy.props.StringProperty(
        name="Project Root Folder",
        description="La carpeta raíz del proyecto actual (donde se encuentra la estructura principal).",
    )

# --- Operator for Project Tree Creation ---
class PM_OT_OpenFileBrowser(bpy.types.Operator):
    bl_label = "Plant the Tree"
    bl_idname = "pm.open_file_browser"
    bl_description = "Abre el Explorador de Archivos para seleccionar un directorio y crear el proyecto."
    bl_options = {'REGISTER'}

    MAX_PATH_LIMIT = 200 # Standard safe limit for Windows MAX_PATH

    project_name: bpy.props.StringProperty(name="Project Name", default="New Project")
    numerate_folders: bpy.props.BoolProperty(name="Numerate folders", default=True)

    create_preproduction: bpy.props.BoolProperty(name="Pre-production", default=True)
    exp_preproduction: bpy.props.BoolProperty(default=False)
    create_script: bpy.props.BoolProperty(name="Script", default=True)
    create_concept_art: bpy.props.BoolProperty(name="Concept Art", default=True)
    exp_concept_art: bpy.props.BoolProperty(default=False)
    create_concept_art_characters: bpy.props.BoolProperty(name="Characters", default=True)
    create_concept_art_sets: bpy.props.BoolProperty(name="Sets", default=True)
    create_concept_art_props: bpy.props.BoolProperty(name="Props", default=True)
    create_storyboard: bpy.props.BoolProperty(name="Storyboard", default=True)
    create_animatic: bpy.props.BoolProperty(name="Animatic", default=True)
    create_reference: bpy.props.BoolProperty(name="Reference", default=True)
    create_research: bpy.props.BoolProperty(name="Research", default=True)

    create_production: bpy.props.BoolProperty(name="Production", default=True)
    exp_production: bpy.props.BoolProperty(default=False)
    create_assets: bpy.props.BoolProperty(name="Assets", default=True)
    exp_assets: bpy.props.BoolProperty(default=False)
    create_models: bpy.props.BoolProperty(name="Models", default=True)
    exp_models: bpy.props.BoolProperty(default=False)
    create_models_characters: bpy.props.BoolProperty(name="Characters", default=True)
    create_models_scenarios: bpy.props.BoolProperty(name="Scenarios", default=True)
    create_models_props: bpy.props.BoolProperty(name="Props", default=True)
    create_scenes_layout: bpy.props.BoolProperty(name="Scenes (Layout)", default=True) 
    create_animation: bpy.props.BoolProperty(name="Animation", default=True)
    exp_animation: bpy.props.BoolProperty(default=False)
    create_animation_blocking: bpy.props.BoolProperty(name="Blocking", default=True)
    create_animation_spline: bpy.props.BoolProperty(name="Spline", default=True)
    create_animation_cleanup: bpy.props.BoolProperty(name="Cleanup", default=True)
    create_libraries: bpy.props.BoolProperty(name="Libraries", default=True)
    exp_libraries: bpy.props.BoolProperty(default=False)
    create_textures_lib: bpy.props.BoolProperty(name="Textures", default=True)
    exp_textures_lib: bpy.props.BoolProperty(default=False)
    create_textures_lib_characters: bpy.props.BoolProperty(name="Characters", default=True)
    create_textures_lib_props: bpy.props.BoolProperty(name="Props", default=True)
    create_textures_lib_environments: bpy.props.BoolProperty(name="Environments", default=True) 
    create_textures_lib_hdris: bpy.props.BoolProperty(name="HDRIs", default=True)
    create_addons_lib: bpy.props.BoolProperty(name="Addons", default=True)
    create_extras_lib: bpy.props.BoolProperty(name="Extras", default=True)

    create_postproduction: bpy.props.BoolProperty(name="Post-production", default=True)
    exp_postproduction: bpy.props.BoolProperty(default=False)
    create_renders: bpy.props.BoolProperty(name="Renders", default=True)
    create_editing: bpy.props.BoolProperty(name="Editing", default=True)
    create_sound: bpy.props.BoolProperty(name="Sound", default=True)
    exp_sound: bpy.props.BoolProperty(default=False)
    create_sound_voices: bpy.props.BoolProperty(name="Voices", default=True)
    create_sound_music: bpy.props.BoolProperty(name="Music", default=True)
    create_sound_effects: bpy.props.BoolProperty(name="Effects", default=True)
    create_composite: bpy.props.BoolProperty(name="Composite", default=True)
    create_exports: bpy.props.BoolProperty(name="Exports", default=True)
    exp_exports: bpy.props.BoolProperty(default=False)
    create_exports_previews: bpy.props.BoolProperty(name="Previews", default=True)
    create_exports_final_versions: bpy.props.BoolProperty(name="Final Versions", default=True)

    directory: bpy.props.StringProperty(
        name="Selected Path",
        subtype='DIR_PATH',
        description="The folder where the new project will be created."
    )

    def execute(self, context):
        project_name = self.project_name.strip()
        base_dir = self.directory

        if not project_name:
            self.report({'ERROR'}, "El nombre del proyecto no puede estar vacío.")
            return {'CANCELLED'}

        if not os.path.isdir(base_dir):
            self.report({'ERROR'}, f"El directorio base '{base_dir}' no es válido o no se pudo acceder.")
            return {'CANCELLED'}

        project_root_path = os.path.join(base_dir, project_name)

        if os.path.exists(project_root_path):
            self.report({'WARNING'}, f"La carpeta raíz '{project_name}' ya existe en: {base_dir}. Por favor, elija un nombre diferente o una ubicación diferente.")
            return {'CANCELLED'}

        project_structure_config = {
            "Pre-production": (self.create_preproduction, {
                "Script": (self.create_script, None),
                "Concept Art": (self.create_concept_art, {
                    "Characters": (self.create_concept_art_characters, None), "Sets": (self.create_concept_art_sets, None), "Props": (self.create_concept_art_props, None),
                }),
                "Storyboard": (self.create_storyboard, None), "Animatic": (self.create_animatic, None), "Reference": (self.create_reference, None), "Research": (self.create_research, None),
            }),
            "Production": (self.create_production, {
                "Assets": (self.create_assets, {
                    "Models": (self.create_models, {"Characters": (self.create_models_characters, None), "Scenarios": (self.create_models_scenarios, None), "Props": (self.create_models_props, None),}),
                }),
                "Scenes (Layout)": (self.create_scenes_layout, None),
                "Animation": (self.create_animation, {"Blocking": (self.create_animation_blocking, None), "Spline": (self.create_animation_spline, None), "Cleanup": (self.create_animation_cleanup, None),}),
                "Libraries": (self.create_libraries, {
                    "Textures": (self.create_textures_lib, {"Characters": (self.create_textures_lib_characters, None), "Props": (self.create_textures_lib_props, None), "Environments": (self.create_textures_lib_environments, None), "HDRIs": (self.create_textures_lib_hdris, None),}),
                    "Addons": (self.create_addons_lib, None), "Extras": (self.create_extras_lib, None),
                }),
            }),
            "Post-production": (self.create_postproduction, { 
                "Renders": (self.create_renders, None), "Editing": (self.create_editing, None),
                "Sound": (self.create_sound, {"Voices": (self.create_sound_voices, None), "Music": (self.create_sound_music, None), "Effects": (self.create_sound_effects, None),}),
                "Composite": (self.create_composite, None),
                "Exports": (self.create_exports, {"Previews": (self.create_exports_previews, None), "FinalVersions": (self.create_exports_final_versions, None),}),
            }),
        }

        top_level_phases_order = ["Pre-production", "Production", "Post-production"]
        
        top_level_folders_info = [] 
        for base_name in top_level_phases_order:
            should_create_prop, nested_structure_dict = project_structure_config.get(base_name, (False, None))
            if should_create_prop: 
                actual_name = base_name
                if self.numerate_folders:
                    actual_name = f"{len(top_level_folders_info) + 1:02d}_{base_name}"
                top_level_folders_info.append((actual_name, base_name, nested_structure_dict)) 

        all_paths_to_create = []

        def _collect_paths(current_parent_path, structure_dict):
            if not structure_dict: return
            current_items_for_order = []
            if current_parent_path.endswith("Production"):
                ordered_keys = ["Assets", "Scenes (Layout)", "Animation", "Libraries"]
                current_items_for_order = [(k, structure_dict[k]) for k in ordered_keys if k in structure_dict]
                remaining_items = [(k, v) for k, v in structure_dict.items() if k not in ordered_keys]
                current_items_for_order.extend(sorted(remaining_items, key=lambda item: item[0]))
            elif current_parent_path.endswith("Post-production"):
                ordered_keys = ["Renders", "Editing", "Sound", "Composite", "Exports"]
                current_items_for_order = [(k, structure_dict[k]) for k in ordered_keys if k in structure_dict]
                remaining_items = [(k, v) for k, v in structure_dict.items() if k not in ordered_keys]
                current_items_for_order.extend(sorted(remaining_items, key=lambda item: item[0]))
            else:
                current_items_for_order = sorted(structure_dict.items(), key=lambda item: item[0])

            for folder_base_name, (should_create_prop_obj, sub_nested_structure) in current_items_for_order:
                if should_create_prop_obj:
                    full_path = os.path.join(current_parent_path, folder_base_name)
                    all_paths_to_create.append(full_path)
                    if sub_nested_structure:
                        _collect_paths(full_path, sub_nested_structure)

        for actual_folder_name, base_folder_name, nested_structure_dict in top_level_folders_info:
            current_level_path = os.path.join(project_root_path, actual_folder_name)
            all_paths_to_create.append(current_level_path) 
            if nested_structure_dict:
                _collect_paths(current_level_path, nested_structure_dict)

        for path_to_validate in all_paths_to_create:
            if len(path_to_validate) > self.MAX_PATH_LIMIT:
                self.report({'ERROR'}, f"La ruta excede el límite de {self.MAX_PATH_LIMIT} caracteres (Windows MAX_PATH): '{path_to_validate}' ({len(path_to_validate)} caracteres). Por favor, acorte el nombre del proyecto o la ubicación.")
                return {'CANCELLED'}

        def _create_nested_folders(parent_path, structure_dict):
            if not structure_dict: return
            current_items_for_order = []
            if parent_path.endswith("Production"):
                ordered_keys = ["Assets", "Scenes (Layout)", "Animation", "Libraries"]
                current_items_for_order = [(k, structure_dict[k]) for k in ordered_keys if k in structure_dict]
                remaining_items = [(k, v) for k, v in structure_dict.items() if k not in ordered_keys]
                current_items_for_order.extend(sorted(remaining_items, key=lambda item: item[0]))
            elif parent_path.endswith("Post-production"):
                ordered_keys = ["Renders", "Editing", "Sound", "Composite", "Exports"]
                current_items_for_order = [(k, structure_dict[k]) for k in ordered_keys if k in structure_dict]
                remaining_items = [(k, v) for k, v in structure_dict.items() if k not in ordered_keys]
                current_items_for_order.extend(sorted(remaining_items, key=lambda item: item[0]))
            else:
                current_items_for_order = sorted(structure_dict.items(), key=lambda item: item[0])

            for folder_base_name, (should_create_prop_obj, sub_nested_structure) in current_items_for_order:
                if not should_create_prop_obj:
                    continue 

                full_nested_path = os.path.join(parent_path, folder_base_name)
                try:
                    os.makedirs(full_nested_path)
                    self.report({'INFO'}, f"  Subcarpeta creada: {full_nested_path}")
                except Exception as e:
                    self.report({'ERROR'}, f"Error al crear subcarpeta '{full_nested_path}': {e}")
                    return {'CANCELLED'} 
                
                if sub_nested_structure:
                    result = _create_nested_folders(full_nested_path, sub_nested_structure)
                    if result == {'CANCELLED'}:
                        return {'CANCELLED'}
            return {'FINISHED'}

        for actual_folder_name, base_folder_name, nested_structure_dict in top_level_folders_info:
            current_level_path = os.path.join(project_root_path, actual_folder_name)
            
            try:
                os.makedirs(current_level_path)
                self.report({'INFO'}, f"Carpeta creada: {current_level_path}")
            except Exception as e:
                self.report({'ERROR'}, f"Error al crear carpeta '{current_level_path}': {e}")
                return {'CANCELLED'} 

            if nested_structure_dict:
                result = _create_nested_folders(current_level_path, nested_structure_dict)
                if result == {'CANCELLED'}:
                    return {'CANCELLED'}
        
        self.report({'INFO'}, "Estructura del proyecto creada con éxito.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "project_name")
        layout.separator()
        layout.prop(self, "numerate_folders")
        layout.separator()
        
        # Pre-production
        box_pre = layout.box()
        pre_row = box_pre.row(align=True)
        pre_row.prop(self, "exp_preproduction", icon='TRIA_DOWN' if self.exp_preproduction else 'TRIA_RIGHT', icon_only=True, emboss=False)
        pre_row.prop(self, "create_preproduction", text="Pre-production")
        if self.exp_preproduction: 
            pre_children_col = box_pre.column(align=True) 
            
            # Script
            script_row = pre_children_col.row(align=True)
            script_row.label(icon='LAYER_ACTIVE')
            script_row.prop(self, "create_script", text="Script")
            
            # Concept Art
            concept_art_box = pre_children_col.box()
            concept_art_row = concept_art_box.row(align=True)
            concept_art_row.prop(self, "exp_concept_art", icon='TRIA_DOWN' if self.exp_concept_art else 'TRIA_RIGHT', icon_only=True, emboss=False)
            concept_art_row.prop(self, "create_concept_art", text="Concept Art")
            if self.exp_concept_art: 
                concept_art_children_col = concept_art_box.column(align=True) 
                concept_art_children_col.prop(self, "create_concept_art_characters")
                concept_art_children_col.prop(self, "create_concept_art_sets")
                concept_art_children_col.prop(self, "create_concept_art_props")
            
            # Storyboard
            storyboard_row = pre_children_col.row(align=True)
            storyboard_row.label(icon='LAYER_ACTIVE')
            storyboard_row.prop(self, "create_storyboard", text="Storyboard")
            
            # Animatic
            animatic_row = pre_children_col.row(align=True)
            animatic_row.label(icon='LAYER_ACTIVE')
            animatic_row.prop(self, "create_animatic", text="Animatic")
            
            # Reference
            reference_row = pre_children_col.row(align=True)
            reference_row.label(icon='LAYER_ACTIVE')
            reference_row.prop(self, "create_reference", text="Reference")
            
            # Research
            research_row = pre_children_col.row(align=True)
            research_row.label(icon='LAYER_ACTIVE')
            research_row.prop(self, "create_research", text="Research")

        # Production
        box_prod = layout.box()
        prod_row = box_prod.row(align=True)
        prod_row.prop(self, "exp_production", icon='TRIA_DOWN' if self.exp_production else 'TRIA_RIGHT', icon_only=True, emboss=False)
        prod_row.prop(self, "create_production", text="Production")
        if self.exp_production:
            prod_children_col = box_prod.column(align=True)
            
            # Assets
            assets_box = prod_children_col.box()
            assets_row = assets_box.row(align=True)
            assets_row.prop(self, "exp_assets", icon='TRIA_DOWN' if self.exp_assets else 'TRIA_RIGHT', icon_only=True, emboss=False)
            assets_row.prop(self, "create_assets", text="Assets")
            if self.exp_assets:
                assets_children_col = assets_box.column(align=True)
                models_box = assets_children_col.box()
                models_row = models_box.row(align=True)
                models_row.prop(self, "exp_models", icon='TRIA_DOWN' if self.exp_models else 'TRIA_RIGHT', icon_only=True, emboss=False)
                models_row.prop(self, "create_models", text="Models")
                if self.exp_models:
                    models_children_col = models_box.column(align=True)
                    models_children_col.prop(self, "create_models_characters")
                    models_children_col.prop(self, "create_models_scenarios")
                    models_children_col.prop(self, "create_models_props")
            
            # Scenes (Layout)
            scenes_layout_row = prod_children_col.row(align=True)
            scenes_layout_row.label(icon='LAYER_ACTIVE')
            scenes_layout_row.prop(self, "create_scenes_layout", text="Scenes (Layout)")
            
            # Animation
            animation_box = prod_children_col.box()
            animation_row = animation_box.row(align=True)
            animation_row.prop(self, "exp_animation", icon='TRIA_DOWN' if self.exp_animation else 'TRIA_RIGHT', icon_only=True, emboss=False)
            animation_row.prop(self, "create_animation", text="Animation")
            if self.exp_animation:
                animation_children_col = animation_box.column(align=True)
                animation_children_col.prop(self, "create_animation_blocking")
                animation_children_col.prop(self, "create_animation_spline")
                animation_children_col.prop(self, "create_animation_cleanup")
            
            # Libraries
            libraries_box = prod_children_col.box()
            libraries_row = libraries_box.row(align=True)
            libraries_row.prop(self, "exp_libraries", icon='TRIA_DOWN' if self.exp_libraries else 'TRIA_RIGHT', icon_only=True, emboss=False)
            libraries_row.prop(self, "create_libraries", text="Libraries")
            if self.exp_libraries:
                libraries_children_col = libraries_box.column(align=True)
                textures_lib_box = libraries_children_col.box()
                textures_lib_row = textures_lib_box.row(align=True)
                textures_lib_row.prop(self, "exp_textures_lib", icon='TRIA_DOWN' if self.exp_textures_lib else 'TRIA_RIGHT', icon_only=True, emboss=False)
                textures_lib_row.prop(self, "create_textures_lib", text="Textures")
                if self.exp_textures_lib:
                    textures_lib_children_col = textures_lib_box.column(align=True)
                    textures_lib_children_col.prop(self, "create_textures_lib_characters")
                    textures_lib_children_col.prop(self, "create_textures_lib_props")
                    textures_lib_children_col.prop(self, "create_textures_lib_environments")
                    textures_lib_children_col.prop(self, "create_textures_lib_hdris")
                
                # Addons
                addons_lib_row = libraries_children_col.row(align=True)
                addons_lib_row.label(icon='LAYER_ACTIVE')
                addons_lib_row.prop(self, "create_addons_lib", text="Addons")
                
                # Extras
                extras_lib_row = libraries_children_col.row(align=True)
                extras_lib_row.label(icon='LAYER_ACTIVE')
                extras_lib_row.prop(self, "create_extras_lib", text="Extras")

        # Post-production
        box_post = layout.box()
        post_row = box_post.row(align=True)
        post_row.prop(self, "exp_postproduction", icon='TRIA_DOWN' if self.exp_postproduction else 'TRIA_RIGHT', icon_only=True, emboss=False)
        post_row.prop(self, "create_postproduction", text="Post-production")
        if self.exp_postproduction:
            post_children_col = box_post.column(align=True)
            
            # Renders
            renders_row = post_children_col.row(align=True)
            renders_row.label(icon='LAYER_ACTIVE')
            renders_row.prop(self, "create_renders", text="Renders")
            
            # Editing
            editing_row = post_children_col.row(align=True)
            editing_row.label(icon='LAYER_ACTIVE')
            editing_row.prop(self, "create_editing", text="Editing")
            
            # Sound
            sound_box = post_children_col.box()
            sound_row = sound_box.row(align=True)
            sound_row.prop(self, "exp_sound", icon='TRIA_DOWN' if self.exp_sound else 'TRIA_RIGHT', icon_only=True, emboss=False)
            sound_row.prop(self, "create_sound", text="Sound")
            if self.exp_sound:
                sound_children_col = sound_box.column(align=True)
                sound_children_col.prop(self, "create_sound_voices")
                sound_children_col.prop(self, "create_sound_music")
                sound_children_col.prop(self, "create_sound_effects")
            
            # Composite
            composite_row = post_children_col.row(align=True)
            composite_row.label(icon='LAYER_ACTIVE')
            composite_row.prop(self, "create_composite", text="Composite")
            
            # Exports
            exports_box = post_children_col.box()
            exports_row = exports_box.row(align=True)
            exports_row.prop(self, "exp_exports", icon='TRIA_DOWN' if self.exp_exports else 'TRIA_RIGHT', icon_only=True, emboss=False)
            exports_row.prop(self, "create_exports", text="Exports")
            if self.exp_exports:
                exports_children_col = exports_box.column(align=True)
                exports_children_col.prop(self, "create_exports_previews")
                exports_children_col.prop(self, "create_exports_final_versions")


# --- Operator for Textures to Current Directory ---
class BPM_OT_TexturesToCurrentDirectory(bpy.types.Operator):
    bl_label = "Textures to Current Directory"
    bl_idname = "bpm.textures_to_current_directory"
    bl_description = "Copia todas las texturas a una carpeta 'textures' en el directorio actual del archivo .blend y guarda si se activa."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.bpm_props

        if not bpy.data.filepath:
            self.report({'ERROR'}, "El archivo .blend no está guardado. Por favor, guarde el archivo antes de gestionar texturas externas.")
            return {'CANCELLED'}

        try:
            bpy.ops.file.pack_all()
            self.report({'INFO'}, "Recursos empaquetados en el archivo .blend.")
        except Exception as e:
            self.report({'ERROR'}, f"Error al empaquetar recursos: {e}")
            return {'CANCELLED'}

        try:
            bpy.ops.file.unpack_all(method='USE_LOCAL') 
            self.report({'INFO'}, "Texturas desempaquetadas en el directorio 'textures' del archivo .blend.")
        except Exception as e:
            self.report({'ERROR'}, f"Error al desempaquetar texturas: {e}")
            return {'CANCELLED'}

        if props.save_file:
            try:
                bpy.ops.wm.save_mainfile()
                self.report({'INFO'}, "Archivo .blend guardado con éxito.")
            except Exception as e:
                self.report({'ERROR'}, f"Error al guardar el archivo: {e}")
                return {'CANCELLED'}

        self.report({'INFO'}, "Operación de gestión de texturas completada.")
        return {'FINISHED'}


# --- Operator to Save Temp Files in Project Tree ---
class BPM_OT_SaveTempInProjectTree(bpy.types.Operator):
    bl_label = "Save Temp in Project Tree"
    bl_idname = "bpm.save_temp_in_project_tree"
    bl_description = "Cambia la ubicación de los archivos temporales de Blender a una carpeta 'Temp' dentro de la estructura del proyecto."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.bpm_props

        if not props.project_root_path or not os.path.isdir(props.project_root_path):
            self.report({'ERROR'}, "Por favor, define primero la Carpeta Raíz del Proyecto (Project Root Folder).")
            return {'CANCELLED'}

        production_folder_name = "Production"
        libraries_folder_name = "Libraries"
        temp_folder_name = "Temp"

        found_production_path = None
        for item in os.listdir(props.project_root_path):
            full_item_path = os.path.join(props.project_root_path, item)
            if os.path.isdir(full_item_path):
                if item == production_folder_name or (item.endswith(f"_{production_folder_name}") and item[:-len(production_folder_name)-1].isdigit()):
                    found_production_path = full_item_path
                    break
        
        if found_production_path:
            target_libraries_path = os.path.join(found_production_path, libraries_folder_name)
        else: 
            target_libraries_path = os.path.join(props.project_root_path, production_folder_name, libraries_folder_name)


        target_temp_path = os.path.join(target_libraries_path, temp_folder_name)

        try:
            os.makedirs(target_temp_path, exist_ok=True)
            self.report({'INFO'}, f"Carpeta temporal asegurada en: {target_temp_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Error al crear o verificar la carpeta temporal: {e}")
            return {'CANCELLED'}
        
        bpy.context.preferences.filepaths.temporary_directory = target_temp_path
        
        self.report({'INFO'}, f"La ubicación de los archivos temporales de Blender ha sido cambiada a: '{target_temp_path}'")
        return {'FINISHED'}


# --- OPERATOR TO SELECT PROJECT ROOT PATH ---
class BPM_OT_SelectProjectRootPath(bpy.types.Operator):
    bl_label = "Select Project Root Folder"
    bl_idname = "bpm.select_project_root_path"
    bl_description = "Abre el explorador de archivos para seleccionar la carpeta raíz del proyecto."
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(
        name="Path",
        subtype='DIR_PATH',
    )

    def execute(self, context):
        context.scene.bpm_props.project_root_path = self.filepath
        self.report({'INFO'}, f"Carpeta Raíz del Proyecto establecida a: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = context.scene.bpm_props.project_root_path 
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# --- Operator to Report Linked Asset Status ---
class BPM_OT_ReportLinkedAssetStatus(bpy.types.Operator):
    bl_label = "Report Status"
    bl_idname = "bpm.report_linked_asset_status"
    bl_description = "Verifica el estado del asset linkeado: si el enlace está roto o si está fuera del árbol del proyecto."
    bl_options = {'REGISTER', 'UNDO'}

    library_name: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.bpm_props
        lib = bpy.data.libraries.get(self.library_name)

        if not lib:
            self.report({'ERROR'}, f"Error: La librería '{self.library_name}' no se encontró.")
            return {'CANCELLED'}

        if not props.project_root_path or not os.path.isdir(props.project_root_path):
            self.report({'ERROR'}, "Por favor, define primero la Carpeta Raíz del Proyecto (Project Root Folder).")
            return {'CANCELLED'}
        
        abs_project_root_path = os.path.abspath(props.project_root_path)

        lib_filepath = bpy.path.abspath(lib.filepath)
        if not os.path.exists(lib_filepath):
            self.report({'WARNING'}, f"'{lib.name}' link is broken (file not found).")
            return {'FINISHED'}

        if not is_path_in_project_tree(lib_filepath, abs_project_root_path):
            self.report({'WARNING'}, f"'{lib.name}' is an outsider (outside project tree).")
            return {'FINISHED'}
        
        self.report({'INFO'}, f"'{lib.name}' is OK.")
        return {'FINISHED'}

# --- Operator to Link a Blender File (VERSIÓN CORREGIDA) ---
# Esta versión invoca directamente el operador nativo de Blender,
# solucionando el error "nothing indicated".
class BPM_OT_LinkBlenderFile(bpy.types.Operator):
    bl_label = "Link Blender File"
    bl_idname = "bpm.link_blender_file"
    bl_description = "Abre el explorador de archivos nativo de Blender para linkear data-blocks desde otro archivo .blend."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # En lugar de manejar la selección de archivos nosotros mismos,
        # le decimos a Blender que ejecute su propio operador 'link'.
        # 'INVOKE_DEFAULT' le dice a Blender que abra la ventana del operador
        # como si el usuario hubiera hecho clic en el menú File > Link...
        bpy.ops.wm.link('INVOKE_DEFAULT')
        return {'FINISHED'}

    # Ya no necesitamos el método invoke(), ni las propiedades filepath o filter_glob,
    # porque el operador nativo de Blender se encarga de todo.
###

# ------------------------------------------------------------------
#  MAKE OVERRIDE  – convierte la selección linkeada en override local
# ------------------------------------------------------------------
class BPM_OT_MakeOverride(bpy.types.Operator):
    bl_idname = "bpm.make_override"
    bl_label = "Make Override"
    bl_description = "Convierte los objetos linkeados seleccionados en overrides locales"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.object.make_override_library()
            self.report({'INFO'}, "Override aplicado.")
        except Exception as e:
            self.report({'ERROR'}, f"Error al hacer override: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}


###
# --- Panel for 3D Viewport N-Panel (BPM Tab) ---
class BPM_PT_ExternalDataManagement(bpy.types.Panel):
    bl_label = "Blender Project Management"
    bl_idname = "BPM_PT_ExternalDataManagement"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BPM"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bpm_props = scene.bpm_props

        # --- Project Root Folder Section ---
        box = layout.box()
        box.label(text="Project Setup", icon='FILE_FOLDER')
        
        row = box.row(align=True)
        row.prop(bpm_props, "project_root_path", text="", emboss=False) 
        row.operator(BPM_OT_SelectProjectRootPath.bl_idname, text="", icon='FILE_FOLDER')

        # --- External Assets Section ---
        box = layout.box()
        box.label(text="Manage External Assets", icon='FILE_IMAGE')

        row = box.row(align=True)
        row.prop(bpm_props, "save_file", text="Save file") 
        row.operator(BPM_OT_TexturesToCurrentDirectory.bl_idname, text="Textures to Current Directory") 

        # --- Temporary Files Section ---
        box = layout.box()
        box.label(text="Temporary Files", icon='FILE_HIDDEN')
        
        col = box.column(align=True)
        col.operator(BPM_OT_SaveTempInProjectTree.bl_idname, text="Save Temp in Project Tree") 

# --- Linked Management Panel (VERSIÓN CORREGIDA Y MEJORADA) ---
class BPM_PT_LinkedManagement(bpy.types.Panel):
    bl_label = "Linked Management"
    bl_idname = "BPM_PT_LinkedManagement"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BPM"

    def draw(self, context):
        layout = self.layout
        
        # Caja para mostrar las librerías ya linkeadas
        box_list = layout.box()
        box_list.label(text='Linked Libraries', icon='LINKED') 
        
        if not bpy.data.libraries:
            box_list.label(text="No linked libraries found.", icon='INFO')
        else:
            col = box_list.column(align=True)
            for lib in bpy.data.libraries:
                row = col.row(align=True)
                
                # Determinar el icono basado en el estado del asset
                icon = 'LINKED' # Icono por defecto (OK)
                lib_filepath = bpy.path.abspath(lib.filepath)
                
                if not os.path.exists(lib_filepath):
                    icon = 'ERROR' # Enlace roto
                elif not is_path_in_project_tree(lib_filepath, context.scene.bpm_props.project_root_path):
                    icon = 'QUESTION' # Asset externo
                
                row.label(text=lib.name, icon=icon)
                
                # Botón de "Report"
                report_op = row.operator(BPM_OT_ReportLinkedAssetStatus.bl_idname, text="Report")
                report_op.library_name = lib.name

        # --- NUEVA CAJA DE ACCIONES ---
        # Esta es la nueva caja que he añadido para el botón de Link y futuras acciones.
        box_actions = layout.box()
        box_actions.label(text="Actions", icon='PLUS')

        col_actions = box_actions.column(align=True)
        # Aquí se añade el botón que ejecuta el operador para linkear archivos .blend
        col_actions.operator(
            BPM_OT_LinkBlenderFile.bl_idname, 
            text="Link a .blend File", 
            icon='LINK_BLEND'
        )
        
        col_actions.operator(
            "bpm.make_override",
            text="Make Override",
            icon='IMPORT'            
            
        )

# --- Menu Item in "File" Menu ---
class TOPBAR_MT_FileProjectManagementMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_FileProjectManagementMenu"
    bl_label = "Project Management"

    def draw(self, context):
        layout = self.layout
        layout.operator(PM_OT_OpenFileBrowser.bl_idname, text="Open Project Browser", icon='FILE_FOLDER')

def add_file_menu_item(self, context):
    self.layout.menu(TOPBAR_MT_FileProjectManagementMenu.bl_idname)
    
##############

class BPM_OT_LoadBlendSafeMode(bpy.types.Operator):
    bl_idname = "bpm.load_blend_safe_mode"
    bl_label = "Load .blend in Safe Mode"
    bl_description = ("Abre un .blend con la UI deshabilitada y Simplify al mínimo; "
                      "ideal para archivos que crashean al abrirse.")
    bl_options = {'REGISTER'}

    _handler_installed = False

    @classmethod
    def _apply_simplify(cls, dummy):
        scene = bpy.context.scene
        scene.render.use_simplify = True
        scene.render.simplify_subdivision = 0
        scene.render.simplify_child_particles = 0
        bpy.app.handlers.load_post.remove(cls._apply_simplify)
        cls._handler_installed = False

    def execute(self, context):
        context.preferences.filepaths.use_load_ui = False
        if not self.__class__._handler_installed:
            bpy.app.handlers.load_post.append(self.__class__._apply_simplify)
            self.__class__._handler_installed = True
        bpy.ops.wm.open_mainfile('INVOKE_DEFAULT')
        self.report({'INFO'}, "Modo seguro: selecciona el archivo a cargar.")
        return {'FINISHED'}


class BPM_OT_DisableSafeMode(bpy.types.Operator):
    bl_idname = "bpm.disable_safe_mode"
    bl_label = "Disable Safe Mode"
    bl_description = "Restaura Load UI y desactiva Simplify."
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.preferences.filepaths.use_load_ui = True
        bpy.ops.wm.save_userpref()
        if context.scene.render.use_simplify:
            context.scene.render.use_simplify = False
        self.report({'INFO'}, "Modo seguro desactivado.")
        return {'FINISHED'}


class BPM_PT_RecoveryTools(bpy.types.Panel):
    bl_label = "Recover"
    bl_idname = "BPM_PT_RecoveryTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BPM"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Safe Mode", icon='RECOVER_LAST')
        col = box.column(align=True)
        col.operator("bpm.load_blend_safe_mode", text="Load .blend in Safe Mode", icon='ERROR')
        col.operator("bpm.disable_safe_mode", text="Disable Safe Mode", icon='CHECKMARK')

#############

# --- Register and Unregister Functions ---
classes = [
    BPM_Props,
    PM_OT_OpenFileBrowser,
    BPM_OT_TexturesToCurrentDirectory,
    BPM_OT_SaveTempInProjectTree,
    BPM_OT_SelectProjectRootPath,
    BPM_OT_ReportLinkedAssetStatus,
    BPM_OT_LinkBlenderFile,
    BPM_OT_MakeOverride,              #  ← ya lo tenías
    BPM_OT_LoadBlendSafeMode,         #  ← operador nuevo
    BPM_OT_DisableSafeMode,           #  ← operador nuevo
    BPM_PT_ExternalDataManagement,
    BPM_PT_LinkedManagement,
    BPM_PT_RecoveryTools,             #  ← panel nuevo
    TOPBAR_MT_FileProjectManagementMenu,

]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bpm_props = bpy.props.PointerProperty(type=BPM_Props)
    bpy.types.TOPBAR_MT_file.append(add_file_menu_item)


def unregister():
    bpy.types.TOPBAR_MT_file.remove(add_file_menu_item)
    del bpy.types.Scene.bpm_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()