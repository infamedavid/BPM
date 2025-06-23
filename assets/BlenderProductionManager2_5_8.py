bl_info = {
    "name"        : "Blender Production Manager — Tree Builder + Overseer",
    "author"      : "Infamedavid",
    "version"     : (2, 5, 8),
    "blender"     : (4, 0, 0),
    "location"    : "File ▸ Project Management & N-Panel ▸ BPM Tab",
    "description" : "Creates a production folder structure and provides an overseer dashboard for managing asset CSV reports.",
    "category"    : "System",
}

import bpy
import os
import csv

# ====================================================================================
#  HELPERS 
# ====================================================================================

def read_csv_report(path):
    if not os.path.exists(path): return []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"[BPM] Error reading {path}: {e}")
        return []

def truncate(text, n=15):
    t = str(text)
    return t if len(t) <= n else t[:n-1] + '…'

# ====================================================================================
#  PROPERTIES 
# ====================================================================================
class BPM_OverseerRow(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    branch: bpy.props.StringProperty()
    type: bpy.props.StringProperty()
    last_update: bpy.props.StringProperty()
    process: bpy.props.StringProperty()
    state: bpy.props.StringProperty()
    assigned_to: bpy.props.StringProperty()
    note: bpy.props.StringProperty(name="Note", description="Supervisor notes")
    checked: bpy.props.BoolProperty(name="Checked", description="Approved by supervisor")
    location: bpy.props.StringProperty()

class BPM_OverseerCSV(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty()
    last_read: bpy.props.IntProperty(default=0)
    rows: bpy.props.CollectionProperty(type=BPM_OverseerRow)

class BPM_OverseerSettings(bpy.types.PropertyGroup):
    csv_paths: bpy.props.CollectionProperty(type=BPM_OverseerCSV)

# ====================================================================================
#  OPERATOR  •  PLANT THE TREE 
# ====================================================================================
class PM_OT_OpenFileBrowser(bpy.types.Operator):
    bl_label       = "Plant the Tree"
    bl_idname      = "pm.open_file_browser"
    bl_description = "Opens the File Browser to select a directory and create the project."
    bl_options     = {'REGISTER'}

    MAX_PATH_LIMIT = 200

    project_name        : bpy.props.StringProperty(name="Project Name", default="New Project")
    numerate_folders    : bpy.props.BoolProperty  (name="Numerate folders", default=True)
    create_preproduction          : bpy.props.BoolProperty(name="Pre-production", default=True)
    exp_preproduction             : bpy.props.BoolProperty(default=False)
    create_script                 : bpy.props.BoolProperty(name="Script", default=True)
    create_concept_art            : bpy.props.BoolProperty(name="Concept Art", default=True)
    exp_concept_art               : bpy.props.BoolProperty(default=False)
    create_concept_art_characters : bpy.props.BoolProperty(name="Characters", default=True)
    create_concept_art_sets       : bpy.props.BoolProperty(name="Sets", default=True)
    create_concept_art_props      : bpy.props.BoolProperty(name="Props", default=True)
    create_storyboard             : bpy.props.BoolProperty(name="Storyboard", default=True)
    create_animatic               : bpy.props.BoolProperty(name="Animatic", default=True)
    create_reference              : bpy.props.BoolProperty(name="Reference", default=True)
    create_research               : bpy.props.BoolProperty(name="Research", default=True)
    create_production           : bpy.props.BoolProperty(name="Production", default=True)
    exp_production              : bpy.props.BoolProperty(default=False)
    create_assets               : bpy.props.BoolProperty(name="Assets", default=True)
    exp_assets                  : bpy.props.BoolProperty(default=False)
    create_models               : bpy.props.BoolProperty(name="Models", default=True)
    exp_models                  : bpy.props.BoolProperty(default=False)
    create_models_characters    : bpy.props.BoolProperty(name="Characters", default=True)
    create_models_scenarios     : bpy.props.BoolProperty(name="Scenarios", default=True)
    create_models_props         : bpy.props.BoolProperty(name="Props", default=True)
    create_scenes_layout        : bpy.props.BoolProperty(name="Scenes (Layout)", default=True)
    create_animation            : bpy.props.BoolProperty(name="Animation", default=True)
    exp_animation               : bpy.props.BoolProperty(default=False)
    create_animation_blocking   : bpy.props.BoolProperty(name="Blocking", default=True)
    create_animation_spline     : bpy.props.BoolProperty(name="Spline", default=True)
    create_animation_cleanup    : bpy.props.BoolProperty(name="Cleanup", default=True)
    create_libraries            : bpy.props.BoolProperty(name="Libraries", default=True)
    exp_libraries               : bpy.props.BoolProperty(default=False)
    create_textures_lib         : bpy.props.BoolProperty(name="Textures", default=True)
    exp_textures_lib            : bpy.props.BoolProperty(default=False)
    create_textures_lib_characters  : bpy.props.BoolProperty(name="Characters", default=True)
    create_textures_lib_props       : bpy.props.BoolProperty(name="Props", default=True)
    create_textures_lib_environments: bpy.props.BoolProperty(name="Environments", default=True)
    create_textures_lib_hdris       : bpy.props.BoolProperty(name="HDRIs", default=True)
    create_addons_lib           : bpy.props.BoolProperty(name="Addons", default=True)
    create_extras_lib           : bpy.props.BoolProperty(name="Extras", default=True)
    create_postproduction      : bpy.props.BoolProperty(name="Post-production", default=True)
    exp_postproduction         : bpy.props.BoolProperty(default=False)
    create_renders             : bpy.props.BoolProperty(name="Renders", default=True)
    create_editing             : bpy.props.BoolProperty(name="Editing", default=True)
    create_sound               : bpy.props.BoolProperty(name="Sound", default=True)
    exp_sound                  : bpy.props.BoolProperty(default=False)
    create_sound_voices        : bpy.props.BoolProperty(name="Voices", default=True)
    create_sound_music         : bpy.props.BoolProperty(name="Music", default=True)
    create_sound_effects       : bpy.props.BoolProperty(name="Effects", default=True)
    create_composite           : bpy.props.BoolProperty(name="Composite", default=True)
    create_exports             : bpy.props.BoolProperty(name="Exports", default=True)
    exp_exports                : bpy.props.BoolProperty(default=False)
    create_exports_previews        : bpy.props.BoolProperty(name="Previews", default=True)
    create_exports_final_versions  : bpy.props.BoolProperty(name="Final Versions", default=True)

    directory: bpy.props.StringProperty(
        name="Selected Path",
        subtype='DIR_PATH',
        description="The folder where the new project will be created."
    )

    def execute(self, context):
        project_name = self.project_name.strip()
        base_dir     = self.directory

        if not project_name:
            self.report({'ERROR'}, "Project name cannot be empty.")
            return {'CANCELLED'}
        if not os.path.isdir(base_dir):
            self.report({'ERROR'}, f"Base directory '{base_dir}' is not valid.")
            return {'CANCELLED'}

        project_root_path = os.path.join(base_dir, project_name)
        if os.path.exists(project_root_path):
            self.report({'WARNING'}, f"'{project_name}' already exists in {base_dir}.")
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
                    "Models": (self.create_models, { "Characters": (self.create_models_characters, None), "Scenarios": (self.create_models_scenarios, None), "Props": (self.create_models_props, None), }),
                }),
                "Scenes (Layout)": (self.create_scenes_layout, None),
                "Animation": (self.create_animation, { "Blocking": (self.create_animation_blocking, None), "Spline": (self.create_animation_spline, None), "Cleanup": (self.create_animation_cleanup, None), }),
                "Libraries": (self.create_libraries, {
                    "Textures": (self.create_textures_lib, { "Characters": (self.create_textures_lib_characters, None), "Props": (self.create_textures_lib_props, None), "Environments": (self.create_textures_lib_environments, None), "HDRIs": (self.create_textures_lib_hdris, None), }),
                    "Addons": (self.create_addons_lib, None), "Extras": (self.create_extras_lib, None),
                }),
            }),
            "Post-production": (self.create_postproduction, {
                "Renders": (self.create_renders, None), "Editing": (self.create_editing, None),
                "Sound": (self.create_sound, { "Voices": (self.create_sound_voices, None), "Music": (self.create_sound_music, None), "Effects": (self.create_sound_effects, None), }),
                "Composite": (self.create_composite, None),
                "Exports": (self.create_exports, { "Previews": (self.create_exports_previews, None), "Final Versions": (self.create_exports_final_versions, None), }),
            }),
        }

        top_level_phases_order = ["Pre-production", "Production", "Post-production"]
        top_level_folders_info = []
        for base_name in top_level_phases_order:
            should_create, nested = project_structure_config.get(base_name, (False, None))
            if should_create:
                actual_name = f"{len(top_level_folders_info)+1:02d}_{base_name}" if self.numerate_folders else base_name
                top_level_folders_info.append((actual_name, nested))

        all_paths_to_create = []
        def _collect_paths(parent, struct):
            if not struct: return
            if parent.endswith("Production"): ordered = ["Assets", "Scenes (Layout)", "Animation", "Libraries"]
            elif parent.endswith("Post-production"): ordered = ["Renders", "Editing", "Sound", "Composite", "Exports"]
            else: ordered = None
            items = struct.items()
            if ordered: items = [(k, struct[k]) for k in ordered if k in struct] + sorted([(k, v) for k, v in struct.items() if k not in ordered])
            for folder, (flag, sub) in items:
                if flag:
                    full = os.path.join(parent, folder)
                    all_paths_to_create.append(full)
                    _collect_paths(full, sub)

        for top_name, nested in top_level_folders_info:
            root = os.path.join(project_root_path, top_name)
            all_paths_to_create.append(root)
            _collect_paths(root, nested)

        for path in all_paths_to_create:
            if len(path) > self.MAX_PATH_LIMIT:
                self.report({'ERROR'}, f"Path exceeds {self.MAX_PATH_LIMIT} characters:\n{path}")
                return {'CANCELLED'}

        try:
            for path in all_paths_to_create:
                os.makedirs(path, exist_ok=True)
            self.report({'INFO'}, "Structure created successfully.")
        except Exception as e:
            self.report({'ERROR'}, f"Error creating folders: {e}")
            return {'CANCELLED'}
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
        self._draw_section(layout, "Pre-production", "exp_preproduction", "create_preproduction", [
            ("create_script", "Script", None),
            ("create_concept_art", "Concept Art", [("create_concept_art_characters", "Characters"), ("create_concept_art_sets", "Sets"), ("create_concept_art_props", "Props")]),
            ("create_storyboard", "Storyboard", None), ("create_animatic", "Animatic", None), ("create_reference", "Reference", None), ("create_research", "Research", None),
        ])
        self._draw_section(layout, "Production", "exp_production", "create_production", [
            ("create_assets", "Assets", [("create_models", "Models", [("create_models_characters", "Characters"), ("create_models_scenarios", "Scenarios"), ("create_models_props", "Props")])]),
            ("create_scenes_layout", "Scenes (Layout)", None),
            ("create_animation", "Animation", [("create_animation_blocking", "Blocking"), ("create_animation_spline", "Spline"), ("create_animation_cleanup", "Cleanup")]),
            ("create_libraries", "Libraries", [
                ("create_textures_lib", "Textures", [("create_textures_lib_characters", "Characters"), ("create_textures_lib_props", "Props"), ("create_textures_lib_environments", "Environments"), ("create_textures_lib_hdris", "HDRIs")]),
                ("create_addons_lib", "Addons", None), ("create_extras_lib", "Extras", None),
            ]),
        ])
        self._draw_section(layout, "Post-production", "exp_postproduction", "create_postproduction", [
            ("create_renders", "Renders", None), ("create_editing", "Editing", None),
            ("create_sound", "Sound", [("create_sound_voices", "Voices"), ("create_sound_music", "Music"), ("create_sound_effects", "Effects")]),
            ("create_composite", "Composite", None),
            ("create_exports", "Exports", [("create_exports_previews", "Previews"), ("create_exports_final_versions", "Final Versions")]),
        ])

    def _draw_section(self, layout, label, exp_prop, create_prop, items):
        box = layout.box()
        row = box.row(align=True)
        row.prop(self, exp_prop, icon='TRIA_DOWN' if getattr(self, exp_prop) else 'TRIA_RIGHT', icon_only=True, emboss=False)
        row.prop(self, create_prop, text=label)
        if getattr(self, exp_prop):
            col = box.column(align=True)
            for prop_name, text, children in items:
                if children is None:
                    row_i = col.row(align=True)
                    row_i.label(icon='LAYER_ACTIVE')
                    row_i.prop(self, prop_name, text=text)
                else:
                    exp_name = f"exp_{prop_name[7:]}"
                    if not hasattr(self, exp_name): setattr(self.__class__, exp_name, bpy.props.BoolProperty(default=False))
                    sub_box = col.box()
                    sub_row = sub_box.row(align=True)
                    sub_row.prop(self, exp_name, icon='TRIA_DOWN' if getattr(self, exp_name) else 'TRIA_RIGHT', icon_only=True, emboss=False)
                    sub_row.prop(self, prop_name, text=text)
                    if getattr(self, exp_name):
                        sub_col = sub_box.column(align=True)
                        for child_prop, child_text in children: sub_col.prop(self, child_prop, text=child_text)

