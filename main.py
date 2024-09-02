import pygame
import sys
import math
import json
import os
from climber_config import (HEAD_RADIUS, HEAD_COLOR, UPPER_BODY_RADIUS, LOWER_BODY_RADIUS,
                            BODY_COLOR, BODY_DISTANCE, HAND_RADIUS, HAND_COLOR, HAND_BODY_MAX_DISTANCE,
                            FEET_SIZE, FEET_COLOR, FEET_BODY_MAX_DISTANCE, BODY_STRING_COLOR, BODY_STRING_THICKNESS,
                            ARM_STRING_COLOR, ARM_STRING_THICKNESS, LEG_STRING_COLOR, LEG_STRING_THICKNESS)
from board_config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, BACKGROUND_IMAGE_PATH

# Load board state from JSON
STATE_FILE = "board_state.json"


def load_board_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None

# Class to represent a limb


class Limb:
    def __init__(self, start_pos, color, radius, max_distance, string_color, string_thickness, shape="circle"):
        self.pos = start_pos
        self.color = color
        self.radius = radius
        self.max_distance = max_distance
        self.string_color = string_color
        self.string_thickness = string_thickness
        self.shape = shape
        self.gravity_on = False

    def draw(self, screen, body_pos):
        pygame.draw.line(screen, self.string_color, self.pos,
                         body_pos, self.string_thickness)
        if self.shape == "circle":
            pygame.draw.circle(screen, self.color, (int(
                self.pos[0]), int(self.pos[1])), self.radius)
        elif self.shape == "square":
            pygame.draw.rect(screen, self.color, (
                self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2, self.radius * 2))

    def toggle_gravity(self):
        self.gravity_on = not self.gravity_on

    def apply_gravity(self, body_pos):
        if self.gravity_on:
            # Move the limb downward naturally
            desired_y = body_pos[1] + (self.max_distance / 2)
            if self.pos[1] < desired_y:
                self.pos[1] += 5  # Move the limb downwards in small steps
                if self.pos[1] > desired_y:
                    self.pos[1] = desired_y

    def drag(self, mouse_pos, body_pos, other_limbs):
        if self.is_near(mouse_pos) and not self.overlaps_with_other_limbs(mouse_pos, other_limbs):
            self.pos = list(mouse_pos)
            body_pos = self.move_body_smoothly(body_pos)
        return body_pos

    def is_near(self, mouse_pos):
        return calculate_distance(self.pos, mouse_pos) < self.radius

    def overlaps_with_other_limbs(self, mouse_pos, other_limbs):
        for limb in other_limbs:
            if calculate_distance(mouse_pos, limb.pos) < self.radius + limb.radius:
                return True
        return False

    def move_body_smoothly(self, body_pos):
        limb_to_body_dist = calculate_distance(self.pos, body_pos)
        if limb_to_body_dist > self.max_distance / 2:
            diff_x = self.pos[0] - body_pos[0]
            diff_y = self.pos[1] - body_pos[1]
            factor = (limb_to_body_dist - self.max_distance / 2) / \
                limb_to_body_dist

            body_pos[0] += diff_x * factor
            body_pos[1] += diff_y * factor

        return body_pos

    def constrain(self, body_pos):
        limb_to_body_dist = calculate_distance(self.pos, body_pos)
        if limb_to_body_dist > self.max_distance / 2:
            diff_x = self.pos[0] - body_pos[0]
            diff_y = self.pos[1] - body_pos[1]
            factor = (limb_to_body_dist - self.max_distance / 2) / \
                limb_to_body_dist

            self.pos[0] = body_pos[0] + diff_x * (1 - factor)
            self.pos[1] = body_pos[1] + diff_y * (1 - factor)

        return self.pos

# Function to calculate the distance between two points


def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

# Function to keep the upper and lower body circles connected with a fixed distance


def maintain_body_connection(upper_body_pos, lower_body_pos, body_distance):
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


# Initialize pygame
pygame.init()

# Load board state
board_state = load_board_state()

if board_state:
    num_rows = board_state['num_rows']
    circles = board_state['circles']
    squares = board_state['squares']
else:
    # Default settings if no state is saved
    num_rows = 8
    circles = []
    squares = []

# Set up the screen
ROW_HEIGHT = SCREEN_HEIGHT // num_rows
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Climbing Game")

