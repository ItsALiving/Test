bl_info = {
    'name': 'Quick Gun Setup',
    'description': (
        "Creates an armature from selected meshes, assigns vertex groups, "
        "applies an armature modifier, auto-parents or removes parent for selected bones (in pose mode), "
        "joins selected objects, and can delete all changes added with the add-on."
    ),
    'author': 'ItsALiving',
    'version': (0, 8, 6),  # Local version tuple
    'blender': (4, 0, 0),
    'location': 'View3D > UI > Quick Gun Setup',
    'warning': '',
    "wiki_url": "",
    'tracker_url': '',
    'support': 'COMMUNITY',
    'category': 'User Interface',
    # Updater settings (used below)
    'github_repo': 'ItsALiving/Test',
    'github_raw_url': 'https://raw.githubusercontent.com/ItsALiving/Test/main/',
    'version_txt': 'version.txt'
}

import math
import bpy
import mathutils
import os
import urllib.request

# Global URLs for the updater
REMOTE_INIT_URL = "https://raw.githubusercontent.com/ItsALiving/Test/main/__init__.py"
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/ItsALiving/Test/main/version.txt"

# ------------------ Online Updater Operators ------------------

class CheckForUpdateOperator(bpy.types.Operator):
    """Check remote version and report if an update is available."""
    bl_idname = "addon.check_for_update"
    bl_label = "Check for Update"

    def execute(self, context):
        try:
            with urllib.request.urlopen(REMOTE_VERSION_URL) as response:
                remote_version_str = response.read().decode("utf-8").strip()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to fetch remote version: {e}")
            return {'CANCELLED'}

        try:
            # Assume version.txt is in the format: 0.8.7
            remote_version = tuple(map(int, remote_version_str.split(".")))
        except Exception as e:
            self.report({'ERROR'}, f"Invalid version format in remote version file: {e}")
            return {'CANCELLED'}

        local_version = bl_info.get("version", (0, 0, 0))
        if remote_version > local_version:
            self.report({'INFO'}, f"Update available: {remote_version_str} (Local: {'.'.join(map(str, local_version))})")
        else:
            self.report({'INFO'}, "No update available.")
        return {'FINISHED'}

class UpdateNowOperator(bpy.types.Operator):
    """Download the latest __init__.py and overwrite the current file."""
    bl_idname = "addon.update_now"
    bl_label = "Update Now"

    def execute(self, context):
        try:
            with urllib.request.urlopen(REMOTE_INIT_URL) as response:
                new_code = response.read().decode("utf-8")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to fetch update: {e}")
            return {'CANCELLED'}

        addon_file = __file__
        try:
            with open(addon_file, "w", encoding="utf-8") as f:
                f.write(new_code)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write update: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "Update applied. Please restart Blender for changes to take effect.")
        return {'FINISHED'}

# ------------------ Existing Functionality ------------------