# ====================================================================================
#  OPERATORS 
# ====================================================================================
class BPM_OT_AddCSV(bpy.types.Operator):
    bl_idname = 'bpm.add_csv'; bl_label = 'Load CSV Reports'
    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    def execute(self,ctx):
        store = ctx.scene.bpm_overseer.csv_paths; existing={e.path for e in store}
        for f in self.files:
            p=os.path.join(self.directory, f.name)
            if p in existing: continue
            new = store.add(); new.path = p
            new.rows.clear()
            for rec in read_csv_report(p):
                row = new.rows.add()
                row.name = rec.get("Name", ""); row.branch = rec.get("Branch", ""); row.type = rec.get("Type", "")
                row.last_update = rec.get("LastUpdate", ""); row.process = rec.get("Process", ""); row.state = rec.get("State", "")
                row.assigned_to = rec.get("AssignedTo", ""); row.note = rec.get("Note", "")
                row.checked = rec.get("Checked", "false") == "true"; row.location = rec.get("Location", "")
        return {'FINISHED'}
    def invoke(self,ctx,evt): ctx.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}

class BPM_OT_RemoveCSV(bpy.types.Operator):
    bl_idname='bpm.remove_csv'; bl_label='Unload CSV'
    index:bpy.props.IntProperty()
    def execute(self,ctx):
        ctx.scene.bpm_overseer.csv_paths.remove(self.index); return {'FINISHED'}

