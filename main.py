import pygame
import sys
import math
from climber_config import (HEAD_RADIUS, HEAD_COLOR, UPPER_BODY_RADIUS, LOWER_BODY_RADIUS,
                            BODY_COLOR, BODY_DISTANCE, HAND_RADIUS, HAND_COLOR, HAND_BODY_MAX_DISTANCE,
                            FEET_SIZE, FEET_COLOR, FEET_BODY_MAX_DISTANCE, BODY_STRING_COLOR, BODY_STRING_THICKNESS,
                            ARM_STRING_COLOR, ARM_STRING_THICKNESS, LEG_STRING_COLOR, LEG_STRING_THICKNESS)
from board_config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, BACKGROUND_IMAGE_PATH

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ragdoll Mockup")

# Load and fit the background image if provided
background_image = None
if BACKGROUND_IMAGE_PATH:
    background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background_image = pygame.transform.scale(
        background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Initial positions
upper_body_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - BODY_DISTANCE // 2]
lower_body_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + BODY_DISTANCE // 2]
head_pos = [upper_body_pos[0], upper_body_pos[1] -
            UPPER_BODY_RADIUS - HEAD_RADIUS]

left_arm_pos = [upper_body_pos[0] - 50, upper_body_pos[1] - 50]
right_arm_pos = [upper_body_pos[0] + 50, upper_body_pos[1] - 50]
left_leg_pos = [lower_body_pos[0] - 50, lower_body_pos[1] + 50]
right_leg_pos = [lower_body_pos[0] + 50, lower_body_pos[1] + 50]

# Function to calculate the distance between two points


def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

# Function to smoothly move the body based on limb movement


def move_body_smoothly(limb_pos, body_pos, max_distance):
    limb_to_body_dist = calculate_distance(limb_pos, body_pos)

    if limb_to_body_dist > max_distance / 2:
        diff_x = limb_pos[0] - body_pos[0]
        diff_y = limb_pos[1] - body_pos[1]
        factor = (limb_to_body_dist - max_distance / 2) / limb_to_body_dist

        body_pos[0] += diff_x * factor
        body_pos[1] += diff_y * factor

    return body_pos

# Function to handle dragging and constraints with smooth movement


def drag_and_constrain_smoothly(limb_pos, body_pos, max_distance):
    limb_to_body_dist = calculate_distance(limb_pos, body_pos)

    if limb_to_body_dist > max_distance / 2:
        diff_x = limb_pos[0] - body_pos[0]
        diff_y = limb_pos[1] - body_pos[1]
        factor = (limb_to_body_dist - max_distance / 2) / limb_to_body_dist

        limb_pos[0] = body_pos[0] + diff_x * (1 - factor)
        limb_pos[1] = body_pos[1] + diff_y * (1 - factor)

    return limb_pos

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


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle dragging of limbs and body
    mouse_pressed = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if mouse_pressed[0]:  # Left mouse button is pressed
        if calculate_distance(mouse_pos, left_arm_pos) < HAND_RADIUS:
            left_arm_pos = list(mouse_pos)
            upper_body_pos = move_body_smoothly(
                left_arm_pos, upper_body_pos, HAND_BODY_MAX_DISTANCE)
        elif calculate_distance(mouse_pos, right_arm_pos) < HAND_RADIUS:
            right_arm_pos = list(mouse_pos)
            upper_body_pos = move_body_smoothly(
                right_arm_pos, upper_body_pos, HAND_BODY_MAX_DISTANCE)
        elif calculate_distance(mouse_pos, left_leg_pos) < FEET_SIZE:
            left_leg_pos = list(mouse_pos)
            lower_body_pos = move_body_smoothly(
                left_leg_pos, lower_body_pos, FEET_BODY_MAX_DISTANCE)
        elif calculate_distance(mouse_pos, right_leg_pos) < FEET_SIZE:
            right_leg_pos = list(mouse_pos)
            lower_body_pos = move_body_smoothly(
                right_leg_pos, lower_body_pos, FEET_BODY_MAX_DISTANCE)
        elif calculate_distance(mouse_pos, upper_body_pos) < UPPER_BODY_RADIUS:
            upper_body_pos = list(mouse_pos)
        elif calculate_distance(mouse_pos, lower_body_pos) < LOWER_BODY_RADIUS:
            lower_body_pos = list(mouse_pos)

    # Constrain limb positions with smooth movement
    left_arm_pos = drag_and_constrain_smoothly(
        left_arm_pos, upper_body_pos, HAND_BODY_MAX_DISTANCE)
    right_arm_pos = drag_and_constrain_smoothly(
        right_arm_pos, upper_body_pos, HAND_BODY_MAX_DISTANCE)
    left_leg_pos = drag_and_constrain_smoothly(
        left_leg_pos, lower_body_pos, FEET_BODY_MAX_DISTANCE)
    right_leg_pos = drag_and_constrain_smoothly(
        right_leg_pos, lower_body_pos, FEET_BODY_MAX_DISTANCE)

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

    # Draw the line connecting upper and lower body
    pygame.draw.line(screen, BODY_STRING_COLOR, upper_body_pos,
                     lower_body_pos, BODY_STRING_THICKNESS)

    # Draw the upper and lower body
    pygame.draw.circle(screen, BODY_COLOR, (int(
        upper_body_pos[0]), int(upper_body_pos[1])), UPPER_BODY_RADIUS)
    pygame.draw.circle(screen, BODY_COLOR, (int(
        lower_body_pos[0]), int(lower_body_pos[1])), LOWER_BODY_RADIUS)

    # Draw the limbs connecting to the body
    pygame.draw.line(screen, ARM_STRING_COLOR, left_arm_pos,
                     upper_body_pos, ARM_STRING_THICKNESS)
    pygame.draw.line(screen, ARM_STRING_COLOR, right_arm_pos,
                     upper_body_pos, ARM_STRING_THICKNESS)
    pygame.draw.line(screen, LEG_STRING_COLOR, left_leg_pos,
                     lower_body_pos, LEG_STRING_THICKNESS)
    pygame.draw.line(screen, LEG_STRING_COLOR, right_leg_pos,
                     lower_body_pos, LEG_STRING_THICKNESS)

    # Draw the limbs
    pygame.draw.circle(screen, HAND_COLOR, (int(
        left_arm_pos[0]), int(left_arm_pos[1])), HAND_RADIUS)
    pygame.draw.circle(screen, HAND_COLOR, (int(
        right_arm_pos[0]), int(right_arm_pos[1])), HAND_RADIUS)
    pygame.draw.rect(screen, FEET_COLOR, (
        left_leg_pos[0] - FEET_SIZE // 2, left_leg_pos[1] - FEET_SIZE // 2, FEET_SIZE, FEET_SIZE))
    pygame.draw.rect(screen, FEET_COLOR, (
        right_leg_pos[0] - FEET_SIZE // 2, right_leg_pos[1] - FEET_SIZE // 2, FEET_SIZE, FEET_SIZE))

    # Draw the head
    pygame.draw.circle(screen, HEAD_COLOR, (int(
        head_pos[0]), int(head_pos[1])), HEAD_RADIUS)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