def remove_existing_vertex_groups_modifiers_and_armature(keep_QGS_mesh=True):
    print("DEBUG: Starting remove_existing_vertex_groups_modifiers_and_armature()...")

    removed_vgroups = 0
    removed_modifiers = 0
    removed_QGS_meshes = 0
    removed_QGS_armature_objs = 0
    removed_armature_datas = 0

    all_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    for mesh in all_meshes:
        for group in list(mesh.vertex_groups):
            if group.name.startswith("QGS_"):
                try:
                    mesh.vertex_groups.remove(group)
                    removed_vgroups += 1
                    print(f"DEBUG: Removed QGS vertex group '{group.name}' from mesh '{mesh.name}'.")
                except ReferenceError:
                    pass
        for mod in list(mesh.modifiers):
            if mod.type == 'ARMATURE' and mod.name == "QGS_Armature":
                try:
                    mesh.modifiers.remove(mod)
                    removed_modifiers += 1
                    print(f"DEBUG: Removed QGS_Armature modifier from mesh '{mesh.name}'.")
                except ReferenceError:
                    pass

    QGS_armature_objects = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and obj.get("QGS", False)]
    for arm_obj in QGS_armature_objects:
        try:
            for scene in bpy.data.scenes:
                top_coll = scene.collection
                if arm_obj.name in top_coll.objects:
                    top_coll.objects.unlink(top_coll.objects[arm_obj.name])
            for coll in bpy.data.collections:
                if arm_obj.name in coll.objects:
                    coll.objects.unlink(coll.objects[arm_obj.name])
            if arm_obj.name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[arm_obj.name], do_unlink=True)
                removed_QGS_armature_objs += 1
                print(f"DEBUG: Removed QGS armature object '{arm_obj.name}'.")
        except ReferenceError:
            pass

    QGS_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.get("QGS", False)]
    if keep_QGS_mesh:
        for mesh_obj in QGS_meshes:
            if "QGS" in mesh_obj:
                del mesh_obj["QGS"]
                print(f"DEBUG: Removed QGS property from mesh '{mesh_obj.name}' (keeping the object).")
    else:
        for mesh_obj in QGS_meshes:
            try:
                bpy.data.objects.remove(mesh_obj, do_unlink=True)
                removed_QGS_meshes += 1
                print(f"DEBUG: Removed QGS mesh object '{mesh_obj.name}'.")
            except ReferenceError:
                pass

    for arm_data in list(bpy.data.armatures):
        if arm_data.name.startswith("QGS_"):
            try:
                if arm_data.users == 0:
                    bpy.data.armatures.remove(arm_data, do_unlink=True)
                    removed_armature_datas += 1
                    print(f"DEBUG: Removed QGS armature data block '{arm_data.name}'.")
            except ReferenceError:
                pass

    print("DEBUG: Finished removing QGS items. Totals:")
    print(f"       QGS Vertex Groups removed: {removed_vgroups}")
    print(f"       QGS Armature Modifiers removed: {removed_modifiers}")
    print(f"       QGS Armature Objects removed: {removed_QGS_armature_objs}")
    print(f"       QGS Armature Data blocks removed: {removed_armature_datas}")
    print(f"       QGS Mesh Objects removed: {removed_QGS_meshes} (only if keep_QGS_mesh=False)")

def count_QGS_changes():
    total_changes = 0
    for obj in bpy.data.objects:
        if obj.get("QGS", False):
            total_changes += 1
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for group in obj.vertex_groups:
                if group.name.startswith("QGS_"):
                    total_changes += 1
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE' and mod.name == "QGS_Armature":
                    total_changes += 1
    for arm_data in bpy.data.armatures:
        if arm_data.name.startswith("QGS_"):
            total_changes += 1
    return total_changes

def set_origin_to_center_of_mass():
    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not selected_objects:
        bpy.ops.object.dialog_message('INVOKE_DEFAULT', message="No object selected. Please select at least one object.")
        return {'CANCELLED'}

    bpy.context.view_layer.objects.active = selected_objects[0]
    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in selected_objects:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

    print("✅ Origins set to center of mass.")
    return {'FINISHED'}

def create_armature_and_bones(armature_name, bone_length=0.1):
    if not armature_name.startswith("QGS_"):
        armature_name = "QGS_" + armature_name

    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not selected_objects:
        bpy.ops.object.dialog_message('INVOKE_DEFAULT', message="No object selected. Please select at least one object.")
        return None

    armature = bpy.data.armatures.new(name=armature_name)
    armature_obj = bpy.data.objects.new(name=armature_name, object_data=armature)
    armature_obj["QGS"] = True

    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')

    for obj in selected_objects:
        bone_name = "QGS_" + obj.name
        bone = armature.edit_bones.new(bone_name)
        bone.head = obj.location
        bone.tail = obj.location + mathutils.Vector((0, 0, bone_length))
        bone.use_connect = False

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"✅ Armature '{armature_name}' created. Bone length = {bone_length}.")
    return armature_obj

