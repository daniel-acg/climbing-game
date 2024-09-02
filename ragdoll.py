import math

# Ragdoll mechanics functions

def calculate_distance(pos1, pos2):
    """Calculate the distance between two points."""
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

def move_body_smoothly(limb_pos, body_pos, max_distance):
    """Smoothly move the body based on the limb's position."""
    limb_to_body_dist = calculate_distance(limb_pos, body_pos)

    if limb_to_body_dist > max_distance / 2:
        diff_x = limb_pos[0] - body_pos[0]
        diff_y = limb_pos[1] - body_pos[1]
        factor = (limb_to_body_dist - max_distance / 2) / limb_to_body_dist

        body_pos[0] += diff_x * factor
        body_pos[1] += diff_y * factor

    return body_pos

def drag_and_constrain_smoothly(limb_pos, body_pos, max_distance):
    """Handle dragging and constraints with smooth movement."""
    limb_to_body_dist = calculate_distance(limb_pos, body_pos)

    if limb_to_body_dist > max_distance / 2:
        diff_x = limb_pos[0] - body_pos[0]
        diff_y = limb_pos[1] - body_pos[1]
        factor = (limb_to_body_dist - max_distance / 2) / limb_to_body_dist

        limb_pos[0] = body_pos[0] + diff_x * (1 - factor)
        limb_pos[1] = body_pos[1] + diff_y * (1 - factor)

    return limb_pos

def maintain_body_connection(upper_body_pos, lower_body_pos, body_distance):
    """Keep the upper and lower body circles connected with a fixed distance."""
    current_distance = calculate_distance(upper_body_pos, lower_body_pos)
    if current_distance != body_distance:
        diff_x = lower_body_pos[0] - upper_body_pos[0]
        diff_y = lower_body_pos[1] - upper_body_pos[1]
        factor = body_distance / current_distance

        midpoint = [
            (upper_body_pos[0] + lower_body_pos[0]) / 2,
            (upper_body_pos[1] + lower_body_pos[1]) / 2,
        ]

        upper_body_pos = [
            midpoint[0] - diff_x * factor / 2,
            midpoint[1] - diff_y * factor / 2,
        ]
        lower_body_pos = [
            midpoint[0] + diff_x * factor / 2,
            midpoint[1] + diff_y * factor / 2,
        ]

    return upper_body_pos, lower_body_pos

def check_snapping(limb_pos, snap_radius, last_snapped_shape):
    """Check if a limb should snap to a shape."""
    if last_snapped_shape and calculate_distance(limb_pos, last_snapped_shape) <= snap_radius:
        return last_snapped_shape, True
    return limb_pos, False

def unsnap_limb(limb_pos, last_snapped_shape):
    """Unsnap the limb if it's clicked and dragged away from the snapped shape."""
    if last_snapped_shape and calculate_distance(limb_pos, last_snapped_shape) > 0:
        return limb_pos, False
    return limb_pos, True
