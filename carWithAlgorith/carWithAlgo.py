import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
CAR_WIDTH = 24
CAR_HEIGHT = 24
TRAFIC_LIGHT_WIDTH = 30
TRAFIC_LIGHT_HEIGHT = 30
TRAFFIC_LIGHTS = {'red':5, 'yellow':13, 'green':20}
current_time = pygame.time.get_ticks()
last_traffic_light_change = current_time

def get_pixel_color(x, y):
    return background_image.get_at((x,y))


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background_image = pygame.image.load('putCartoon.jpg')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

road_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

# getting the color of the rode
pixel_array = pygame.PixelArray(background_image)
for x in range(SCREEN_WIDTH):
    for y in range(SCREEN_HEIGHT):
        pixel_color = get_pixel_color(x, y)
        color_threshold = 5
        if all(abs(a - b) <= color_threshold for a, b in zip(pixel_color, (113,116,123))):
            road_surface.set_at((x, y), (113, 116, 123, 255))

pixel_array.close()

car = pygame.image.load('carCartoon.png')
car = pygame.transform.scale(car, (CAR_WIDTH, CAR_HEIGHT))
car_x, car_y = SCREEN_WIDTH - (CAR_WIDTH + 15), SCREEN_HEIGHT - CAR_HEIGHT
car_speed = 0.3

trafic_lights = pygame.image.load("semafor.png")
trafic_lights = pygame.transform.scale(trafic_lights, (TRAFIC_LIGHT_WIDTH, TRAFIC_LIGHT_HEIGHT))
trafic_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
trafic_lights_dict = {
    1: (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 165),
    2: (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 300),
    3: (SCREEN_WIDTH - 230, SCREEN_HEIGHT - 165),
    4: (SCREEN_WIDTH - 460, SCREEN_HEIGHT - 165),
    5: (SCREEN_WIDTH - 600, SCREEN_HEIGHT - 300),
    6: (SCREEN_WIDTH - 530, SCREEN_HEIGHT - 340), 
    7: (SCREEN_WIDTH - 170, SCREEN_HEIGHT - 350)
}

road_mask = pygame.mask.from_surface(road_surface)
car_mask = pygame.mask.from_surface(car)



# A* algo on the road edges
def find_path(start, end, road_mask):
    open_set = [start]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: distance(start, end)}

    while open_set:
        current = min(open_set, key=lambda x: f_score[x])
        open_set.remove(current)

        if current == end:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, road_mask):
            tentative_g_score = g_score[current] + distance(current, neighbor)
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + distance(neighbor, end)
                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None

# distance to the clicked position
def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)

# creating a path
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current)
    return path

# next points on the road
def get_neighbors(point, road_mask):
    x, y = point
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            neighbor_x = x + dx
            neighbor_y = y + dy
            if 0 <= neighbor_x < SCREEN_WIDTH and 0 <= neighbor_y < SCREEN_HEIGHT:
                if road_mask.get_at((neighbor_x, neighbor_y)):
                    neighbors.append((neighbor_x, neighbor_y))
    return neighbors

path = None
running = True
clicked_position = None
enter_pressed = False
while running:
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_position = event.pos

        if keys[pygame.K_RETURN] and clicked_position is not None:
            enter_pressed = True
        if keys[pygame.K_r]:
            # Resetovanje automobila na početnu poziciju
            car_x, car_y = SCREEN_WIDTH - (CAR_WIDTH + 15), SCREEN_HEIGHT - CAR_HEIGHT
            path = None
            enter_pressed = False
            continue

    if clicked_position:
        goal = pygame.draw.circle(trafic_surface, 'blue', clicked_position, 10)

        new_x, new_y = car_x, car_y

        if keys[pygame.K_LEFT]:
            new_x -= car_speed
        if keys[pygame.K_RIGHT]:
            new_x += car_speed
        if keys[pygame.K_UP]:
            new_y -= car_speed
        if keys[pygame.K_DOWN]:
            new_y += car_speed
     
        new_x = max(0, min((SCREEN_WIDTH - CAR_WIDTH), new_x))
        new_y = max(0, min((SCREEN_HEIGHT - CAR_HEIGHT), new_y))

        if road_mask.overlap(car_mask, (new_x, new_y)):
            car_x, car_y = new_x, new_y
        
        current_time = pygame.time.get_ticks()
        if current_time - last_traffic_light_change >= 4000:  # 4000 ms = 4 sek
            trafic_surface.fill((0, 0, 0, 0))   # keeping ony one light on the traffic lights
            for traffic_num in range(1, len(trafic_lights_dict) + 1):
                light = random.choice(list(TRAFFIC_LIGHTS.keys()))
                x = trafic_lights_dict[traffic_num][0] + 16       
                y = trafic_lights_dict[traffic_num][1] + TRAFFIC_LIGHTS[light]
                pygame.draw.circle(trafic_surface, light, (x, y), 7)
            last_traffic_light_change = current_time  # refresing last change
         
        if not path:
            # creating car rect for manipulation
            car_rect = car_mask.get_rect()
            car_center = (car_x + car_rect.width / 2, car_y + car_rect.height / 2)
            path = find_path(car_center, clicked_position, road_mask)
        else:
            pygame.draw.lines(road_surface, (255, 0, 0), False, path, 2)
            if enter_pressed:
                for point in path:
                    for event in pygame.event.get():

                        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                            running = False

                    if not running:
                        break
                    
                    car_x, car_y = point[0] - car_rect.width / 2, point[1] - car_rect.height / 2
                    screen.blit(background_image, (0, 0))
                    screen.blit(road_surface, (0, 0))
                    screen.blit(car, (car_x, car_y))
                    for i in range(1, len(trafic_lights_dict) + 1):
                        
                        screen.blit(trafic_lights, trafic_lights_dict[i])
                    screen.blit(trafic_surface, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(50)  
                enter_pressed = False


    screen.blit(background_image, (0,0))
    screen.blit(road_surface, (0, 0))
    screen.blit(car, (car_x, car_y))
    for i in range(1, len(trafic_lights_dict) + 1):
        screen.blit(trafic_lights, trafic_lights_dict[i])
    screen.blit(trafic_surface, (0,0))
    

    pygame.display.flip()


pygame.quit()