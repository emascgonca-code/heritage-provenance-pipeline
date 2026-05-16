"""
Heritage Provenance & Integrity Pipeline — Blender Addon
=========================================================
Author: Ema Gonçalves
Version: 0.1
Description:
    Computes SHA-256 hash of source image files (e.g. archival drawings),
    extracts manually entered geometric parameters, and generates a structured
    JSON provenance log — all from within Blender.

Installation:
    Edit > Preferences > Add-ons > Install > select this .py file > Enable

Usage:
    In the 3D Viewport, open the sidebar (N key) > "Heritage Provenance" tab.
"""

bl_info = {
    "name": "Heritage Provenance & Integrity Pipeline",
    "author": "Ema Gonçalves",
    "version": (0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Heritage Provenance",
    "description": "Computes SHA-256 hash of archival source files and generates structured provenance logs for heritage 3D reconstruction.",
    "category": "Heritage",
}

import bpy
import hashlib
import json
import os
from datetime import datetime, timezone


# ─────────────────────────────────────────────
#  PARAMETER ITEM (collection property element)
# ─────────────────────────────────────────────

class HERITAGE_ParameterItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Parameter", default="length_between_perpendiculars")
    value: bpy.props.StringProperty(name="Value", default="")
    unit: bpy.props.StringProperty(name="Unit", default="feet")
    certainty: bpy.props.EnumProperty(
        name="Certainty",
        items=[
            ("high",   "High — read directly",         "Value is clearly legible"),
            ("medium", "Medium — partially legible",    "Value required interpretation"),
            ("low",    "Low — inferred",                "Value was inferred from context"),
        ],
        default="high",
    )
    note: bpy.props.StringProperty(name="Note", default="")


# ─────────────────────────────────────────────
#  SCENE-LEVEL PROPERTIES
# ─────────────────────────────────────────────

class HERITAGE_Properties(bpy.types.PropertyGroup):

    # Source file
    source_filepath: bpy.props.StringProperty(
        name="Source File",
        description="Path to the archival source image (JPG, PNG, TIFF, PDF…)",
        subtype="FILE_PATH",
        default="",
    )

    # Archive metadata
    archive_reference: bpy.props.StringProperty(
        name="Archive Reference",
        description="Institutional reference / call number",
        default="LR-FAF-SA5b-0001-P_0001",
    )
    archive_institution: bpy.props.StringProperty(
        name="Institution",
        default="Lloyd's Register Foundation",
    )
    document_title: bpy.props.StringProperty(
        name="Document Title",
        default="Midship Section — New Ship No. 55 Thermopylae",
    )
    document_date: bpy.props.StringProperty(
        name="Document Date",
        default="1869",
    )
    source_url: bpy.props.StringProperty(
        name="Source URL",
        default="",
    )

    # Validator
    validator_name: bpy.props.StringProperty(
        name="Validator",
        default="Ema Gonçalves",
    )

    # Output
    output_directory: bpy.props.StringProperty(
        name="Output Directory",
        subtype="DIR_PATH",
        default="//",
    )

    # Parameters list
    parameters: bpy.props.CollectionProperty(type=HERITAGE_ParameterItem)
    active_parameter_index: bpy.props.IntProperty(default=0)

    # State
    computed_hash: bpy.props.StringProperty(default="")
    file_size_bytes: bpy.props.IntProperty(default=0)
    log_path: bpy.props.StringProperty(default="")
    status_message: bpy.props.StringProperty(default="")


# ─────────────────────────────────────────────
#  OPERATORS
# ─────────────────────────────────────────────

class HERITAGE_OT_ComputeHash(bpy.types.Operator):
    """Compute SHA-256 hash of the selected source file"""
    bl_idname = "heritage.compute_hash"
    bl_label  = "Compute Hash"

    def execute(self, context):
        props = context.scene.heritage_props
        filepath = bpy.path.abspath(props.source_filepath)

        if not filepath or not os.path.isfile(filepath):
            props.status_message = "⚠ File not found. Check the path."
            self.report({"WARNING"}, props.status_message)
            return {"CANCELLED"}

        sha256 = hashlib.sha256()
        size   = 0
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
                    size += len(chunk)
        except OSError as e:
            props.status_message = f"⚠ Could not read file: {e}"
            return {"CANCELLED"}

        props.computed_hash   = sha256.hexdigest()
        props.file_size_bytes = size
        props.status_message  = "✓ Hash computed successfully."
        return {"FINISHED"}


class HERITAGE_OT_AddParameter(bpy.types.Operator):
    """Add a geometric parameter entry"""
    bl_idname = "heritage.add_parameter"
    bl_label  = "Add Parameter"

    def execute(self, context):
        props = context.scene.heritage_props
        item = props.parameters.add()
        item.name = "new_parameter"
        props.active_parameter_index = len(props.parameters) - 1
        return {"FINISHED"}


class HERITAGE_OT_RemoveParameter(bpy.types.Operator):
    """Remove the selected parameter entry"""
    bl_idname = "heritage.remove_parameter"
    bl_label  = "Remove Parameter"

    def execute(self, context):
        props = context.scene.heritage_props
        idx   = props.active_parameter_index
        if 0 <= idx < len(props.parameters):
            props.parameters.remove(idx)
            props.active_parameter_index = max(0, idx - 1)
        return {"FINISHED"}


class HERITAGE_OT_ExportLog(bpy.types.Operator):
    """Export the structured provenance log as JSON"""
    bl_idname = "heritage.export_log"
    bl_label  = "Export Provenance Log"

    def execute(self, context):
        props    = context.scene.heritage_props
        filepath = bpy.path.abspath(props.source_filepath)

        if not props.computed_hash:
            props.status_message = "⚠ Compute hash before exporting."
            self.report({"WARNING"}, props.status_message)
            return {"CANCELLED"}

        # Build parameter list
        parameters = []
        for p in props.parameters:
            entry = {
                "name":      p.name,
                "value":     p.value,
                "unit":      p.unit,
                "certainty": p.certainty,
            }
            if p.note:
                entry["note"] = p.note
            parameters.append(entry)

        # Assemble log
        log = {
            "pipeline_name":    "Heritage Provenance & Integrity Pipeline",
            "pipeline_version": "0.1",
            "timestamp_utc":    datetime.now(timezone.utc).isoformat(),
            "source": {
                "filepath":           filepath,
                "filename":           os.path.basename(filepath),
                "sha256":             props.computed_hash,
                "file_size_bytes":    props.file_size_bytes,
                "archive_reference":  props.archive_reference,
                "institution":        props.archive_institution,
                "document_title":     props.document_title,
                "document_date":      props.document_date,
                "source_url":         props.source_url,
            },
            "parameters_extracted": parameters,
            "human_validator":      props.validator_name,
            "validation_date_utc":  datetime.now(timezone.utc).date().isoformat(),
            "notes": (
                "All parameter values were reviewed and confirmed by the human validator. "
                "The SHA-256 hash anchors the integrity of the source document at the time "
                "of this record. Any subsequent modification to the source file will produce "
                "a different hash, making alterations detectable."
            ),
        }

        # Write JSON
        out_dir  = bpy.path.abspath(props.output_directory)
        os.makedirs(out_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename      = f"provenance_log_{timestamp_str}.json"
        out_path      = os.path.join(out_dir, filename)

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(log, f, indent=2, ensure_ascii=False)
        except OSError as e:
            props.status_message = f"⚠ Could not write log: {e}"
            return {"CANCELLED"}

        props.log_path       = out_path
        props.status_message = f"✓ Log exported: {filename}"
        self.report({"INFO"}, props.status_message)
        return {"FINISHED"}


class HERITAGE_OT_CopyHash(bpy.types.Operator):
    """Copy the SHA-256 hash to clipboard"""
    bl_idname = "heritage.copy_hash"
    bl_label  = "Copy Hash"

    def execute(self, context):
        props = context.scene.heritage_props
        if props.computed_hash:
            context.window_manager.clipboard = props.computed_hash
            props.status_message = "✓ Hash copied to clipboard."
        return {"FINISHED"}


# ─────────────────────────────────────────────
#  PANEL
# ─────────────────────────────────────────────

class HERITAGE_PT_MainPanel(bpy.types.Panel):
    bl_label       = "Heritage Provenance"
    bl_idname      = "HERITAGE_PT_main"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Heritage Provenance"

    def draw(self, context):
        layout = self.layout
        props  = context.scene.heritage_props

        # ── Source File ──────────────────────────────
        box = layout.box()
        box.label(text="Source Document", icon="IMAGE_DATA")
        box.prop(props, "source_filepath")
        box.prop(props, "archive_reference")
        box.prop(props, "archive_institution")
        box.prop(props, "document_title")
        box.prop(props, "document_date")
        box.prop(props, "source_url")

        layout.separator()

        # ── Hash ────────────────────────────────────
        box = layout.box()
        box.label(text="Integrity — SHA-256", icon="LOCKED")
        box.operator("heritage.compute_hash", icon="FILE_REFRESH")

        if props.computed_hash:
            # Display hash in two wrapped rows (first/second 32 chars)
            col = box.column(align=True)
            col.label(text=props.computed_hash[:32])
            col.label(text=props.computed_hash[32:])
            row = box.row()
            row.label(text=f"Size: {props.file_size_bytes:,} bytes")
            box.operator("heritage.copy_hash", icon="COPYDOWN")

        layout.separator()

        # ── Parameters ──────────────────────────────
        box = layout.box()
        box.label(text="Geometric Parameters", icon="DRIVER_DISTANCE")

        row = box.row()
        row.operator("heritage.add_parameter",    icon="ADD",    text="Add")
        row.operator("heritage.remove_parameter", icon="REMOVE", text="Remove")

        for i, param in enumerate(props.parameters):
            sub = box.box()
            sub.prop(param, "name")
            row = sub.row(align=True)
            row.prop(param, "value")
            row.prop(param, "unit")
            sub.prop(param, "certainty")
            sub.prop(param, "note")

        layout.separator()

        # ── Export ──────────────────────────────────
        box = layout.box()
        box.label(text="Export", icon="EXPORT")
        box.prop(props, "validator_name")
        box.prop(props, "output_directory")
        box.operator("heritage.export_log", icon="FILE_TICK")

        if props.log_path:
            box.label(text=os.path.basename(props.log_path), icon="CHECKMARK")

        layout.separator()

        # ── Status ──────────────────────────────────
        if props.status_message:
            row = layout.row()
            icon = "INFO" if props.status_message.startswith("✓") else "ERROR"
            row.label(text=props.status_message, icon=icon)


# ─────────────────────────────────────────────
#  REGISTRATION
# ─────────────────────────────────────────────

classes = (
    HERITAGE_ParameterItem,
    HERITAGE_Properties,
    HERITAGE_OT_ComputeHash,
    HERITAGE_OT_AddParameter,
    HERITAGE_OT_RemoveParameter,
    HERITAGE_OT_ExportLog,
    HERITAGE_OT_CopyHash,
    HERITAGE_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.heritage_props = bpy.props.PointerProperty(type=HERITAGE_Properties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.heritage_props


if __name__ == "__main__":
    register()