def create_vertex_groups_from_selection():
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not selected_meshes:
        bpy.ops.object.dialog_message('INVOKE_DEFAULT', message="No object selected. Please select at least one object.")
        return {'CANCELLED'}

    for mesh in selected_meshes:
        bpy.context.view_layer.objects.active = mesh
        bpy.ops.object.mode_set(mode='OBJECT')
        group = mesh.vertex_groups.new(name="QGS_" + mesh.name)
        vertex_indices = [v.index for v in mesh.data.vertices]
        group.add(vertex_indices, 1.0, 'REPLACE')

    print("✅ Vertex groups created with prefix 'QGS_' matching bone names.")
    return {'FINISHED'}

def add_armature_modifier(armature_obj):
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not selected_meshes or armature_obj is None:
        return
    for mesh in selected_meshes:
        modifier = mesh.modifiers.new(name="QGS_Armature", type='ARMATURE')
        modifier.object = armature_obj
    print("✅ Armature modifiers added with name 'QGS_Armature' to selected meshes.")

class ArmatureAndVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "object.armature_and_vertex_groups"
    bl_label = "Create Armature & Vertex Groups"

    armature_name: bpy.props.StringProperty(
        name="Armature Name", 
        default="Armature"
    )

    bone_length: bpy.props.FloatProperty(
        name="Bone Length",
        description="Length of the bones to be created",
        default=0.1,
        min=0.0,
        max=100.0
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "armature_name")
        layout.prop(self, "bone_length")

    def execute(self, context):
        selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            self.report({'ERROR'}, "No object selected. Please select at least one object.")
            return {'CANCELLED'}

        remove_existing_vertex_groups_modifiers_and_armature()

        if set_origin_to_center_of_mass() == {'CANCELLED'}:
            return {'CANCELLED'}

        armature_obj = create_armature_and_bones(self.armature_name, self.bone_length)
        if armature_obj is None:
            return {'CANCELLED'}

        create_vertex_groups_from_selection()
        add_armature_modifier(armature_obj)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class AutoParentSelectedBonesOperator(bpy.types.Operator):
    bl_idname = "armature.auto_parent_selected_bones"
    bl_label = "Auto-Parent Selected Bones"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='EDIT')
        arm = obj.data
        selected_bones = [bone for bone in arm.edit_bones if bone.select]
        if len(selected_bones) < 2:
            self.report({'ERROR'}, "Select at least two bones.")
            bpy.ops.object.mode_set(mode='POSE')
            return {'CANCELLED'}
        active_bone = arm.edit_bones.active
        if not active_bone:
            self.report({'ERROR'}, "No active bone found. Please select an active bone.")
            bpy.ops.object.mode_set(mode='POSE')
            return {'CANCELLED'}
        for bone in selected_bones:
            if bone != active_bone:
                old_parent = bone.parent.name if bone.parent else ""
                bone["QGS_old_parent"] = old_parent
                bone.parent = active_bone
        bpy.ops.object.mode_set(mode='POSE')
        self.report({'INFO'}, f"Selected bones parented to '{active_bone.name}' (old parents stored).")
        return {'FINISHED'}

class RemoveParentSelectedBonesOperator(bpy.types.Operator):
    bl_idname = "armature.remove_parent_selected_bones"
    bl_label = "Remove Parent from Selected Bones"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='EDIT')
        arm = obj.data
        removed_count = 0
        for bone in arm.edit_bones:
            if bone.select and bone.parent:
                bone["QGS_removed_parent"] = bone.parent.name
                bone.parent = None
                removed_count += 1
        bpy.ops.object.mode_set(mode='POSE')
        if removed_count:
            self.report({'INFO'}, f"Removed parent from {removed_count} bone(s) (old parent stored).")
        else:
            self.report({'INFO'}, "No parents found to remove.")
        return {'FINISHED'}

class ReverseAutoParentChangeOperator(bpy.types.Operator):
    bl_idname = "armature.reverse_auto_parent"
    bl_label = "Reverse Auto-Parent/Remove Change"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='EDIT')
        arm = obj.data
        reversed_count = 0
        for bone in arm.edit_bones:
            if bone.select:
                old_parent_name = None
                if "QGS_old_parent" in bone:
                    old_parent_name = bone["QGS_old_parent"]
                    del bone["QGS_old_parent"]
                elif "QGS_removed_parent" in bone:
                    old_parent_name = bone["QGS_removed_parent"]
                    del bone["QGS_removed_parent"]
                if old_parent_name and old_parent_name in arm.edit_bones:
                    bone.parent = arm.edit_bones[old_parent_name]
                    reversed_count += 1
                elif old_parent_name is not None:
                    bone.parent = None
        bpy.ops.object.mode_set(mode='POSE')
        if reversed_count:
            self.report({'INFO'}, f"Reversed changes on {reversed_count} bone(s).")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No stored original parent found on selected bones.")
            return {'CANCELLED'}

