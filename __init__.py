bl_info = {
    "name": "Self-Updating Addon",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar",
    "description": "Addon that updates itself via the internet.",
    "category": "Development",
}

import bpy
import urllib.request
import os

REMOTE_VERSION_URL = "https://github.com/ItsALiving/Test/blob/main/version.xtx"
REMOTE_ADDON_URL = "https://github.com/ItsALiving/Test/blob/main/__init__.py"

def get_current_version():
    return bl_info.get('version', (0, 0, 0))

def get_remote_version():
    try:
        with urllib.request.urlopen(REMOTE_VERSION_URL) as response:
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

def perform_update():
    try:
        with urllib.request.urlopen(REMOTE_ADDON_URL) as response:
            addon_content = response.read()

            addon_folder = os.path.dirname(os.path.abspath(__file__))
            init_file = os.path.join(addon_folder, "__init__.py")

            with open(init_file, 'wb') as f:
                f.write(addon_content)
            print("Addon updated successfully.")
            return True
    except Exception as e:
        print("Addon update failed:", e)
    return False

class SELFUPDATER_OT_Update(bpy.types.Operator):
    bl_idname = "selfupdater.update_addon"
    bl_label = "Update Addon"
    bl_description = "Checks for addon updates online"

    def execute(self, context):
        has_update, new_version = check_for_update()
        if has_update:
            if perform_update():
                self.report({'INFO'}, f"Addon updated to {new_version}. Restart Blender to apply.")
            else:
                self.report({'ERROR'}, "Update failed.")
        else:
            self.report({'INFO'}, "Addon already up to date.")
        return {'FINISHED'}

class SELFUPDATER_PT_Panel(bpy.types.Panel):
    bl_label = "Self-Updater"
    bl_idname = "SELFUPDATER_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Updater"

    def draw(self, context):
        layout = self.layout
        layout.operator("selfupdater.update_addon")

def register():
    bpy.utils.register_class(SELFUPDATER_OT_Update)
    bpy.utils.register_class(SELFUPDATER_PT_Panel)

def unregister():
    bpy.utils.unregister_class(SELFUPDATER_OT_Update)
    bpy.utils.unregister_class(SELFUPDATER_PT_Panel)

if __name__ == "__main__":
    register()
