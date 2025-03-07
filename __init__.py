bl_info = {
    "name": "Self-Updating Addon",
    "author": "Your Name",
    "version": (0, 8, 6),
    "blender": (3, 0, 0),
    "description": "Addon that updates itself via the internet.",
    "location": "View3D > Sidebar",
    "category": "Development",
}

import bpy
import urllib.request
import os
import time

REMOTE_VERSION_URL = "https://raw.githubusercontent.com/ItsALiving/Test/main/version.txt"
REMOTE_ADDON_URL = "https://raw.githubusercontent.com/ItsALiving/Test/main/__init__.py"

def get_current_version():
    return bpy.context.preferences.addons[__name__].bl_info.get('version', (0, 0, 0))

def get_remote_version():
    try:
        url = f"{REMOTE_VERSION_URL}?t={int(time.time())}"  # prevent caching
        with urllib.request.urlopen(url) as response:
            version = response.read().decode('utf-8').strip()
            return tuple(map(int, version.split('.')))
    except Exception as e:
        print("Version check failed:", e)
    return None

def check_for_update():
    current_version = get_current_version()
    remote_version = get_remote_version()
    if remote_version and remote_version > current_version:
        return True, remote_version
    return False, current_version

def get_current_version():
    return bl_info.get('version', (0, 0, 0))

def perform_update():
    try:
        url = f"{REMOTE_ADDON_URL}?t={int(time.time())}"  # prevent caching
        with urllib.request.urlopen(url) as response:
            addon_script = response.read()

        addon_folder = os.path.dirname(os.path.abspath(__file__))
        init_file = os.path.join(addon_folder, "__init__.py")

        with open(init_file, 'wb') as file:
            file.write(addon_script)
        return True

    except Exception as e:
        print("Addon update failed:", e)
    return False

REMOTE_ADDON_URL = "https://example.com/my_addon/__init__.py"

class MYADDON_OT_Self_Update(bpy.types.Operator):
    bl_idname = "myaddon.self_update"
    bl_label = "Check and Update Addon"

    def execute(self, context):
        has_update, new_version = check_for_update()
        if has_update:
            if perform_update():
                self.report({'INFO'}, f"Addon updated to version {new_version}. Restart Blender.")
            else:
                self.report({'ERROR'}, "Update failed.")
        else:
            self.report({'INFO'}, "Addon already up to date.")
        return {'FINISHED'}

class MYADDON_PT_Panel(bpy.types.Panel):
    bl_label = "Self-Updater"
    bl_idname = "MYADDON_PT_self_updater"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Updater"

    def draw(self, context):
        layout = self.layout
        layout.operator("myaddon.self_update", icon="FILE_REFRESH")

class MYADDON_OT_SelfUpdate(bpy.types.Operator):
    bl_idname = "myaddon.self_update"
    bl_label = "Update Addon"
    bl_description = "Check online and update addon"

    def execute(self, context):
        has_update, new_version = check_for_update()
        if has_update:
            if perform_update():
                self.report({'INFO'}, f"Addon updated to version {new_version}. Restart Blender.")
            else:
                self.report({'ERROR'}, "Update failed.")
        else:
            self.report({'INFO'}, "Addon already up to date.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_OT_SelfUpdate)
    bpy.utils.register_class(MYADDON_OT_SelfUpdate)

classes = [MYADDON_OT_Self_Update, MYADDON_PT_Panel]

def register():
    bpy.utils.register_class(MYADDON_OT_Self_Update)
    bpy.utils.register_class(MYADDON_PT_Panel)

def unregister():
    bpy.utils.unregister_class(MYADDON_OT_Self_Update)
    bpy.utils.unregister_class(MYADDON_PT_Panel)

if __name__ == "__main__":
    register()