class AddChildOfConstraintOperator(bpy.types.Operator):
    """Add a Child-of Constraint to all selected bones (except the active one),
       optionally setting inverse if toggled."""
    bl_idname = "armature.add_child_of_constraint"
    bl_label = "Add Child-of Constraint"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Armature must be in Pose Mode.")
            return {'CANCELLED'}
        selected_bones = context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bone selected. Please select at least one bone.")
            return {'CANCELLED'}
        if len(selected_bones) < 2:
            self.report({'ERROR'}, "Select at least one additional bone along with the active bone.")
            return {'CANCELLED'}
        active_bone = context.active_pose_bone
        if not active_bone:
            self.report({'ERROR'}, "No active pose bone selected.")
            return {'CANCELLED'}
        set_inverse = context.scene.set_inverse_child_of
        for bone in selected_bones:
            if bone != active_bone:
                constraint = bone.constraints.new('CHILD_OF')
                constraint.name = "QGS_ChildOf"
                constraint.target = obj
                constraint.subtarget = active_bone.name
                if set_inverse:
                    obj.data.bones.active = obj.data.bones.get(bone.name)
                    bpy.ops.constraint.childof_set_inverse(
                        constraint=constraint.name,
                        owner='BONE',
                    )
        self.report({'INFO'}, f"Child-of constraint added to {len(selected_bones)-1} bone(s). Set Inverse: {set_inverse}")
        return {'FINISHED'}

class RemoveChildOfConstraintOperator(bpy.types.Operator):
    """Remove the Child-of Constraint from the active bone."""
    bl_idname = "armature.remove_child_of_constraint"
    bl_label = "Remove Child-of Constraint"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Armature must be in Pose Mode.")
            return {'CANCELLED'}
        selected_bones = context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bone selected. Please select at least one bone.")
            return {'CANCELLED'}
        active_bone = context.active_pose_bone
        if not active_bone:
            self.report({'ERROR'}, "No active pose bone selected.")
            return {'CANCELLED'}
        constraint = None
        for con in active_bone.constraints:
            if con.name == "QGS_ChildOf":
                constraint = con
                break
        if constraint:
            active_bone.constraints.remove(constraint)
            self.report({'INFO'}, f"Child-of constraint removed from bone '{active_bone.name}'.")
        else:
            self.report({'INFO'}, "No Child-of constraint named 'QGS_ChildOf' found on the active bone.")
        return {'FINISHED'}

class RotateBoneOperator(bpy.types.Operator):
    bl_idname = "armature.rotate_bones_edit"
    bl_label = "Rotate Bones Around Head"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        items=[('X', 'X Axis', ''), ('Y', 'Y Axis', ''), ('Z', 'Z Axis', '')],
        default='X'
    )

    reverse: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE' or context.mode != 'EDIT_ARMATURE':
            self.report({'ERROR'}, "Must be in Edit Mode with an armature selected.")
            return {'CANCELLED'}

        angle = context.scene.qgs_rotation_angle
        if self.reverse:
            angle = -angle

        angle_rad = math.radians(angle)

        for bone in context.selected_editable_bones:
            head_pos = bone.head.copy()
            tail_pos = bone.tail.copy()
            vec = tail_pos - head_pos

            rot_matrix = mathutils.Matrix.Rotation(angle_rad, 3, self.axis)
            rotated_vec = rot_matrix @ vec

            bone.tail = bone.head + rotated_vec

        self.report({'INFO'}, f"Bone tails rotated {angle}° around {self.axis}-axis.")
        return {'FINISHED'}

