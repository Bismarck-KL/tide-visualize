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

# music settings
bgm_volume = 0.2


# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tide Visualize")

# Initialize pygame
pygame.init()

# Initialize loading screen
from loading_screen import LoadingScreen
loading = LoadingScreen(width, height)
loading.show_message("Initializing audio system...")
# init mixer
pygame.mixer.init()
# Set up music
bgmfilename = os.getenv('FILENAME', "assets/sfx/bgm.mp3")
envfilename = os.getenv('FILENAME', "assets/sfx/wave_env.mp3")

try:
    loading.show_message("Loading music files...")
    pygame.mixer.music.load(bgmfilename)
    pygame.mixer.music.set_volume(bgm_volume)
    pygame.mixer.music.play(loops=-1)  # Loop
except pygame.error as e:
    print(f"Error loading music file: {e}")

try:
    loading.show_message("Loading environment sound files...")
    env_sound = pygame.mixer.Sound(envfilename)  # Create Sound object
    env_sound.set_volume(bgm_volume)
    env_sound.play(loops=-1)
except pygame.error as e:
    print(f"Error loading sound file: {e}")

    
show_ui = True

# Font setup
title_font = pygame.font.Font(None, 34) 
tide_font = pygame.font.Font(None, 12) 

# Colors
black = (0, 0, 0)  # Black
white = (255, 255, 255) # White
blue = (135, 206, 235)  # Sky blue
night_black = (20, 20, 20)  # Night background
sun_color = (255, 128, 0)  # Sun color
moon_color = (200, 200, 100)  # Moon color
sand_color = (194, 178, 128)  # Sandy color
grain_color = (255, 228, 196)  # Light beige for grains of sand
wave_color = (0, 105, 148)    # Dark blue for the waves

# Text
border_color = (255, 255, 255)


# Star Timing control
last_time = time.time()
hour_increment_interval = 0.1  # Interval in seconds for each hour
seconds_per_hour = hour_increment_interval  # Total seconds for each hour in the animation
frame_per_seconds = 60
move_speed = (width / 12) / (seconds_per_hour * (frame_per_seconds / 1))  # Speed calculation


# Fade settings
fade_duration = 1000  # Duration of the fade in milliseconds
fade_steps = frame_per_seconds/2  
fade_step_time = fade_duration 
fade_in_progress = False  # Flag to track fade progress
fade_alpha = 0  # Current fade level (0 to 1)
start_color = None
end_color = None

def draw_background():

    global fade_in_progress, fade_alpha, current_color, start_color, end_color

    # Start a fade if the target color changes
    if not fade_in_progress and (start_color is None or target_color != start_color):
        start_color = current_color  # Current color is where we are starting
        end_color = target_color
        fade_alpha = 0  # Reset alpha for new fade
        fade_in_progress = True

    # Handle the fading process
    if fade_in_progress:
        fade_alpha += 1 / fade_steps  # Increment alpha
        if fade_alpha >= 1:  # Fade is complete
            fade_alpha = 1
            fade_in_progress = False  # Stop fading
            current_color = end_color  # Update current color to target

    # Fill the screen with the interpolated color
    fill_color = interpolate_color(start_color, end_color, fade_alpha)
    screen.fill(fill_color)

# Function to fade between two colors
def interpolate_color(color1, color2, alpha):
    return (
        int(color1[0] + (color2[0] - color1[0]) * alpha),
        int(color1[1] + (color2[1] - color1[1]) * alpha),
        int(color1[2] + (color2[2] - color1[2]) * alpha)
    )

# Initialize Star positions
starPositionY = height / 4
sun_x = 0.0
moon_x = width / 2  # Start the moon in the middle of the screen

def draw_sun():
    global sun_x

    # Calculate sun position
    if 6 <= current_hour <= 18:
        sunTargetX = (width / 12) * (current_hour - 6)  # Move from 0 to width
        sun_y = starPositionY
    else:
        sun_x, sunTargetX, sun_y = -100, -100, -100  # Offscreen

    # Smoothly increment sun_x towards sunTargetX
    if sun_x < sunTargetX:
        sun_x += move_speed  # Adjust speed for smooth movement

    # Draw sun if it's visible
    if 6 < current_hour <= 18:
        pygame.draw.circle(screen, sun_color, (int(sun_x), int(sun_y)), 30)

