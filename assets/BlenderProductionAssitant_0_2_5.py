bl_info = {
    "name": "Blender Production Assistant",
    "author": "infamedavid",
    "version": (0, 2, 5),  
    "blender": (4, 0, 0),
    "location": "3D Viewport > N-Panel > BPM Tab",
    "description": "Tools for artists: textures, overrides, temp files, linked assets, safe mode and CSV reports.",
    "category": "Production",
}

import bpy
import os
import csv
import re

# ------------------------------------------------------------------
#  HELPERS
# ------------------------------------------------------------------
def is_path_in_project_tree(filepath, project_root_path):
    if not project_root_path:
        return False
    abs_filepath = os.path.abspath(bpy.path.abspath(filepath))
    abs_root_path = os.path.abspath(project_root_path)
    if not abs_root_path.endswith(os.sep):
        abs_root_path += os.sep
    return abs_filepath.startswith(abs_root_path)


def parse_blend_filename(filepath):
    """Devuelve name, branch, last_update según la convención <branch>_<name>[_###].blend"""
    base = os.path.basename(filepath)
    if not base.lower().endswith(".blend"):
        return "UNKNOWN", "00", "main"
    stem = base[:-6]  # quitar .blend
    m = re.match(r"^(?:(\d{2})_)?(.+?)(?:_([0-9]{3}))?$", stem)
    if not m:
        return stem, "00", "main"
    branch = m.group(1) or "00"
    name   = m.group(2)
    last   = m.group(3) or "main"
    return name, branch, last