class RotateBonesXOperator(RotateBoneOperator):
    bl_idname = "armature.rotate_bones_x"
    bl_label = "Rotate Head 90° X"
    def execute(self, context):
        self.axis = 'X'
        self.reverse = False
        return super().execute(context)

class RotateBonesYOperator(RotateBoneOperator):
    bl_idname = "armature.rotate_bones_y"
    bl_label = "Rotate Bone 90° Y"
    def execute(self, context):
        self.axis = 'Y'
        self.reverse = False
        return super().execute(context)

class RotateBonesZOperator(RotateBoneOperator):
    bl_idname = "armature.rotate_bones_z"
    bl_label = "Rotate Bone 90° Z"
    def execute(self, context):
        self.axis = 'Z'
        self.reverse = False
        return super().execute(context)
    
class RotateBonesXReverseOperator(RotateBoneOperator):
    bl_idname = "armature.rotate_bones_x_reverse"
    bl_label = "Rotate Bone -X"
    def execute(self, context):
        self.axis = 'X'
        self.reverse = True
        return super().execute(context)

class RotateBonesYReverseOperator(RotateBoneOperator):
    bl_idname = "armature.rotate_bones_y_reverse"
    bl_label = "Rotate Bone -Y"
    def execute(self, context):
        self.axis = 'Y'
        self.reverse = True
        return super().execute(context)

class RotateBonesZReverseOperator(RotateBoneOperator):
    bl_idname = "armature.rotate_bones_z_reverse"
    bl_label = "Rotate Bone -Z"
    def execute(self, context):
        self.axis = 'Z'
        self.reverse = True
        return super().execute(context)
    
# ------------------ Join and Separate Operators ------------------

class JoinObjectsOperator(bpy.types.Operator):
    """Join selected mesh objects, rename the joined object, and mark it as QGS."""
    bl_idname = "object.join_objects"
    bl_label = "Join Objects"

    def execute(self, context):
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if len(selected_meshes) < 2:
            self.report({'INFO'}, "Need at least two mesh objects to join.")
            return {'CANCELLED'}
        new_name = context.scene.join_objects_name
        context.view_layer.objects.active = selected_meshes[0]
        bpy.ops.object.join()
        joined_obj = context.active_object
        if joined_obj:
            joined_obj.name = new_name
            if joined_obj.data:
                joined_obj.data.name = new_name
            joined_obj["QGS"] = True
            print(f"DEBUG: Marked joined object '{joined_obj.name}' as QGS.")
            self.report({'INFO'}, f"Joined objects into '{new_name}' (QGS flagged).")
        else:
            self.report({'INFO'}, "No joined object found.")
        return {'FINISHED'}

