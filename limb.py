import pygame
import math
from ragdoll import (calculate_distance, move_body_smoothly,
                     drag_and_constrain_smoothly, check_snapping, unsnap_limb)
from climber_config import HAND_RADIUS, FEET_SIZE


class Limb:
    def __init__(self, name, initial_pos, max_distance, snap_radius, color, string_color, string_thickness):
        self.name = name
        self.position = initial_pos
        self.snapped = False
        self.snapped_shape = None
        self.max_distance = max_distance
        self.snap_radius = snap_radius
        self.color = color
        self.string_color = string_color
        self.string_thickness = string_thickness

    def move(self, new_pos, body_pos):
        """Move the limb, checking for snapping."""
        self.position = list(new_pos)
        body_pos = move_body_smoothly(
            self.position, body_pos, self.max_distance)
        self.position, snapped = check_snapping(
            self.position, self.snap_radius, self.snapped_shape)
        if snapped:
            self.snapped = True
            self.snapped_shape = self.position
        return body_pos

    def unsnap(self, mouse_pos):
        """Unsnap the limb when it's clicked and dragged."""
        self.position, self.snapped = unsnap_limb(
            mouse_pos, self.snapped_shape)
        if not self.snapped:
            self.snapped_shape = None

    def check_unsnap(self):
        """Check if the limb needs to be unsnapped due to movement."""
        if self.snapped and self.snapped_shape is not None:
            self.snapped = calculate_distance(
                self.position, self.snapped_shape) <= self.snap_radius
            if not self.snapped:
                self.snapped_shape = None

    def constrain_position(self, body_pos):
        """Constrain the limb's position if it's not snapped."""
        if not self.snapped:
            self.position = drag_and_constrain_smoothly(
                self.position, body_pos, self.max_distance)

    def draw(self, screen, body_pos):
        """Draw the limb and its connecting string."""
        # Draw the line connecting the limb to the body
        pygame.draw.line(screen, self.string_color,
                         self.position, body_pos, self.string_thickness)
        # Draw the limb itself (circle for arms, square for legs)
        if self.name in ['left_arm', 'right_arm']:
            pygame.draw.circle(screen, self.color, (int(
                self.position[0]), int(self.position[1])), HAND_RADIUS)
        elif self.name in ['left_leg', 'right_leg']:
            pygame.draw.rect(screen, self.color, (
                self.position[0] - FEET_SIZE // 2, self.position[1] - FEET_SIZE // 2, FEET_SIZE, FEET_SIZE))
