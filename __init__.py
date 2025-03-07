bl_info = {
    "name": "Self-Updating Addon",
    "author": "Your Name",
    "version": (0, 8, 6),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar",
    "description": "Addon that updates itself via the internet.",
    "category": "Development",
}

import bpy
import urllib.request
import os
import time

REMOTE_VERSION_URL = "https://raw.githubusercontent.com/ItsALiving/Test/main/version.txt"
REMOTE_ADDON_URL = "https://raw.githubusercontent.com/ItsALiving/Test/main/__init__.py"

def get_current_version():
    return bl_info.get('version', (0, 0, 0))

def get_remote_version():
    try:
        url = f"{REMOTE_VERSION_URL}?t={int(time.time())}"
        with urllib.request.urlopen(url) as response:
            version = response.read().decode('utf-8').strip()
            return tuple(map(int, version.split('.')))
    except Exception as e:
        print("Failed to fetch remote version:", e)
        return None

def check_for_update():
    current_version = get_current_version()
    remote_version = get_remote_version()
    print(f"Current version: {current_version}, Remote version: {remote_version}")
    if remote_version and remote_version > current_version:
        return True, remote_version
    return False, current_version

def perform_update():
    try:
        url = f"{REMOTE_ADDON_URL}?t={int(time.time())}"
        with urllib.request.urlopen(url) as response:
            new_script = response.read()

        addon_folder = os.path.dirname(os.path.realpath(__file__))
        init_file = os.path.join(addon_folder, "__init__.py")

        # Ensure you have permissions and file is writable
        with open(init_file, 'wb') as f:
            f.write(new_script)

        print(f"Addon successfully updated at {init_file}")
        return True

    except Exception as e:
        print("Addon update failed due to:", e)
        return False


class ADDON_OT_self_update(bpy.types.Operator):
    bl_idname = "addon.self_update"
    bl_label = "Update Addon"
    bl_description = "Check online and update addon if newer version exists."

    def execute(self, context):
        has_update, remote_version = check_for_update()
        if has_update:
            if perform_update():
                self.report({'INFO'}, f"Addon updated to {remote_version}. Restart Blender.")
            else:
                self.report({'ERROR'}, "Addon update failed.")
        else:
            self.report({'INFO'}, "Addon already up to date.")
        return {'FINISHED'}

class ADDON_PT_Panel(bpy.types.Panel):
    bl_label = "Addon Updater"
    bl_idname = "ADDON_PT_updater_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Updater"

    def draw(self, context):
        layout = self.layout
        layout.operator("addon.self_update", icon='FILE_REFRESH')

classes = [ADDON_OT_self_update, ADDON_PT_Panel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