def ensure_csv(path, header):
    """Crea el CSV con cabecera si no existe."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header)


# ------------------------------------------------------------------
#  PROPERTY GROUPS
# ------------------------------------------------------------------
class BPM_Props(bpy.types.PropertyGroup):
    save_file: bpy.props.BoolProperty(
        name="Save file",
        description="Save the .blend file after unpacking textures",
        default=True
    )
    project_root_path: bpy.props.StringProperty(
        name="Project Root Folder",
        description="Root folder of the current project",
    )
    # PROPIEDAD: para el número de backup a abrir, con límites fijos de 1 a 10.
    backup_number: bpy.props.IntProperty(
        name="Backup Number",
        description="Backup file number to open (.blend1, .blend2, etc.)",
        default=1,
        min=1,
        max=10 # <==edit this to increade
    )


class BPM_AssetStatusProps(bpy.types.PropertyGroup):
    type_text: bpy.props.StringProperty(name="Type",    description="Ej.: Character, Prop, Scene, FX")
    process_text: bpy.props.StringProperty(name="Process", description="Stage: Modeling, Rig, Layout…")
    state: bpy.props.EnumProperty(
        name="State",
        items=[('NYS', "NYS", "Not Yet Started"),
               ('WIP', "WIP", "Work In Progress"),
               ('FNL', "FNL", "Final")],
        default='NYS'
    )
    assigned_to: bpy.props.StringProperty(name="Assigned To", description="Your Name / nick")
    note: bpy.props.StringProperty(name="Note", description="Coments (Optional)")


# ------------------------------------------------------------------
#  OPERADORES — TEXTURAS / TEMPORALES  (sin cambios)
# ------------------------------------------------------------------
class BPM_OT_TexturesToCurrentDirectory(bpy.types.Operator):
    bl_label = "Textures to Current Directory"
    bl_idname = "bpm.textures_to_current_directory"
    bl_description = "Copies textures to 'textures' folder and saves if enabled."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.bpm_props
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save File First."); return {'CANCELLED'}
        try:
            bpy.ops.file.pack_all(); bpy.ops.file.unpack_all(method='USE_LOCAL')
            if props.save_file: bpy.ops.wm.save_mainfile()
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}"); return {'CANCELLED'}
        self.report({'INFO'}, "Done"); return {'FINISHED'}


class BPM_OT_SaveTempInProjectTree(bpy.types.Operator):
    bl_label = "Save Temp in Project Tree"
    bl_idname = "bpm.save_temp_in_project_tree"
    bl_description = "Sends temp files to Production/Libraries/Temp"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.bpm_props
        if not props.project_root_path or not os.path.isdir(props.project_root_path):
            self.report({'ERROR'}, "Define Project Root Firts."); return {'CANCELLED'}
        production, libraries, temp = "Production", "Libraries", "Temp"
        found = next((os.path.join(props.project_root_path, d) for d in os.listdir(props.project_root_path)
                      if os.path.isdir(os.path.join(props.project_root_path, d)) and
                      (d == production or d.endswith(f"_{production}") and d[:-len(production)-1].isdigit())), None)
        target_lib = os.path.join(found or os.path.join(props.project_root_path, production), libraries)
        temp_path  = os.path.join(target_lib, temp)
        try: os.makedirs(temp_path, exist_ok=True); bpy.context.preferences.filepaths.temporary_directory = temp_path
        except Exception as e: self.report({'ERROR'}, f"Error Temp: {e}"); return {'CANCELLED'}
        self.report({'INFO'}, f"Temp en {temp_path}"); return {'FINISHED'}


class BPM_OT_SelectProjectRootPath(bpy.types.Operator):
    bl_label = "Select Project Root Folder"; bl_idname = "bpm.select_project_root_path"; bl_options = {'REGISTER'}
    filepath: bpy.props.StringProperty(subtype='DIR_PATH')
    def execute(self, context):
        context.scene.bpm_props.project_root_path = self.filepath; self.report({'INFO'}, "Project Root OK"); return {'FINISHED'}
    def invoke(self, context, event):
        self.filepath = context.scene.bpm_props.project_root_path; context.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}


# ------------------------------------------------------------------
#  OPERADORES — LINK / OVERRIDE (sin cambios)
# ------------------------------------------------------------------
class BPM_OT_ReportLinkedAssetStatus(bpy.types.Operator):
    bl_label, bl_idname = "Report Status", "bpm.report_linked_asset_status"
    bl_description = "Verify status of linked."; bl_options = {'REGISTER', 'UNDO'}
    library_name: bpy.props.StringProperty()
    def execute(self, context):
        props = context.scene.bpm_props; lib = bpy.data.libraries.get(self.library_name)
        if not lib: self.report({'ERROR'}, "Not Found"); return {'CANCELLED'}
        if not props.project_root_path: self.report({'ERROR'}, "Define Project Root"); return {'CANCELLED'}
        path = bpy.path.abspath(lib.filepath)
        if not os.path.exists(path): icon='WARNING'; self.report({'WARNING'}, "Broken Link.")
        elif not is_path_in_project_tree(path, props.project_root_path): self.report({'WARNING'}, "Outsider")
        else: self.report({'INFO'}, "OK.")
        return {'FINISHED'}


class BPM_OT_LinkBlenderFile(bpy.types.Operator):
    bl_label, bl_idname = "Link Blender File", "bpm.link_blender_file"
    bl_description = "Link data-blocks from another .blend."; bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context): bpy.ops.wm.link('INVOKE_DEFAULT'); return {'FINISHED'}


class BPM_OT_MakeOverride(bpy.types.Operator):
    bl_label, bl_idname = "Make Override", "bpm.make_override"
    bl_description = "Make Overide."; bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        try: bpy.ops.object.make_override_library(); self.report({'INFO'}, "Override OK")
        except Exception as e: self.report({'ERROR'}, f"Error: {e}"); return {'CANCELLED'}
        return {'FINISHED'}


# ------------------------------------------------------------------
#  OPERADORES — MODO SEGURO (sin cambios)
# ------------------------------------------------------------------
class BPM_OT_LoadBlendSafeMode(bpy.types.Operator):
    bl_label, bl_idname = "Load .blend in Safe Mode", "bpm.load_blend_safe_mode"
    bl_description = "Load Broken Blend files"; bl_options = {'REGISTER'}
    _handler_installed = False
    @classmethod
    def _apply_simplify(cls, _):
        sc = bpy.context.scene; sc.render.use_simplify = True; sc.render.simplify_subdivision = 0; sc.render.simplify_child_particles = 0
        bpy.app.handlers.load_post.remove(cls._apply_simplify); cls._handler_installed = False
    def execute(self, context):
        context.preferences.filepaths.use_load_ui = False
        if not self.__class__._handler_installed:
            bpy.app.handlers.load_load_post.append(self.__class__._apply_simplify); self.__class__._handler_installed = True
        bpy.ops.wm.open_mainfile('INVOKE_DEFAULT'); return {'FINISHED'}


class BPM_OT_DisableSafeMode(bpy.types.Operator):
    bl_label, bl_idname = "Disable Safe Mode", "bpm.disable_safe_mode"
    bl_description = "Restaura Load UI y desactiva Simplify."; bl_options = {'REGISTER'}
    def execute(self, context):
        context.preferences.filepaths.use_load_ui = True; bpy.ops.wm.save_userpref()
        if context.scene.render.use_simplify: context.scene.render.use_simplify = False
        return {'FINISHED'}


# ------------------------------------------------------------------
#  OPERADOR — SAVE ASSET REPORT CSV  (sin cambios)
# ------------------------------------------------------------------
class BPM_OT_SaveAssetReport(bpy.types.Operator):
    bl_label = "Save Report"; bl_idname = "bpm.save_asset_report"
    bl_description = "Genera o actualiza el CSV de reporte para este asset."; bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save the Blend First"); return {'CANCELLED'}

        scene = context.scene; props = scene.bpm_asset
        filepath = bpy.data.filepath; folder = os.path.dirname(filepath)
        name, branch, last = parse_blend_filename(filepath)
        loc_rel = os.path.relpath(folder, scene.bpm_props.project_root_path) \
                  if scene.bpm_props.project_root_path else folder

        header = ["Name","Branch","Type","LastUpdate","Process","State","AssignedTo","Checked","Location","Note"]

        # NEW → nombre de archivo basado en rama + nombre base
        csv_name = f"{branch}_{name} report.csv" if branch != "00" else f"{name} report.csv"
        csv_path = os.path.join(folder, csv_name)
        ensure_csv(csv_path, header)

        row = [
            name,
            branch,
            props.type_text.strip()    or "NA",
            last,
            props.process_text.strip() or "NA",
            props.state,
            props.assigned_to.strip()  or "NA",
            "false",
            loc_rel.replace("\\", "/"),
            props.note.strip()         or "NA",
        ]

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        data = rows[1:]
        idx = next((i for i,r in enumerate(data) if r and r[0]==name and r[1]==branch), None)

        if idx is not None and data[idx] == row:
            self.report({'INFO'}, "No Changes"); return {'FINISHED'}

        if idx is not None:
            data[idx] = row
        else:
            data.append(row)

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(data)

        self.report({'INFO'}, f"Reporte guardado: {csv_name}")
        return {'FINISHED'}


# ------------------------------------------------------------------
#  NUEVO OPERADOR — OPEN BACKUP FILE (VALIDACIÓN DE RANGO EN OPERADOR)
# ------------------------------------------------------------------
class BPM_OT_OpenBackupFile(bpy.types.Operator):
    bl_label = "Open Backup"; bl_idname = "bpm.open_backup_file"
    bl_description = "Open a backup (.blend1, .blend2, etc.)"; bl_options = {'REGISTER'}

    def execute(self, context):
        current_filepath = bpy.data.filepath
        if not current_filepath:
            self.report({'ERROR'}, "Not Backup Found.")
            return {'CANCELLED'}

        props = context.scene.bpm_props
        backup_num = props.backup_number

        # **VALIDACIÓN CLAVE:** Límite fijo a 10
        if backup_num < 1 or backup_num > 10:
            self.report({'ERROR'}, f"El número de backup ({backup_num}) debe estar entre 1 y 10.")
            return {'CANCELLED'}

        dir_name = os.path.dirname(current_filepath)
        base_name = os.path.basename(current_filepath)
        
        file_stem, ext = os.path.splitext(base_name)
        if ext.lower() != ".blend":
            self.report({'ERROR'}, "El archivo actual no es un archivo .blend válido.")
            return {'CANCELLED'}

        backup_filename = f"{file_stem}.blend{backup_num}"
        backup_filepath = os.path.join(dir_name, backup_filename)

        if not os.path.exists(backup_filepath):
            self.report({'ERROR'}, f"Backup '{backup_filename}' no encontrado. Intenta con un número menor o verifica la carpeta.")
            return {'CANCELLED'}

        try:
            bpy.ops.wm.open_mainfile(filepath=backup_filepath)
            self.report({'INFO'}, f"Abriendo backup: '{backup_filename}'")
        except Exception as e:
            self.report({'ERROR'}, f"Error al abrir el backup: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


# ------------------------------------------------------------------
#  PANELES  (modificado para añadir el nuevo panel de backups)
# ------------------------------------------------------------------
class BPM_PT_ExternalDataManagement(bpy.types.Panel):
    bl_label = "Blender Production Assistant"; bl_idname = "BPM_PT_ExternalDataManagement"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "BPA"
    def draw(self, context):
        layout = self.layout; props = context.scene.bpm_props
        box = layout.box(); box.label(text="Project Setup", icon='FILE_FOLDER')
        row = box.row(); row.prop(props, "project_root_path", text="", emboss=False)
        row.operator("bpm.select_project_root_path", text="", icon='FILE_FOLDER')
        box = layout.box(); box.label(text="External Assets", icon='FILE_IMAGE')
        row = box.row(); row.prop(props, "save_file", text="Save")
        row.operator("bpm.textures_to_current_directory", text="To /textures")
        


class BPM_PT_LinkedManagement(bpy.types.Panel):
    bl_label = "Linked Management"; bl_idname = "BPM_PT_LinkedManagement"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "BPA"
    def draw(self, context):
        layout = self.layout; props = context.scene.bpm_props
        box = layout.box(); box.label(text="Linked Libraries", icon='LINKED')
        if not bpy.data.libraries:
            box.label(text="No linked libraries", icon='INFO')
        else:
            for lib in bpy.data.libraries:
                row = box.row(align=True); icon='LINKED'
                path = bpy.path.abspath(lib.filepath)
                if not os.path.exists(path): icon='ERROR'
                elif not is_path_in_project_tree(path, props.project_root_path): icon='QUESTION'
                row.label(text=lib.name, icon=icon)
                row.operator("bpm.report_linked_asset_status", text="Report").library_name = lib.name
        box = layout.box(); box.label(text="Actions", icon='PLUS')
        box.operator("bpm.link_blender_file", icon='LINK_BLEND')
        box.operator("bpm.make_override", icon='IMPORT')


class BPM_PT_RecoveryTools(bpy.types.Panel):
    bl_label = "Recover"; bl_idname = "BPM_PT_RecoveryTools"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "BPA"
    def draw(self, context):
        layout = self.layout
        box = layout.box(); box.label(text="Safe Mode", icon='RECOVER_LAST')
        col = box.column(align=True); col.operator("bpm.load_blend_safe_mode", icon='ERROR')
        col.separator()  # <- AIRE VISUAL
        col.operator("bpm.disable_safe_mode")

        # NUEVO BOX para Backups
        box = layout.box(); box.label(text="Backup", icon='FILE_BACKUP')
        col = box.column(align=True)
        
        props = context.scene.bpm_props # Obtener las propiedades
        
        # Dibujar la propiedad con los límites definidos en la propiedad misma
        row = col.row(align=True)
        row.label(text="Open blend [")
        row.prop(props, "backup_number", text="", expand=True, toggle=True) # Los límites vienen de BPM_Props.backup_number
        row.label(text="]")
        
        col.separator() 

        col.operator("bpm.open_backup_file")
        
        box = layout.box(); box.label(text="Temp Files", icon='FILE_HIDDEN')
        box.operator("bpm.save_temp_in_project_tree")
        
       

class BPM_PT_AssetStatus(bpy.types.Panel):
    bl_label, bl_idname = "Asset Status", "BPM_PT_AssetStatus"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "BPA"
    def draw(self, context):
        layout = self.layout
        if not bpy.data.filepath:
            layout.label(text="Save the .blend", icon='ERROR'); return
        name, branch, last = parse_blend_filename(bpy.data.filepath); props = context.scene.bpm_asset
        col = layout.column(align=True)
        col.label(text=f"Name: {name}"); col.label(text=f"Branch: {branch}"); col.label(text=f"LastUpdate: {last}")
        col.prop(props, "type_text"); col.prop(props, "process_text"); col.prop(props, "state")
        col.prop(props, "assigned_to"); col.prop(props, "note")
        col.separator() 
        col.operator("bpm.save_asset_report", icon='FILE_TICK')


# ------------------------------------------------------------------
#  REGISTRO (modificado para incluir el nuevo operador)
# ------------------------------------------------------------------
classes = [
    BPM_Props, BPM_AssetStatusProps,
    BPM_OT_TexturesToCurrentDirectory, BPM_OT_SaveTempInProjectTree, BPM_OT_SelectProjectRootPath,
    BPM_OT_ReportLinkedAssetStatus, BPM_OT_LinkBlenderFile, BPM_OT_MakeOverride,
    BPM_OT_LoadBlendSafeMode, BPM_OT_DisableSafeMode,
    BPM_OT_SaveAssetReport,
    BPM_OT_OpenBackupFile, # NUEVO OPERADOR
    BPM_PT_ExternalDataManagement, BPM_PT_LinkedManagement, BPM_PT_RecoveryTools, BPM_PT_AssetStatus,
]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.bpm_props = bpy.props.PointerProperty(type=BPM_Props)
    bpy.types.Scene.bpm_asset = bpy.props.PointerProperty(type=BPM_AssetStatusProps)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.bpm_props; del bpy.types.Scene.bpm_asset

if __name__ == "__main__":
    register()