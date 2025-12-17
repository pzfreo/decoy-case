"""
INSTRUCTIONS FOR RUNNING:
1. This script cannot run directly in the web-based Gemini Canvas because it requires 
   the 'build123d' CAD kernel which runs on local Python.

2. To run this locally, install the required libraries:
   pip install build123d ocp-vscode

3. Run the script:
   python decoy_case.py

4. Visualizing:
   - If using VS Code, install the "OCP CAD Viewer" extension to see the live 3D preview.
   - Otherwise, the script exports 'decoy_case.stl' and 'decoy_case.glb' for use in slicers.
"""

from build123d import *

# Try/Except block for VS Code visualization
try:
    from ocp_vscode import *
    VISUALIZE = True
except ImportError:
    VISUALIZE = False
    print("ocp_vscode not found, skipping visualization.")

# ==========================================
# 1. PARAMETERS
# ==========================================

# -- Physical Board Dimensions --
pcb_len = 28.5
pcb_wid = 11.0
pcb_thick = 1.6

# Component sizes
usb_len_metal = 7.0 
usb_w = 9.0
usb_h = 3.6
term_block_len = 8.5
term_block_h = 10.5

# -- Enclosure Settings --
wall_thick = 1.6
floor_thick = 4.0   # Thicker floor to allow for counterbores
fit_tol = 0.20      # Tolerance for the Lid/Base rim fit
standoff_h = 2.5    # Clearance for pins under the board
recess_h = 3.8      # Height of the PCB retention tray (from floor)
usb_anvil_h = 2.0   # Height of the "anvil" bar under the USB port (Now on Base)
usb_cut_w = 12.0    # Width of the USB opening arch

# Internal height
internal_h = 16.0

# Wire Exit Settings
slot_w = 7.0
slot_h = 1.3
wire_h_from_pcb = 5.5

# Clamp Logic
wire_center_h = standoff_h + wire_h_from_pcb 
clamp_anvil_h = wire_center_h - (slot_h / 2)
clamp_arch_top = wire_center_h + (slot_h / 2)

# Screw Settings (M3)
screw_post_dia = 6.0   
screw_pilot_dia = 2.5  
screw_clear_dia = 3.2  
head_dia = 6.0         
cb_depth = 2.0         # Depth of the counterbore recess

# -- Calculated Dimensions --
# X/Y FIT
pcb_xy_tol = 0.15

# Length Calculation (Tucked posts)
cavity_l = pcb_len + 2.0 
cavity_w = pcb_wid + (2 * screw_post_dia) + pcb_xy_tol

outer_l = cavity_l + 2*wall_thick
outer_w = cavity_w + 2*wall_thick

# Calculate Post Centers
post_offset_x = (cavity_l / 2) - (screw_post_dia / 2)
post_offset_y = (cavity_w / 2) - (screw_post_dia / 2)
post_r = screw_post_dia / 2

# ==========================================
# 2. CREATE GHOST PARTS
# ==========================================

pcb_z_center = standoff_h + (pcb_thick/2)
pcb = Box(pcb_len, pcb_wid, pcb_thick).move(Location((0, 0, pcb_z_center)))

# USB Ghost (Flush with edge)
usb_x = -(pcb_len/2) + (usb_len_metal/2)
usb_z = standoff_h + pcb_thick + (usb_h/2) - 0.5
usb = Box(usb_len_metal, usb_w, usb_h).move(Location((usb_x, 0, usb_z)))

term_x = (pcb_len/2) - (term_block_len/2)
term_z = standoff_h + pcb_thick + (term_block_h/2)
term = Box(term_block_len, pcb_wid - 1.0, term_block_h).move(Location((term_x, 0, term_z)))

# ==========================================
# 3. GENERATE THE BASE
# ==========================================