class SeparateVertexGroupsOperator(bpy.types.Operator):
    """
    Separates the active mesh into separate objects based on its vertex groups,
    guaranteeing exactly one new object per group.
    Also creates a non-physical backup of the mesh data.
    """
    bl_idname = "object.separate_vertex_groups"
    bl_label = "Separate Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("DEBUG: Starting SeparateVertexGroupsOperator...")

        original_obj = context.active_object
        if not original_obj or original_obj.type != 'MESH':
            self.report({'INFO'}, "Active object is not a mesh.")
            print("DEBUG: Cancelled because active object is not a mesh.")
            return {'CANCELLED'}

        if not original_obj.vertex_groups:
            self.report({'INFO'}, "Active mesh has no vertex groups.")
            print("DEBUG: Cancelled because mesh has no vertex groups.")
            return {'CANCELLED'}

        backup_mesh = original_obj.data.copy()
        backup_mesh.name = "BACKUP_" + original_obj.data.name
        bpy.context.scene["QGS_backup_mesh_name"] = backup_mesh.name
        print(f"DEBUG: Backup mesh data created with name '{backup_mesh.name}'.")

        main_obj_name = original_obj.name
        vgroup_names = [vg.name for vg in original_obj.vertex_groups]

        bpy.ops.object.mode_set(mode='EDIT')

        for vg_name in vgroup_names:
            bpy.ops.mesh.select_all(action='DESELECT')
            idx = original_obj.vertex_groups.find(vg_name)
            if idx == -1:
                continue
            original_obj.vertex_groups.active_index = idx
            bpy.ops.object.vertex_group_select()
            bpy.ops.object.mode_set(mode='OBJECT')
            selected_verts = [v for v in original_obj.data.vertices if v.select]
            if not selected_verts:
                print(f"DEBUG: Group '{vg_name}' has no assigned vertices; skipping.")
                bpy.ops.object.mode_set(mode='EDIT')
                continue
            prev_objs = set(context.scene.objects)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')
            new_objs = [obj for obj in context.scene.objects if obj not in prev_objs and obj.name != main_obj_name]
            if not new_objs:
                print(f"DEBUG: No new objects found for group '{vg_name}'.")
                continue
            if len(new_objs) == 1:
                final_obj = new_objs[0]
                print(f"DEBUG: Group '{vg_name}' => single object '{final_obj.name}'.")
            else:
                print(f"DEBUG: Group '{vg_name}' => multiple objects; joining them.")
                bpy.ops.object.select_all(action='DESELECT')
                for o in new_objs:
                    o.select_set(True)
                context.view_layer.objects.active = new_objs[0]
                bpy.ops.object.join()
                final_obj = context.active_object
                print(f"DEBUG: Joined into final object '{final_obj.name}'.")
            final_obj.name = vg_name
            final_obj.data.name = vg_name
            final_obj["QGS"] = True
            original_obj = bpy.data.objects.get(main_obj_name)
            if not original_obj:
                print("DEBUG: Original object lost during separation.")
                self.report({'INFO'}, "Original object lost or removed.")
                return {'CANCELLED'}
            bpy.ops.object.select_all(action='DESELECT')
            original_obj.select_set(True)
            context.view_layer.objects.active = original_obj
            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.object.mode_set(mode='OBJECT')
        original_obj = bpy.data.objects.get(main_obj_name)
        if original_obj and len(original_obj.data.vertices) == 0:
            print(f"DEBUG: Original object '{main_obj_name}' is empty; removing.")
            bpy.data.objects.remove(original_obj, do_unlink=True)
            self.report({'INFO'}, "Original object was empty and removed.")
        else:
            self.report({'INFO'}, "Mesh separated by vertex groups.")
        print("DEBUG: Separation complete.")
        return {'FINISHED'}

def is_QGS_mesh(obj):
    if obj.type != 'MESH':
        return False
    if obj.get("QGS", False):
        return True
    for vg in obj.vertex_groups:
        if vg.name.startswith("QGS_"):
            return True
    for mod in obj.modifiers:
        if mod.type == 'ARMATURE' and mod.name == "QGS_Armature":
            return True
    return False

