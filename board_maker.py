import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Board Creator")

# Colors
BACKGROUND_COLOR = (255, 255, 255)
LINE_COLOR = (200, 200, 200)
CIRCLE_COLOR = (173, 216, 230)  # Light blue
SQUARE_COLOR = (216, 191, 216)  # Light purple
BUTTON_COLOR = (0, 200, 0)  # Green
BUTTON_TEXT_COLOR = (255, 255, 255)

# Shape properties
CIRCLE_RADIUS = 10
SQUARE_SIZE = 20

# Rows properties
NUM_ROWS = 6
ROW_HEIGHT = SCREEN_HEIGHT // NUM_ROWS

# Button properties
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_POS = (SCREEN_WIDTH - BUTTON_WIDTH - 10,
              SCREEN_HEIGHT - BUTTON_HEIGHT - 10)

# Create shapes
circles = [{'pos': [50 + i * 50, 100 + i * 50]} for i in range(10)]
squares = [{'pos': [300 + i * 50, 150 + i * 50]} for i in range(10)]


def draw_button(screen, text, position, size):
    pygame.draw.rect(screen, BUTTON_COLOR, (*position, *size))
    font = pygame.font.SysFont(None, 36)
    text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(
        center=(position[0] + size[0] // 2, position[1] + size[1] // 2))
    screen.blit(text_surf, text_rect)


def save_board_as_image(screen, filename):
    pygame.image.save(screen, filename)


def main():
    dragging_shape = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check if the user clicked on a circle
                for circle in circles:
                    dist = ((circle['pos'][0] - mouse_pos[0]) ** 2 +
                            (circle['pos'][1] - mouse_pos[1]) ** 2) ** 0.5
                    if dist < CIRCLE_RADIUS:
                        dragging_shape = circle
                        break

                # Check if the user clicked on a square
                for square in squares:
                    if (square['pos'][0] - SQUARE_SIZE // 2 <= mouse_pos[0] <= square['pos'][0] + SQUARE_SIZE // 2 and
                            square['pos'][1] - SQUARE_SIZE // 2 <= mouse_pos[1] <= square['pos'][1] + SQUARE_SIZE // 2):
                        dragging_shape = square
                        break

                # Check if the user clicked the save button
                if (BUTTON_POS[0] <= mouse_pos[0] <= BUTTON_POS[0] + BUTTON_WIDTH and
                        BUTTON_POS[1] <= mouse_pos[1] <= BUTTON_POS[1] + BUTTON_HEIGHT):
                    save_board_as_image(screen, "board.jpg")
                    print("Board saved as board.jpg")

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_shape = None

            elif event.type == pygame.MOUSEMOTION and dragging_shape:
                dragging_shape['pos'] = list(event.pos)

        # Drawing
        screen.fill(BACKGROUND_COLOR)

        # Draw rows
        for i in range(1, NUM_ROWS):
            pygame.draw.line(screen, LINE_COLOR, (0, i * ROW_HEIGHT),
                             (SCREEN_WIDTH, i * ROW_HEIGHT), 2)

        # Draw circles
        for circle in circles:
            pygame.draw.circle(screen, CIRCLE_COLOR,
                               circle['pos'], CIRCLE_RADIUS)

        # Draw squares
        for square in squares:
            pygame.draw.rect(screen, SQUARE_COLOR,
                             (square['pos'][0] - SQUARE_SIZE // 2, square['pos'][1] - SQUARE_SIZE // 2,
                              SQUARE_SIZE, SQUARE_SIZE))

        # Draw save button
        draw_button(screen, "Save", BUTTON_POS, (BUTTON_WIDTH, BUTTON_HEIGHT))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