class BPM_OT_ReloadCSV(bpy.types.Operator):
    bl_idname='bpm.reload_csv'; bl_label='Reload Report'
    index:bpy.props.IntProperty()
    def execute(self,ctx):
        csv_entry = ctx.scene.bpm_overseer.csv_paths[self.index]
        csv_entry.rows.clear()
        for rec in read_csv_report(csv_entry.path):
            row = csv_entry.rows.add()
            row.name = rec.get("Name", ""); row.branch = rec.get("Branch", ""); row.type = rec.get("Type", "")
            row.last_update = rec.get("LastUpdate", ""); row.process = rec.get("Process", ""); row.state = rec.get("State", "")
            row.assigned_to = rec.get("AssignedTo", ""); row.note = rec.get("Note", "")
            row.checked = rec.get("Checked", "false") == "true"; row.location = rec.get("Location", "")
        return {'FINISHED'}

class BPM_OT_ReloadAll(bpy.types.Operator):
    bl_idname='bpm.reload_all_csvs'; bl_label='Reload All'
    def execute(self,ctx):
        for i in range(len(ctx.scene.bpm_overseer.csv_paths)): bpy.ops.bpm.reload_csv(index=i)
        return {'FINISHED'}

class BPM_OT_ValidateAsset(bpy.types.Operator):
    bl_idname='bpm.validate_asset'; bl_label='Validate Row'
    csv_index: bpy.props.IntProperty()
    row_index: bpy.props.IntProperty()
    def execute(self, ctx):
        csvs = ctx.scene.bpm_overseer.csv_paths
        if self.csv_index >= len(csvs): return {'CANCELLED'}
        entry = csvs[self.csv_index]
        if self.row_index >= len(entry.rows): return {'CANCELLED'}
        target_row = entry.rows[self.row_index]
        filepath = entry.path
        if not filepath or not os.path.exists(filepath): return {'CANCELLED'}
        original_data = read_csv_report(filepath)
        if not original_data: return {'CANCELLED'}
        updated = False
        for i, data_row in enumerate(original_data):
            if data_row.get("Name") == target_row.name and data_row.get("Branch") == target_row.branch:
                original_data[i]["Note"] = target_row.note
                original_data[i]["Checked"] = "true" if target_row.checked else "false"
                updated = True; break
        if updated:
            try:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=original_data[0].keys())
                    writer.writeheader(); writer.writerows(original_data)
                self.report({'INFO'}, f'Row "{target_row.name}" validated and saved to CSV.')
            except Exception as e:
                self.report({'ERROR'}, str(e)); return {'CANCELLED'}
        else:
            self.report({'WARNING'}, 'Could not find the corresponding row in the CSV to update.')
        return {'FINISHED'}