class UnlinkAddonOperator(bpy.types.Operator):
    """Delete all changes made with the add-on.
       Re-joins QGS-affected meshes (even if only one exists),
       then restores the original mesh data from backup (if available),
       removes all QGS-related data, and finally sets location, rotation, scale to default.
    """
    bl_idname = "object.unlink_addon"
    bl_label = "Delete All Made By User"

    def execute(self, context):
        print("DEBUG: Running UnlinkAddonOperator (Delete All Made By User)...")

        obj = context.object
        if obj and obj.type == 'ARMATURE' and obj.mode == 'POSE':
            bpy.ops.object.mode_set(mode='OBJECT')
            print("DEBUG: Switched from Pose Mode to Object Mode before cleanup.")

        if "QGS_backup_mesh_name" in bpy.context.scene:
            backup_mesh_name = bpy.context.scene["QGS_backup_mesh_name"]
            if backup_mesh_name in bpy.data.meshes:
                QGS_meshes = [o for o in list(bpy.data.objects) if is_QGS_mesh(o)]
                if QGS_meshes:
                    bpy.ops.object.select_all(action='DESELECT')
                    for o in QGS_meshes:
                        o.select_set(True)
                    context.view_layer.objects.active = QGS_meshes[0]
                    bpy.ops.object.join()
                    joined_obj = context.active_object
                else:
                    joined_obj = context.active_object

                if joined_obj and joined_obj.type == 'MESH':
                    joined_obj.data = bpy.data.meshes[backup_mesh_name]
                    joined_obj.name = context.scene.join_objects_name
                    if joined_obj.data:
                        joined_obj.data.name = context.scene.join_objects_name
                    print(f"DEBUG: Restored backup mesh data to '{joined_obj.name}'.")

                for o in list(bpy.data.objects):
                    if o.type == 'MESH' and o.get("QGS", False) and o != joined_obj:
                        bpy.data.objects.remove(o, do_unlink=True)
                        print(f"DEBUG: Removed extra QGS object '{o.name}'.")

                del bpy.context.scene["QGS_backup_mesh_name"]
                remove_existing_vertex_groups_modifiers_and_armature(keep_QGS_mesh=True)

                if joined_obj:
                    bpy.ops.object.select_all(action='DESELECT')
                    joined_obj.select_set(True)
                    context.view_layer.objects.active = joined_obj
                    joined_obj.location = (0, 0, 0)
                    joined_obj.rotation_euler = (0, 0, 0)
                    joined_obj.scale = (1, 1, 1)
                    print("DEBUG: Set final object's location=(0,0,0), rotation=(0,0,0), scale=(1,1,1).")

                self.report(
                    {'INFO'},
                    "Backup restored; original mesh data recovered, and transforms set to defaults."
                )

                if context.object and context.object.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                return {'FINISHED'}
            else:
                print("DEBUG: Backup mesh name not found in bpy.data.meshes.")

        QGS_meshes = [o for o in list(bpy.data.objects) if is_QGS_mesh(o)]
        if QGS_meshes:
            print(f"DEBUG: Found {len(QGS_meshes)} QGS-affected mesh object(s).")
            if len(QGS_meshes) > 1:
                bpy.ops.object.select_all(action='DESELECT')
                for o in QGS_meshes:
                    o.select_set(True)
                context.view_layer.objects.active = QGS_meshes[0]
                bpy.ops.object.join()
                joined_obj = context.active_object
                if joined_obj:
                    joined_obj.name = context.scene.join_objects_name
                    if joined_obj.data:
                        joined_obj.data.name = context.scene.join_objects_name
                    print(f"DEBUG: Rejoined QGS objects into '{joined_obj.name}'.")
            else:
                joined_obj = QGS_meshes[0]
                print(f"DEBUG: Only one QGS-affected mesh found: '{joined_obj.name}'. No join necessary.")
            if joined_obj and "QGS" in joined_obj:
                del joined_obj["QGS"]
        else:
            print("DEBUG: No QGS-affected mesh objects found to rejoin.")
            joined_obj = None

        remove_existing_vertex_groups_modifiers_and_armature(keep_QGS_mesh=True)

        if joined_obj:
            bpy.ops.object.select_all(action='DESELECT')
            joined_obj.select_set(True)
            context.view_layer.objects.active = joined_obj
            joined_obj.location = (0, 0, 0)
            joined_obj.rotation_euler = (0, 0, 0)
            joined_obj.scale = (1, 1, 1)
            print("DEBUG: Set final object's location=(0,0,0), rotation=(0,0,0), scale=(1,1,1).")

        if context.object and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        print("DEBUG: Completed removal of QGS items, final object set to default transforms.")
        self.report(
            {'INFO'},
            "All QGS changes removed; mesh rejoined, transforms set to default."
        )
        return {'FINISHED'}

class DialogMessage(bpy.types.Operator):
    """Simple popup message"""
    bl_idname = "object.dialog_message"
    bl_label = "Message"
    message: bpy.props.StringProperty(name="")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text=self.message)

# ------------------ Panel ------------------

