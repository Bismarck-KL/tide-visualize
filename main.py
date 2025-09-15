import requests
from lxml import html
import numpy as np
import dotenv
import os
import pygame
import random
import time

# Load environment variables
dotenv.load_dotenv()

# Get the year and filename from the environment variables
year = int(os.getenv('YEAR', 2024))
filename = os.getenv('FILENAME', f"page-{year}.html")

# Fetch data
if not os.path.exists(filename):
    page = requests.get(os.getenv('URL')).text
    with open(filename, 'w', encoding='UTF8') as f:
        f.write(page)
else:
    with open(filename, 'r', encoding='UTF8') as f:
        page = f.read()

# Parse the page to HTML
tree = html.fromstring(page)
rows = tree.xpath(os.getenv('ROW_XPATH'))

data_list = []
for row in rows: 
    parts = row.text_content().split()
    if parts[0] != "Date" and len(parts) == 25:
        data_list.append([float(x) for x in parts])

# Convert the data_list to a 2D NumPy array
data_array = np.array(data_list)
# print("data_array:",data_array)


# Set up 
# Animation settings
clock = pygame.time.Clock()
running = True
current_hour = 0
total_hours = 24

current_date_index = 0
current_date = 0
current_month = 0
current_day = 0


# Initialize pygame
pygame.init()

# Font setup
title_font = pygame.font.Font(None, 34) 
tide_font = pygame.font.Font(None, 12) 

# Colors
black = (0, 0, 0)  # Black
white = (255, 255, 255) # White
blue = (135, 206, 235)  # Sky blue
night_black = (20, 20, 20)  # Night background


# Star Timing control
last_time = time.time()
hour_increment_interval = 0.1  # Interval in seconds for each hour
seconds_per_hour = hour_increment_interval  # Total seconds for each hour in the animation
frame_per_seconds = 60


def draw_ui():

    # Display the current hour in the left side of the screen
    hour_text = title_font.render(str(current_day) + "/" + str(current_month) + " - " + str(current_hour)+":00", True, black if day else white)
    text_rect = hour_text.get_rect(topleft = (20, 20))
    # Draw the border rectangle
    pygame.draw.rect(screen, black if day else white, text_rect.inflate(20, 10), 2)
    # Blit the text on top
    screen.blit(hour_text, text_rect)

    # Tide data
    tide_text = tide_font.render("Tide:"+str(data_array[current_date_index][current_hour+1]), True, black if day else white)
    tide_text_rect = tide_text.get_rect()
    tide_text_rect.centerx = width // 2  # Center horizontally
    tide_text_rect.bottom = height - 20  # Position bottom 50 pixels from the bottom
    pygame.draw.rect(screen, black if day else white, tide_text_rect.inflate(20, 10), 2)
    screen.blit(tide_text, tide_text_rect)

    # Speed
    speed_text = tide_font.render("Seconds/hour: {}".format(seconds_per_hour), True, black if day else white)
    speed_text_rect = speed_text.get_rect()
    speed_text_rect.topright = (width - 20, 20) 
    screen.blit(speed_text, speed_text_rect)


# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tide Visualize")

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Set the background color based on the time of day
    day = 6 < current_hour < 19
    screen.fill(blue if day else night_black)

    current_date = data_array[current_date_index]
    current_month = int(current_date[0] // 100)
    current_day = int(current_date[0] % 100)


    # Update display
    pygame.display.flip()

    # Increment hour if the interval has passed
    current_time = time.time()
    if current_time - last_time >= hour_increment_interval:
        current_hour += 1
        last_time = current_time  # Reset the timer
        # Reset current_hour after 24
    if current_hour >= total_hours:
        current_hour = 0
        if current_date_index < len(data_array):
            current_date_index+=1
        else:
            current_date_index=0


# Quit pygame
pygame.quit()