with BuildPart() as base_part:
    
    # 1. Base Plate (Floor)
    # UPDATED: Uses floor_thick instead of wall_thick
    Box(outer_l, outer_w, floor_thick, align=(Align.CENTER, Align.CENTER, Align.MIN))
    
    # 2. Alignment Lip
    # UPDATED: Z-Location uses floor_thick
    lip_height = 2.5
    with Locations((0, 0, floor_thick)):
        with BuildPart(mode=Mode.PRIVATE) as lip_obj:
            Box(cavity_l - fit_tol, cavity_w - fit_tol, lip_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Box(cavity_l - fit_tol - 2.4, cavity_w - fit_tol - 2.4, lip_height, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        add(lip_obj.part)
        
        # Cut corners for shell posts
        for x in [-post_offset_x, post_offset_x]:
            for y in [-post_offset_y, post_offset_y]:
                with Locations((x, y)):
                    # Main cylinder cut
                    Cylinder(radius=post_r + fit_tol, height=lip_height, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                    # Corner reinforcement cut
                    sx = 1 if x > 0 else -1
                    sy = 1 if y > 0 else -1
                    cut_size = post_r + fit_tol
                    with Locations((sx * cut_size/2, sy * cut_size/2, 0)):
                        Box(cut_size, cut_size, lip_height, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        
        # Cut slot for clamp tower (Back)
        with Locations((cavity_l/2, 0, 0)):
             Box(wall_thick*4, slot_w, lip_height * 2, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # 3. PCB Retention Recess
    recess_wall_t = 1.2
    # UPDATED: Z-Location uses floor_thick
    with Locations((0, 0, floor_thick)):
        with BuildPart(mode=Mode.PRIVATE) as recess_obj:
            Box(pcb_len + pcb_xy_tol + 2*recess_wall_t, pcb_wid + pcb_xy_tol + 2*recess_wall_t, recess_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Box(pcb_len + pcb_xy_tol, pcb_wid + pcb_xy_tol, recess_h, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        
        with BuildPart(mode=Mode.PRIVATE) as posts_tool:
            for x in [-post_offset_x, post_offset_x]:
                for y in [-post_offset_y, post_offset_y]:
                    with Locations((x, y)):
                        Cylinder(radius=post_r + fit_tol, height=recess_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        add(recess_obj.part - posts_tool.part)

    # 4. PCB Standoffs (Square 1mm)
    soff_size = 1.0
    soff_offset_y = (pcb_wid / 2) - (soff_size / 2)
    
    # Back Standoffs (Flush with back corners)
    soff_back_x = (pcb_len / 2) - (soff_size / 2)
    
    # Front Standoffs (Moved back 1.2mm to clear the USB opening cut)
    soff_front_x = -(pcb_len / 2) + (soff_size / 2) + 1.2
    
    # UPDATED: Z-Location uses floor_thick
    with Locations((0, 0, floor_thick)):
        # Back Pair
        with Locations([(soff_back_x, y) for y in [-soff_offset_y, soff_offset_y]]):
            Box(soff_size, soff_size, standoff_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Front Pair
        with Locations([(soff_front_x, y) for y in [-soff_offset_y, soff_offset_y]]):
            Box(soff_size, soff_size, standoff_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # 5. Screw Holes (Corners) - RESTORED COUNTERBORE
    with Locations([(x, y) for x in [-post_offset_x, post_offset_x] for y in [-post_offset_y, post_offset_y]]):
        # Full thickness clearance hole (using floor_thick)
        Cylinder(radius=screw_clear_dia/2, height=floor_thick*3, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        # Counterbore from bottom
        with Locations((0,0,0)):
             Cylinder(radius=head_dia/2, height=cb_depth, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # 6. Wire Clamp Anvil
    # UPDATED: Z-Location uses floor_thick
    with Locations((outer_l/2 - wall_thick/2, 0, floor_thick)):
        Box(wall_thick, slot_w, clamp_anvil_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # 7. FLUSH USB ANVIL (Front Filler)
    # UPDATED: Z-Location uses floor_thick
    with Locations((-outer_l/2 + wall_thick/2, 0, floor_thick)):
         Box(wall_thick, usb_cut_w - fit_tol, usb_anvil_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # 8. FINAL CUT: USB Opening (Front)
    # UPDATED: Z-Location uses floor_thick + usb_anvil_h
    cut_depth = (outer_l/2) - (pcb_len/2)
    with Locations((-outer_l/2, 0, floor_thick + usb_anvil_h)):
            Box(cut_depth, usb_cut_w, lip_height * 3, align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)


# ==========================================
# 4. GENERATE THE SHELL
# ==========================================

with BuildPart() as shell_part:
    shell_ext_h = internal_h + wall_thick 
    
    # 1. Main Block
    Box(outer_l, outer_w, shell_ext_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    
    # 2. Hollow Cavity
    Box(cavity_l, cavity_w, internal_h, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    
    # 3. Screw Posts (Reinforced)
    for x in [-post_offset_x, post_offset_x]:
        for y in [-post_offset_y, post_offset_y]:
            with Locations((x, y, 0)):
                # A. Main Post Body
                Cylinder(radius=post_r, height=internal_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # B. Corner Fill
                sx = 1 if x > 0 else -1
                sy = 1 if y > 0 else -1
                with Locations((sx * post_r/2, sy * post_r/2, 0)):
                    Box(post_r, post_r, internal_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # C. Pilot Hole
                Cylinder(radius=screw_pilot_dia/2, height=internal_h, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # 4. Z-AXIS HOLD DOWNS
    # Front (USB)
    usb_hold_h = internal_h - (standoff_h + pcb_thick + usb_h)
    if usb_hold_h > 0:
        with Locations((-(pcb_len/2) + (usb_len_metal/2), 0, internal_h)):
            Box(usb_len_metal, usb_w, usb_hold_h, align=(Align.CENTER, Align.CENTER, Align.MAX))

    # Back (Terminal)
    term_hold_h = internal_h - (standoff_h + pcb_thick + term_block_h)
    if term_hold_h > 0:
        with Locations(((pcb_len/2) - (term_block_len/2), 0, internal_h)):
             Box(term_block_len, term_block_len, term_hold_h, align=(Align.CENTER, Align.CENTER, Align.MAX))

    # 5. USB Cutout (Front / -X)
    usb_cut_top = usb_z + (usb_h + 3.0)/2
    with Locations((-outer_l/2, 0, 0)):
         Box(wall_thick*4, usb_cut_w, usb_cut_top, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # 6. Wire Clamp Arch (Back / +X)
    with Locations((outer_l/2, 0, 0)): 
        Box(wall_thick*4, slot_w, clamp_arch_top, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

# ==========================================
# 5. VISUALIZATION
# ==========================================

if VISUALIZE:
    offset_loc = Location((0, 0, floor_thick))
    vis_pcb = pcb.moved(offset_loc)
    vis_usb = usb.moved(offset_loc)
    vis_term = term.moved(offset_loc)
    
    vis_shell = shell_part.part.moved(Location((0,0, floor_thick + 30)))

    show(
        base_part, 
        vis_pcb, 
        vis_usb, 
        vis_term, 
        vis_shell,
        names=["Base Plate", "PCB", "USB", "Terminal", "Shell Cover"],
        colors=["#444444", "green", "silver", "teal", "orange"],
        alphas=[1.0, 0.8, 0.8, 0.8, 0.9]
    )

# ==========================================
# 6. EXPORT
# ==========================================

print("Exporting files...")
export_stl(base_part.part, "decoy_base.stl")
export_stl(shell_part.part, "decoy_shell.stl")

export_gltf(base_part.part, "decoy_base.glb")
export_gltf(shell_part.part, "decoy_shell.glb")
print("Done.")