# Load and fit the background image if provided
background_image = None
if BACKGROUND_IMAGE_PATH:
    background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background_image = pygame.transform.scale(
        background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Initial positions of the climber
upper_body_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - BODY_DISTANCE // 2]
lower_body_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + BODY_DISTANCE // 2]
head_pos = [upper_body_pos[0], upper_body_pos[1] -
            UPPER_BODY_RADIUS - HEAD_RADIUS]

# Lower body gravity toggle
lower_body_gravity_on = False

# Define initial positions for limbs
left_arm_pos = [upper_body_pos[0] - 50, upper_body_pos[1] - 50]
right_arm_pos = [upper_body_pos[0] + 50, upper_body_pos[1] - 50]
left_leg_pos = [lower_body_pos[0] - 50, lower_body_pos[1] + 50]
right_leg_pos = [lower_body_pos[0] + 50, lower_body_pos[1] + 50]

# Create Limb instances for each arm and leg
left_arm = Limb(left_arm_pos, HAND_COLOR, HAND_RADIUS, HAND_BODY_MAX_DISTANCE,
                ARM_STRING_COLOR, ARM_STRING_THICKNESS, "circle")
right_arm = Limb(right_arm_pos, HAND_COLOR, HAND_RADIUS,
                 HAND_BODY_MAX_DISTANCE, ARM_STRING_COLOR, ARM_STRING_THICKNESS, "circle")
left_leg = Limb(left_leg_pos, FEET_COLOR, FEET_SIZE // 2,
                FEET_BODY_MAX_DISTANCE, LEG_STRING_COLOR, LEG_STRING_THICKNESS, "square")
right_leg = Limb(right_leg_pos, FEET_COLOR, FEET_SIZE // 2,
                 FEET_BODY_MAX_DISTANCE, LEG_STRING_COLOR, LEG_STRING_THICKNESS, "square")

# Store all limbs in a list for easier management
all_limbs = [left_arm, right_arm, left_leg, right_leg]

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 3:  # Right-click toggles gravity
                for limb in all_limbs:
                    if limb.is_near(mouse_pos):
                        limb.toggle_gravity()
                if calculate_distance(mouse_pos, lower_body_pos) < LOWER_BODY_RADIUS:
                    lower_body_gravity_on = not lower_body_gravity_on

    # Handle dragging of limbs and body
    mouse_pressed = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if mouse_pressed[0]:  # Left mouse button is pressed
        upper_body_pos = left_arm.drag(mouse_pos, upper_body_pos, [
                                       right_arm, left_leg, right_leg])
        upper_body_pos = right_arm.drag(mouse_pos, upper_body_pos, [
                                        left_arm, left_leg, right_leg])
        lower_body_pos = left_leg.drag(mouse_pos, lower_body_pos, [
                                       left_arm, right_arm, right_leg])
        lower_body_pos = right_leg.drag(mouse_pos, lower_body_pos, [
                                        left_arm, right_arm, left_leg])

    # Apply gravity to each limb
    for limb in all_limbs:
        if limb.shape == "circle":
            limb.apply_gravity(upper_body_pos)
        else:
            limb.apply_gravity(lower_body_pos)

    # Apply gravity to the lower body if toggled
    if lower_body_gravity_on:
        desired_y = upper_body_pos[1] + BODY_DISTANCE
        if lower_body_pos[1] < desired_y:
            lower_body_pos[1] += 5
            if lower_body_pos[1] > desired_y:
                lower_body_pos[1] = desired_y

    # Constrain limb positions with smooth movement
    left_arm.constrain(upper_body_pos)
    right_arm.constrain(upper_body_pos)
    left_leg.constrain(lower_body_pos)
    right_leg.constrain(lower_body_pos)

    # Maintain the fixed distance between upper and lower body
    upper_body_pos, lower_body_pos = maintain_body_connection(
        upper_body_pos, lower_body_pos, BODY_DISTANCE)

    # Update head position based on upper body movement
    head_pos = [upper_body_pos[0], upper_body_pos[1] -
                UPPER_BODY_RADIUS - HEAD_RADIUS]

    # Drawing
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(BACKGROUND_COLOR)

    # Draw rows
    for i in range(1, num_rows):
        pygame.draw.line(screen, (200, 200, 200), (0, i *
                         ROW_HEIGHT), (SCREEN_WIDTH, i * ROW_HEIGHT), 2)

    # Draw circles (as outlines)
    for pos in circles:
        pygame.draw.circle(screen, (0, 0, 255), pos, 10, 2)

    # Draw squares (as outlines)
    for pos in squares:
        pygame.draw.rect(screen, (128, 0, 128),
                         (pos[0] - 10, pos[1] - 10, 20, 20), 2)

    # Draw the line connecting upper and lower body
    pygame.draw.line(screen, BODY_STRING_COLOR, upper_body_pos,
                     lower_body_pos, BODY_STRING_THICKNESS)

    # Draw the upper and lower body
    pygame.draw.circle(screen, BODY_COLOR, (int(
        upper_body_pos[0]), int(upper_body_pos[1])), UPPER_BODY_RADIUS)
    pygame.draw.circle(screen, BODY_COLOR, (int(
        lower_body_pos[0]), int(lower_body_pos[1])), LOWER_BODY_RADIUS)

    # Draw the limbs connecting to the body
    left_arm.draw(screen, upper_body_pos)
    right_arm.draw(screen, upper_body_pos)
    left_leg.draw(screen, lower_body_pos)
    right_leg.draw(screen, lower_body_pos)

    # Draw the head
    pygame.draw.circle(screen, HEAD_COLOR, (int(
        head_pos[0]), int(head_pos[1])), HEAD_RADIUS)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