class BPM_OT_ValidateAll(bpy.types.Operator):
    bl_idname='bpm.validate_all'; bl_label='Validate All Changes'
    def execute(self, ctx):
        csvs = ctx.scene.bpm_overseer.csv_paths
        for csv_idx, entry in enumerate(csvs):
            filepath = entry.path
            if not filepath or not os.path.exists(filepath): continue
            original_data = read_csv_report(filepath)
            if not original_data: continue
            data_map = {(d.get("Name"), d.get("Branch")): d for d in original_data}
            for row in entry.rows:
                key = (row.name, row.branch)
                if key in data_map:
                    data_map[key]["Note"] = row.note
                    data_map[key]["Checked"] = "true" if row.checked else "false"
            try:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=original_data[0].keys())
                    writer.writeheader(); writer.writerows(list(data_map.values()))
            except Exception as e:
                self.report({'ERROR'}, f"Error writing {os.path.basename(filepath)}: {e}")
        self.report({'INFO'}, 'All changes have been validated and saved to their respective CSVs.')
        return {'FINISHED'}

class BPM_OT_ExportCombined(bpy.types.Operator):
    bl_idname='bpm.export_combined_csv'; bl_label='Export Combined CSV'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH', default="")
    def execute(self,ctx):
        all_data=[]
        for e in ctx.scene.bpm_overseer.csv_paths:
            for r in e.rows:
                d = {
                    "Name":r.name,"Branch":r.branch,"Type":r.type,"LastUpdate":r.last_update,
                    "Process":r.process,"State":r.state,"AssignedTo":r.assigned_to,
                    "Checked":"true" if r.checked else "false","Location":r.location,"Note":r.note
                }
                all_data.append(d)
        if not all_data:
            self.report({'WARNING'}, 'No data to export.'); return {'CANCELLED'}
        try:
            with open(self.filepath,'w',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f,fieldnames=all_data[0].keys())
                writer.writeheader(); writer.writerows(all_data)
            self.report({'INFO'},f'Exported: {self.filepath}')
        except Exception as e:
            self.report({'ERROR'},str(e)); return {'CANCELLED'}
        return {'FINISHED'}
    def invoke(self,ctx,evt):
        self.filepath = ""
        ctx.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ====================================================================================