def draw_moon():
    global moon_x

    # Calculate moon position
    if current_hour >= 18:
        moonTargetX = (width / 12) * (current_hour - 18)  # Move from center to left
        moon_y = starPositionY
    elif current_hour <= 6:
        moonTargetX = width / 2 + (width / 12) * current_hour  # Move right from center
        moon_y = starPositionY
    else:
        moon_x, moon_y,moonTargetX = 0, -100,-100  # Offscreen

    # Smoothly increment moon_x towards moonTargetX
    if 18 < current_hour < 24 or 0 <= current_hour < 7:
        if moon_x < moonTargetX:
            moon_x += move_speed  # Adjust speed for smooth movement
        # pygame.draw.circle(screen, moon_color, (int(moon_x), int(moon_y)), 30)

        # Create a surface for the moon
        moon_surface = pygame.Surface((60, 60), pygame.SRCALPHA)  # Create a transparent surface
        pygame.draw.circle(moon_surface, moon_color, (30, 30), 30)  # Draw full moon
        pygame.draw.rect(moon_surface, (0, 0, 0, 0), (0, 0, 30, 60))  # Cover half with transparency

        # Blit the moon surface onto the main screen
        screen.blit(moon_surface, (moon_x - 30, moon_y - 30))  # Adjust position

# Create water particles within the sea area
water_particles = [(random.randint(0, width), random.randint(height // 2, height // 2 + 100)) for _ in range(20)]  # Example init
#  Sea control
sea_current_height = 0  # Start at the midpoint
sea_target_height = height / 2  # Initial target
sea_move_speed = (height / 2 / 10) / (seconds_per_hour * frame_per_seconds * 2) 

def draw_sea():

    global sea_current_height, sea_target_height
    # Calculate sea target height based on data
    sea_target_height = height / 7 * (data_array[current_date_index][current_hour + 1] / 2)
    # print(f"sea_current_height: {sea_current_height}/{sea_target_height}")

    # Smoothly update current sea height
    if sea_current_height < sea_target_height:
        sea_current_height += sea_move_speed
        if sea_current_height > sea_target_height:  # Prevent overshooting
            sea_current_height = sea_target_height
    elif sea_current_height > sea_target_height:
        sea_current_height -= sea_move_speed
        if sea_current_height < sea_target_height:  # Prevent overshooting
            sea_current_height = sea_target_height


    # Draw the sea (filled rectangle)
    pygame.draw.rect(screen, wave_color, (0, height / 2, width, sea_current_height))

    # Draw waves
    for x in range(0, width, 20):
        pygame.draw.arc(screen, white, 
                        (x, height / 2 + sea_current_height - 30, 40, 40), 
                        3.14, 0, 5) 

    # Update particle positions for slow movement
    for i, (x, y) in enumerate(water_particles):
        y += random.choice([-0.5, 0.5])  # Move slowly up or down
        # Keep particles within the sea height
        if y < (height / 2 + 5):
            y = (height / 2 + 5)
        elif y > height / 2 + sea_current_height:
            y = height / 2 + sea_current_height
        water_particles[i] = (x, y)

    # Draw particles
    for x, y in water_particles:
        pygame.draw.circle(screen, grain_color, (x, int(y)), random.randint(1, 3))

def draw_beach():
    # Draw the sand
    pygame.draw.rect(screen, sand_color, (0, height / 2, width, height / 3 * 2))

seagull_x = 0
seagull_y = height // 6
flap_direction = 1  # 1 for moving up, -1 for moving down
flap_speed = 1      # Speed of flapping
show_seagull = False


def draw_seagulls():

    global seagull_x
    global seagull_y
    global flap_direction
    global flap_speed
    global show_seagull

    # Inside your main loop, update the seagull position
    seagull_x += (2*(4-seconds_per_hour))  # Move the seagull across the screen
    seagull_y += (flap_direction * flap_speed)*(4-seconds_per_hour)  # Move up or down

    # Change flap direction at certain heights
    if seagull_y >= height // 6 + 10:  # Maximum height
        flap_direction = -1
    elif seagull_y <= height // 6 - 10:  # Minimum height
        flap_direction = 1

    # Draw the seagull (simple representation)
    pygame.draw.polygon(screen, (255, 255, 255), [(seagull_x, seagull_y), (seagull_x + 10, seagull_y + 5), (seagull_x + 20, seagull_y)])
    pygame.draw.polygon(screen, (255, 255, 255), [(seagull_x + 10, seagull_y), (seagull_x + 20, seagull_y + 5), (seagull_x + 30, seagull_y)])

    # Reset when it goes off screen
    if seagull_x > width:
        seagull_x = 0
        seagull_y = height // 6  # Reset to initial height
        show_seagull = False

# Store stars as a list of (x, y, radius, color)
stars = []
def user_intereactive_input(button):

    global show_ui 

    mouse_x, mouse_y = pygame.mouse.get_pos()

    if button == 1:  # Left click
        if height / 2 <= mouse_y <= height / 2 + height / 3 * 2:
            # Create a star at the mouse position
            star_radius = random.randint(2, 5)
            lifespan = random.randint(30, 3000)
            star_color = (255, 255, random.randint(180, 255))  # Slightly yellowish white
            stars.append((mouse_x, mouse_y, star_radius, star_color, lifespan))
            # print(f"Star created at ({mouse_x}, {mouse_y}) with radius {star_radius}")
    elif button == 3:
        capture_screenshot_without_ui()

def capture_screenshot_without_ui():


    # Create screenshot directory if it doesn't exist
    screenshot_dir = "screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    
    # Generate filename with current date and time
    current_time = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{current_time}.png")
    
    # Save the screenshot
    pygame.image.save(screen, screenshot_path)

def draw_ui():

    # Display the current hour in the left side of the screen
    hour_text  = title_font.render(f"{current_day:02}/{current_month:02} - {current_hour}:00", True, black if day else white)
    text_rect = hour_text.get_rect(topleft = (20, 20))
    # Draw the border rectangle
    pygame.draw.rect(screen, black if day else white, text_rect.inflate(20, 10), 2)
    # Blit the text on top
    screen.blit(hour_text, text_rect)

    # Tide data
    tide_text = tide_font.render("Tide:"+str(data_array[current_date_index][current_hour+1]), True, black)
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

def user_input(key):

    global hour_increment_interval
    global seconds_per_hour
    global move_speed
    global sea_move_speed
    global bgm_volume
    global show_ui

    if key == pygame.K_RIGHT:
        if hour_increment_interval < 3:
            hour_increment_interval+=1
            if hour_increment_interval >=3:
                hour_increment_interval = 3
            seconds_per_hour = hour_increment_interval
    elif key == pygame.K_LEFT:
        if hour_increment_interval > 0:
            hour_increment_interval-=1
            if hour_increment_interval<=0:
                hour_increment_interval = 0.1
            seconds_per_hour = hour_increment_interval
    elif key == pygame.K_u:
            show_ui = not show_ui
    elif key == pygame.K_i:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause() 
        else:
            pygame.mixer.music.unpause() 

    move_speed = (width / 12) / (seconds_per_hour * (frame_per_seconds / 1)) 
    sea_move_speed = (height / 2 / 10) / (seconds_per_hour * frame_per_seconds * 2) 

    # Control volume    
    if key == pygame.K_UP:
        if bgm_volume < 1.0:
            bgm_volume += 0.1
            if bgm_volume >= 1.0:
                bgm_volume = 1.0
    elif key == pygame.K_DOWN:
        if bgm_volume > 0.0:
            bgm_volume -= 0.1
            if bgm_volume <= 0.0:
                bgm_volume = 0.0

    pygame.mixer.music.set_volume(bgm_volume)
    env_sound.set_volume(bgm_volume)
         

current_color = blue  # Start with the day color
target_color = blue   # Initial target color


# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.KEYUP:
            user_input(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            user_intereactive_input(event.button)

    # Set the background color based on the time of day
    day = 6 < current_hour < 19
    # screen.fill(blue if day else night_black)
    target_color = blue if day else night_black

    draw_background()


    current_date = data_array[current_date_index]
    current_month = int(current_date[0] // 100)
    current_day = int(current_date[0] % 100)


    # Draw the elements
    draw_sun()
    draw_moon()

    draw_beach()

    # Update and draw stars
    for i in range(len(stars)):
        x, y, radius, color, lifespan = stars[i]
        lifespan -= 1  # Decrement lifespan
        
        if lifespan > 0:
            stars[i] = (x, y, radius, color, lifespan)  # Update star with new lifespan
        else:
            stars[i] = None  # Mark for removal

    # Remove None values (stars that have expired)
    stars = [star for star in stars if star is not None]

    # Draw remaining stars
    for star in stars:
        pygame.draw.circle(screen, star[3], (star[0], star[1]), star[2])

    draw_sea()

    if show_seagull:
        draw_seagulls()

    # Draw UI
    if show_ui:
        draw_ui()


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
            if (random.randint(0, 10)) <= 3:
                if not show_seagull:
                    show_seagull = True
        else:
            current_date_index=0

    # Frame rate
    clock.tick(frame_per_seconds) 

# Stop the music/env sound and Quit Pygame 
pygame.mixer.music.stop()
env_sound.stop()
pygame.mixer.quit()
pygame.quit()