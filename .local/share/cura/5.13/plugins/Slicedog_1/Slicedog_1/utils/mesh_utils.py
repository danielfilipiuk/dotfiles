from UM.Math.Vector import Vector

def paintArrow(mb, color, center, direction, arrow_head_length, arrow_head_width, arrow_tail_length,
               arrow_tail_width, pull=True):
    n = direction.normalized()
    invert_arrow = pull
    
    arrow_total_length = arrow_head_length + arrow_tail_length

    p_base_0 = center + n * arrow_head_length
    p_tail_0 = center + n * arrow_total_length

    if invert_arrow:
        p_base_0 = center + n * arrow_tail_length
        p_head = p_tail_0
        p_tail_0 = center
    else:
        p_head = center

    p_base_y1 = p_base_0 + Vector.Unit_Y * arrow_head_width
    p_base_y2 = p_base_0 - Vector.Unit_Y * arrow_head_width
    p_base_x1 = p_base_0 + Vector.Unit_X * arrow_head_width
    p_base_x2 = p_base_0 - Vector.Unit_X * arrow_head_width
    p_base_z1 = p_base_0 + Vector.Unit_Z * arrow_head_width
    p_base_z2 = p_base_0 - Vector.Unit_Z * arrow_head_width

    mb.addFace(p_base_y1, p_head, p_base_x1, color=color)
    mb.addFace(p_base_x1, p_head, p_base_y2, color=color)
    mb.addFace(p_base_y2, p_head, p_base_x2, color=color)
    mb.addFace(p_base_x2, p_head, p_base_y1, color=color)
    mb.addFace(p_base_z1, p_head, p_base_y1, color=color)
    mb.addFace(p_base_z2, p_head, p_base_y1, color=color)
    mb.addFace(p_base_z2, p_head, p_base_y2, color=color)
    mb.addFace(p_base_y2, p_head, p_base_z1, color=color)
    mb.addFace(p_base_x1, p_head, p_base_z1, color=color)
    mb.addFace(p_base_z1, p_head, p_base_x2, color=color)
    mb.addFace(p_base_x2, p_head, p_base_z2, color=color)
    mb.addFace(p_base_z2, p_head, p_base_x1, color=color)

    p_tail_y1 = p_tail_0 + Vector.Unit_Y * arrow_tail_width
    p_tail_y2 = p_tail_0 - Vector.Unit_Y * arrow_tail_width
    p_tail_x1 = p_tail_0 + Vector.Unit_X * arrow_tail_width
    p_tail_x2 = p_tail_0 - Vector.Unit_X * arrow_tail_width
    p_tail_z1 = p_tail_0 + Vector.Unit_Z * arrow_tail_width
    p_tail_z2 = p_tail_0 - Vector.Unit_Z * arrow_tail_width

    p_tail_base_y1 = p_base_0 + Vector.Unit_Y * arrow_tail_width
    p_tail_base_y2 = p_base_0 - Vector.Unit_Y * arrow_tail_width
    p_tail_base_x1 = p_base_0 + Vector.Unit_X * arrow_tail_width
    p_tail_base_x2 = p_base_0 - Vector.Unit_X * arrow_tail_width
    p_tail_base_z1 = p_base_0 + Vector.Unit_Z * arrow_tail_width
    p_tail_base_z2 = p_base_0 - Vector.Unit_Z * arrow_tail_width

    mb.addFace(p_tail_y1, p_tail_base_y1, p_tail_x1, color=color)
    mb.addFace(p_tail_x1, p_tail_base_x1, p_tail_y2, color=color)
    mb.addFace(p_tail_y2, p_tail_base_y2, p_tail_x2, color=color)
    mb.addFace(p_tail_x2, p_tail_base_x2, p_tail_y1, color=color)
    mb.addFace(p_tail_z1, p_tail_base_z1, p_tail_y1, color=color)
    mb.addFace(p_tail_z2, p_tail_base_z2, p_tail_y1, color=color)
    mb.addFace(p_tail_z2, p_tail_base_z2, p_tail_y2, color=color)
    mb.addFace(p_tail_y2, p_tail_base_y2, p_tail_z1, color=color)
    mb.addFace(p_tail_x1, p_tail_base_x1, p_tail_z1, color=color)
    mb.addFace(p_tail_z1, p_tail_base_z1, p_tail_x2, color=color)
    mb.addFace(p_tail_x2, p_tail_base_x2, p_tail_z2, color=color)
    mb.addFace(p_tail_z2, p_tail_base_z2, p_tail_x1, color=color)

    mb.addFace(p_tail_base_y1, p_tail_base_x1, p_tail_x1, color=color)
    mb.addFace(p_tail_base_x1, p_tail_base_y2, p_tail_y2, color=color)
    mb.addFace(p_tail_base_y2, p_tail_base_x2, p_tail_x2, color=color)
    mb.addFace(p_tail_base_x2, p_tail_base_y1, p_tail_y1, color=color)
    mb.addFace(p_tail_base_z1, p_tail_base_y1, p_tail_y1, color=color)
    mb.addFace(p_tail_base_z2, p_tail_base_y1, p_tail_y1, color=color)
    mb.addFace(p_tail_base_z2, p_tail_base_y2, p_tail_y2, color=color)
    mb.addFace(p_tail_base_y2, p_tail_base_z1, p_tail_z1, color=color)
    mb.addFace(p_tail_base_x1, p_tail_base_z1, p_tail_z1, color=color)
    mb.addFace(p_tail_base_z1, p_tail_base_x2, p_tail_x2, color=color)
    mb.addFace(p_tail_base_x2, p_tail_base_z2, p_tail_z2, color=color)
    mb.addFace(p_tail_base_z2, p_tail_base_x1, p_tail_x1, color=color)

def paintLock(mb, color, center, direction, diameter):
    n = direction.normalized()

    p_base_0 = center + n * diameter
    p_head = center

    p_base_y1 = p_base_0 + Vector.Unit_Y * diameter
    p_base_y2 = p_base_0 - Vector.Unit_Y * diameter
    p_base_x1 = p_base_0 + Vector.Unit_X * diameter
    p_base_x2 = p_base_0 - Vector.Unit_X * diameter
    p_base_z1 = p_base_0 + Vector.Unit_Z * diameter
    p_base_z2 = p_base_0 - Vector.Unit_Z * diameter

    mb.addFace(p_base_y1, p_head, p_base_x1, color=color)
    mb.addFace(p_base_x1, p_head, p_base_y2, color=color)
    mb.addFace(p_base_y2, p_head, p_base_x2, color=color)
    mb.addFace(p_base_x2, p_head, p_base_y1, color=color)
    mb.addFace(p_base_z1, p_head, p_base_y1, color=color)
    mb.addFace(p_base_z2, p_head, p_base_y1, color=color)
    mb.addFace(p_base_z2, p_head, p_base_y2, color=color)
    mb.addFace(p_base_y2, p_head, p_base_z1, color=color)
    mb.addFace(p_base_x1, p_head, p_base_z1, color=color)
    mb.addFace(p_base_z1, p_head, p_base_x2, color=color)
    mb.addFace(p_base_x2, p_head, p_base_z2, color=color)
    mb.addFace(p_base_z2, p_head, p_base_x1, color=color)