class ArmatureToolsPanel(bpy.types.Panel):
    bl_label = "Quick Rig"
    bl_idname = "OBJECT_PT_quick_rig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Armature Tools"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Armature Options")
        layout.operator("object.armature_and_vertex_groups", text="Create Armature & Vertex Groups")

        row = layout.row(align=True)
        row.operator("armature.auto_parent_selected_bones", text="Auto-Parent Selected Bones")
        row.operator("armature.reverse_auto_parent", text="Reverse Auto-Parent/Remove")

        layout.operator("armature.remove_parent_selected_bones", text="Remove Parent from Selected Bones")

        row = layout.row(align=True)
        row.operator("armature.add_child_of_constraint", text="Add Child-of Constraint")
        layout.prop(context.scene, "set_inverse_child_of", text="Set Inverse")
        row.operator("armature.remove_child_of_constraint", text="Remove Child-of Constraint")
        
        layout.label(text="Bone Rotation (Edit Mode)", icon='BONE_DATA')
        row = layout.row(align=True)
        row.operator("armature.rotate_bones_x", text="X+")
        row.operator("armature.rotate_bones_y", text="Y+")
        row.operator("armature.rotate_bones_z", text="Z+")
        row = layout.row(align=True)
        row.operator("armature.rotate_bones_x_reverse", text="X-")
        row.operator("armature.rotate_bones_y_reverse", text="Y-")
        row.operator("armature.rotate_bones_z_reverse", text="Z-")
        
        layout.separator()
        layout.label(text="Object Options")
        layout.prop(context.scene, "join_objects_name", text="Enter Name")
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        join_count = len(selected_meshes)
        if join_count < 2:
            join_count = 0
        layout.label(text=f"Will join {join_count} object(s).")
        layout.operator("object.join_objects", text="Join Selected Objects")

        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.vertex_groups:
            sep_count = 0
            for vg in obj.vertex_groups:
                has_geom = False
                for v in obj.data.vertices:
                    try:
                        w = vg.weight(v.index)
                    except RuntimeError:
                        w = 0
                    if w > 0:
                        has_geom = True
                        break
                if has_geom:
                    sep_count += 1
            if sep_count < 2:
                sep_count = 0
            layout.label(text=f"Will separate into {sep_count} object(s).")
        else:
            layout.label(text="Will separate into 0 objects.")
        layout.operator("object.separate_vertex_groups", text="Separate Vertex Groups")

        layout.label(text="Deletes All Changes Added With Add-on", icon='ERROR')
        QGS_count = count_QGS_changes()
        layout.label(text=f"Will remove {QGS_count} QGS changes.")
        layout.operator("object.unlink_addon", text="Delete All Made By User")

        # --- Updater Section ---
        layout.separator()
        layout.label(text="Online Updater", icon='FILE_REFRESH')
        layout.operator("addon.check_for_update", text="Check for Update", icon='FILE_REFRESH')
        layout.operator("addon.update_now", text="Update Now", icon='FILE_TICK')

# ------------------ Registration ------------------

classes = [
    ArmatureAndVertexGroupsOperator,
    AutoParentSelectedBonesOperator,
    RemoveParentSelectedBonesOperator,
    ReverseAutoParentChangeOperator,
    AddChildOfConstraintOperator,
    RemoveChildOfConstraintOperator,
    JoinObjectsOperator,
    UnlinkAddonOperator,
    DialogMessage,
    SeparateVertexGroupsOperator,
    RotateBoneOperator,
    RotateBonesXOperator,
    RotateBonesYOperator,
    RotateBonesZOperator,
    RotateBonesXReverseOperator,
    RotateBonesYReverseOperator,
    RotateBonesZReverseOperator,
    ArmatureToolsPanel,
    CheckForUpdateOperator,
    UpdateNowOperator,
]

def register():
    bpy.types.Scene.set_inverse_child_of = bpy.props.BoolProperty(
        name="Set Inverse",
        description="If checked, automatically call Set Inverse for each new Child-of constraint",
        default=True
    )
    bpy.types.Scene.join_objects_name = bpy.props.StringProperty(
        name="Join Object Name",
        description="Name to assign to the newly joined object when joining or deleting all",
        default="JoinedMesh"
    )
    bpy.types.Scene.qgs_rotation_angle = bpy.props.FloatProperty(
        name="Rotation Angle",
        description="Angle for rotating bones",
        default=90.0,
        min=-360.0,
        max=360.0
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.set_inverse_child_of
    del bpy.types.Scene.join_objects_name
    del bpy.types.Scene.qgs_rotation_angle
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