#  PANEL Overseer
# ====================================================================================
class BPM_PT_Overseer(bpy.types.Panel):
    bl_idname='BPM_PT_Overseer'; bl_label='Overseer Dashboard'
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='BPM'
    def draw(self,ctx):
        lay=self.layout; data=ctx.scene.bpm_overseer
        row=lay.row(align=True)
        row.operator('bpm.add_csv',icon='ADD')
        row.operator('bpm.reload_all_csvs',icon='FILE_REFRESH')
        row.operator('bpm.validate_all',icon='CHECKMARK')
        row.operator('bpm.export_combined_csv',icon='EXPORT')
        lay.separator()
        for csv_idx, e in enumerate(data.csv_paths):
            box = lay.box()
            row = box.row(align=True)
            row.label(text=os.path.basename(e.path), icon='FILE_TEXT')
            op_reload = row.operator('bpm.reload_csv',text='',icon='FILE_REFRESH')
            op_reload.index = csv_idx
            op_remove = row.operator('bpm.remove_csv',text='',icon='X')
            op_remove.index = csv_idx
            col = box.column(align=True)
            for row_idx, r in enumerate(e.rows):
                row = col.row(align=True)
                row.label(text=truncate(r.name))
                row.label(text=truncate(r.branch))
                row.label(text=truncate(r.type))
                row.label(text=truncate(r.last_update))
                row.label(text=truncate(r.process))
                row.label(text=truncate(r.state))
                row.label(text=truncate(r.assigned_to))
                row.prop(r,'checked',text="")
                row.prop(r,'note',text="")
                op_validate = row.operator('bpm.validate_asset',text='',icon='CHECKMARK')
                op_validate.csv_index = csv_idx
                op_validate.row_index = row_idx

