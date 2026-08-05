#!/bin/bash

# Define the base directory
BASE_DIR="/usr/share/inkscape/extensions"

# List of individual files to delete
FILES_TO_DELETE=(
    dxf12_outlines.inx
    dxf12_outlines.py
    dxf_outlines.inx
    dxf_outlines.py
    gimp_xcf.inx
    gimp_xcf.py
    hpgl_output.inx
    hpgl_output.py
    ink2canvas.inx
    ink2canvas.py
    jessyink_autotexts.inx
    jessyink_autotexts.py
    jessyInk_core_mouseHandler_noclick.js
    jessyInk_core_mouseHandler_zoomControl.js
    jessyink_effects.inx
    jessyink_effects.py
    jessyink_export.inx
    jessyink_export.py
    jessyink_install.inx
    jessyink_install.py
    jessyInk.js
    jessyink_key_bindings.inx
    jessyink_key_bindings.py
    jessyink_master_slide.inx
    jessyink_master_slide.py
    jessyink_mouse_handler.inx
    jessyink_mouse_handler.py
    jessyink_summary.inx
    jessyink_summary.py
    jessyink_transitions.inx
    jessyink_transitions.py
    jessyink_uninstall.inx
    jessyink_uninstall.py
    jessyink_video.inx
    jessyink_video.py
    jessyink_video.svg
    jessyink_view.inx
    jessyink_view.py
    media_zip.inx
    media_zip.py
    raster_output_jpg.inx
    raster_output_jpg.py
    raster_output_jpg.svg
    raster_output_png.inx
    raster_output_png.py
    raster_output_tiff.inx
    raster_output_tiff.py
    raster_output_webp.inx
    raster_output_webp.py
    synfig_fileformat.py
    synfig_output.inx
    synfig_output.py
    synfig_prepare.py
    tar_layers.inx
    tar_layers.py
)

echo "Deleting individual files..."
for file in "${FILES_TO_DELETE[@]}"; do
    full_path="$BASE_DIR/$file"
    if [ -f "$full_path" ]; then
        rm -f "$full_path"
        echo "Deleted: $full_path"
    else
        echo "File not found: $full_path"
    fi
done

# Directories to delete
#DIRS_TO_DELETE=(
#    "$BASE_DIR/other/extension-xaml"
#    "$BASE_DIR/inkex"
#)

#echo "Deleting directories..."
#for dir in "${DIRS_TO_DELETE[@]}"; do
#    if [ -d "$dir" ]; then
#        rm -rf "$dir"
#        echo "Deleted directory: $dir"
#    else
#        echo "Directory not found: $dir"
#    fi
#done

echo "Cleanup complete."