# ====================================================================================
#  MENU File ▸ Project Management (from Tree Builder)
# ====================================================================================
class TOPBAR_MT_ProjectManagementMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_project_management_menu"; bl_label  = "Project Management"
    def draw(self, context):
        self.layout.operator(PM_OT_OpenFileBrowser.bl_idname, icon='FILE_FOLDER')

def _add_file_menu(self, context):
    self.layout.menu(TOPBAR_MT_ProjectManagementMenu.bl_idname)

# ====================================================================================
#  REGISTER 
# ====================================================================================
CLASSES = [
    BPM_OverseerRow, BPM_OverseerCSV, BPM_OverseerSettings, PM_OT_OpenFileBrowser,
    BPM_OT_AddCSV, BPM_OT_RemoveCSV, BPM_OT_ReloadCSV, BPM_OT_ReloadAll,
    BPM_OT_ValidateAsset, BPM_OT_ValidateAll, BPM_OT_ExportCombined, BPM_PT_Overseer,
    TOPBAR_MT_ProjectManagementMenu,
]

def register():
    for cls in CLASSES: bpy.utils.register_class(cls)
    bpy.types.Scene.bpm_overseer = bpy.props.PointerProperty(type=BPM_OverseerSettings)
    bpy.types.TOPBAR_MT_file.append(_add_file_menu)

def unregister():
    bpy.types.TOPBAR_MT_file.remove(_add_file_menu)
    del bpy.types.Scene.bpm_overseer
    for cls in reversed(CLASSES): bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()