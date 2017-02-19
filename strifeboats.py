

import pygame, random, time

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900

GRID_WIDTH = 10
GRID_HEIGHT = 10

#ship type sizes
CARRIER = 5
BATTLESHIP = 4
SUBMARINE = 3
DESTROYER = 3
PT_BOAT = 2

#directions
VERT = False
HOR = True

#cell status
OCCUPIED = 1
UNOCCUPIED = 0

#shot result possibilites
MISS = 0
HIT = 1
SUNK = 2

#prompt directions
FIRE_WHEN_READY = 'Fire when ready!'
INCOMING = 'DUCK! The enemy is returning fire!'
PLACE = 'Press \'P\' to place ships.'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


class Cell(pygame.sprite.Sprite):
    '''A grid of cells forms the board. A cell has position and knows
    if it's been clicked and if it's part of a ship's body.'''
    def __init__(self, width, height, letter, number, grid=None, ship=None):
        self.width = width
        self.height = height
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, BLUE, self.rect, 5)
        self.occupied = self.clicked = False
        self.coord = (letter, number)
        self.ship = ship

    def clear(self):
        '''Resets the cell to its initial state.'''
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLACK)
        self.occupied = self.clicked = False
        self.ship = None
        pygame.draw.rect(self.image, BLUE, pygame.Rect((0,0), (self.width, self.height)), 5)
        


class Ship():
    '''A ship is a group of adjacent cells in a line.'''
    def __init__(self, grid=None, row=0, column=0, size=1, direc=VERT, name="Sugar Boat", color=BLUE):
        self.grid = grid
        self.color = color
        self.name = name
        self.body = pygame.sprite.Group()
        self.direc = direc
        self.size = size
        self.row = row
        self.column = column
        self.row_offset = 0
        self.col_offset = 0
        self.health = size

    def update_body(self):
        '''Constructs the ship body using the given cell's row and column
        and the direction the body should extend.'''
        ship_place_test = UNOCCUPIED
        if self.direc == VERT:
            #print 'still vert'
            self.col_offset = 1
            self.row_offset = 0
        else:
            self.col_offset = 0
            self.row_offset = 1
        self.body.empty()
        for x in range(self.size):
            current_cell = self.grid[self.row + x * self.row_offset][self.column + x * self.col_offset]
            #print current_cell.coord
            if current_cell.occupied:
                self.body.empty()
                ship_place_test = OCCUPIED
            else:
                self.body.add(current_cell)
        return ship_place_test

class Brain:
    def __init__(self, grid):
        #keep track of a list of confirmed hits -- that is, if while trying to sink one ship the brain finds another, it will remember the second ship
        self.list_of_contacts = []
        self.grid = grid
        self.confirmed_hit = None
        self.current_target = None
        self.last_target = None

        self.vert_counter = 0

        self.up = False
        self.down = False
        self.left = False
        self.right = False

    def target_select(self):

        if self.last_target:
            row = ord(self.last_target.coord[0]) - 65
            col = self.last_target.coord[1] - 1

        if self.up:
            target = self.grid[row][col - 1]
            if target.clicked or col - 1 < 0:
                self.last_target = self.confirmed_hit
                self.up = False
                self.down = True
            return target

        if self.down:
            target = self.grid[row][col + 1]
            if target.clicked or col + 1 > GRID_HEIGHT:
                self.last_target = self.confirmed_hit
                self.down = False
                self.left = True
            return target

        if self.left:
            target = self.grid[row - 1][col]
            if target.clicked:
                self.last_target = self.confirmed_hit
                self.left = False
                self.right = True
            return target

        if self.right:

            target = self.grid[row + 1][col]
            if target.clicked or row + 1 > GRID_WIDTH:
                self.last_target = self.confirmed_hit
                self.right = False
            return target

        while 1:
            if self.list_of_contacts:
                #check to see if there's another hit on the board unaccounted for
                self.confirmed_hit = self.last_target = self.list_of_contacts.pop()
                self.up = True
                self.target_select
            rand_cell = self.grid[random.randint(0, GRID_WIDTH - 1)][random.randint(0, GRID_HEIGHT - 1)]
            if not rand_cell.clicked:
                if rand_cell.ship:
                    self.last_target = self.confirmed_hit = rand_cell
                    self.up = True
                return rand_cell

    def reset(self):
        '''Called upon sinking a ship to get the brain to reset its trackers'''
        self.last_target = self.confirmed_hit = None
        self.vert_counter = self.offset = 0
        self.up = self.down = self.left = self.right = False


def attack_cell(cell):
    '''checks the given cell for a ship, paints it according to the result'''
    if cell.occupied: #hit a ship
        cell.image.fill(RED)
        cell.ship.health = cell.ship.health - 1
        if cell.ship.health == 0: #hit every cell in the ship
            return SUNK
        return HIT
    else: #missed
        cell.image.fill(BLUE)
        return MISS

def check_vic(ship_list):
    '''simple loop through every ship in the list checking to see if they're all sunk'''
    for ship in ship_list:
        if ship.health != 0:
            return 0
        else:
            result = 1
    return result


def top_prompt(screen, background, msg):
    '''changes the header text'''
    font = pygame.font.Font(None, 36)
    text = font.render(msg, 0, WHITE)
    textpos = (text.get_rect(centerx=background.get_width()/2 - 20, y=20))
    eraser = pygame.Surface((SCREEN_WIDTH, 50))
    eraser.fill(BLACK)
    background.blit(eraser, (0,0))
    background.blit(text, textpos)
    screen.blit(background, (0,0))

def bot_prompt(screen, background, msg):
    '''changes the footer text'''
    font = pygame.font.Font(None, 36)
    text = font.render(msg, 0, WHITE)
    textpos = (text.get_rect(centerx=background.get_width()/2, y=background.get_height() - 50))
    eraser = pygame.Surface((SCREEN_WIDTH, 50))
    eraser.fill(BLACK)
    background.blit(eraser, (0 , SCREEN_HEIGHT - 50))
    background.blit(text, textpos)
    screen.blit(background, (0,0))

def place_ship(screen, background, grid, all_sprites, ship):
    '''places a ship at the clicked cell, if possible'''
    placing = True
    selection = False
    msg1 = 'Place your ' + str(ship.name) + '. Hit \'D\' to change direction.'
    msg2 = 'Confirm placement? Y/N'
    msg = msg1
    
    while placing:
        top_prompt(screen, background, msg)
        #display what direction the ship is facing for convenience
        if ship.direc:
            dir_sym = '-'
        else:
            dir_sym = '|'
        bot_prompt(screen, background, 'Direction: ' + dir_sym)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                #cycle through direction
                if ship.direc:
                    ship.direc = False
                else:
                    ship.direc = True

            if event.type == pygame.MOUSEMOTION:
                for cell in ship.body:
                    cell.clear()
                pos = pygame.Rect((event.pos), (0, 0))
                for i in range(GRID_WIDTH):
                    for j in range(GRID_HEIGHT):
                        if grid[i][j].rect.contains(pos):
                            ship.row = i
                            ship.column = j
                            try: #the try/except will catch an index error from placing a ship that would run off the grid
                                ship_place = ship.update_body()
                                if ship_place == UNOCCUPIED:
                                    for cell in ship.body:
                                        cell.image.fill(ship.color)
                                        cell.ship = ship
                                        cell.occupied = True
                                    all_sprites.update()
                                    all_sprites.draw(screen)
                                    pygame.display.flip()
                            except(IndexError):
                                pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                confirmed = False
                while not confirmed: #simple confirmation prompt to avoid misplacings
                    top_prompt(screen, background, msg2)
                    all_sprites.update()
                    all_sprites.draw(screen)
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                            confirmed = True
                            placing = False
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                            #player misclicked, so undo the ship placement
                            confirmed = True
                            msg = msg1
                            for cell in ship.body:
                                cell.clear()
                                
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
    bot_prompt(screen, background, '') #wipe the footer message

def enemy_ship_place(grid, ship_list):
    '''Loop that pickes ship locations for the enemy fleet at random.'''
    for ship in ship_list:
        ran = random.random()
        if ran >= 0.5:
            ship.direc = True
        else:
            ship.direc = False
        picked = False
        while not picked: #grab a random cell on the board
            randx = random.randint(0, GRID_WIDTH - 1) #for some reason there's an issue with selecting a cell
            randy = random.randint(0, GRID_HEIGHT - 1)#that's actually at an edge, hence the '- 1'
            if grid[randx][randy].occupied == False:
                ship.row = randx
                ship.column = randy
                try: #again, catch placements that would run off the grid
                    ship_place = ship.update_body()
                    if ship_place == UNOCCUPIED:
                        for cell in ship.body:
                            cell.occupied = True
                            cell.ship = ship
                            #cell.image.fill(ship.color) #uncomment this statement if you want to bugfix ship placement and/or cheat
                            picked = True
                except(IndexError):
                    pass
def main():
    #standard pygame initialization of screen, background, clock, font
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Strifeboats') #Apparently 'Battleship' was taken

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BLACK)

    #The arrays of cells are sprite groups
    player_grid_sprites = pygame.sprite.Group()
    ai_grid_sprites = pygame.sprite.Group()

    #the references are the outer bands of the grid that show the numbers and letters
    player_references = pygame.sprite.Group()
    ai_references = pygame.sprite.Group()

    #need to construct double arrays with list comprehensions before filling it in
    player_grid = [[None for x in range(GRID_WIDTH)] for x in range(GRID_HEIGHT)]
    ai_grid = [[None for x in range(GRID_WIDTH)] for x in range(GRID_HEIGHT)]

    #build the grids
    for i in range(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            #fill player grid
            player_grid[i][j] = Cell(50, 50, chr(ord('A') + i), j + 1)
            player_grid[i][j].rect.x =  100 + i * 50
            player_grid[i][j].rect.y =  200 + j * 50

            #fill ai grid
            ai_grid[i][j] = Cell(50, 50, chr(ord('A') + i), j + 1)
            ai_grid[i][j].rect.x = 1250 + i * 50
            ai_grid[i][j].rect.y = 200 + j * 50
            player_grid_sprites.add(player_grid[i][j])
            ai_grid_sprites.add(ai_grid[i][j])

            #fill the reference bars
            if i == 0: #top row
                player_desc_cell = Cell(50, 50, chr(ord('A') + j), 0)
                player_desc_cell.rect.x = player_grid[0][0].rect.x + j * 50 + 20
                player_desc_cell.rect.y = player_grid[0][0].rect.y - 50
                player_desc_cell.image = font.render(chr(ord('A') + j), 0, WHITE)
                player_references.add(player_desc_cell)

                ai_desc_cell = Cell(50, 50, 0, 0)
                ai_desc_cell.rect.x = ai_grid[0][0].rect.x + j * 50 + 20
                ai_desc_cell.rect.y = ai_grid[0][0].rect.y - 50
                ai_desc_cell.image = font.render(chr(ord('A') + j), 0, WHITE)
                ai_references.add(ai_desc_cell)

            if j == 0: # first column
                player_ref_cell = Cell(50, 50, chr(ord('A') + j), 0)
                player_ref_cell.rect.x = player_grid[0][0].rect.x - 50
                player_ref_cell.rect.y = player_grid[0][0].rect.y + i * 50 + 20
                player_ref_cell.image = font.render(str(i + 1), 0, WHITE)
                player_references.add(player_ref_cell)

                ai_ref_cell = Cell(50, 50, chr(ord('A') + j), 0)
                ai_ref_cell.rect.x = ai_grid[0][0].rect.x - 50
                ai_ref_cell.rect.y = ai_grid[0][0].rect.y + i * 50 + 20
                ai_ref_cell.image = font.render(str(i + 1), 0, WHITE)
                ai_references.add(ai_ref_cell)


    #bundle all of these to make it easier to display them at once
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player_grid_sprites, ai_grid_sprites, player_references, ai_references)

    #construct the fleets for the player and the computer
    carrier = Ship(size=CARRIER, grid=player_grid, name='Your Carrier', color=(255,255,0))
    battleship = Ship(size=BATTLESHIP, grid=player_grid, name='Your Battleship', color=(0,255,255))
    submarine = Ship(size=SUBMARINE, grid=player_grid, name='Your Submarine', color=(0,255,0))
    destroyer = Ship(size=DESTROYER, grid=player_grid, name='Your Destroyer', color=(255,0,255))
    pt_boat = Ship(size=PT_BOAT, grid=player_grid, name='Your PT Boat', color=(255,255,255))

    player_ship_list = []

    player_ship_list.append(carrier)
    player_ship_list.append(battleship)
    player_ship_list.append(submarine)
    player_ship_list.append(destroyer)
    player_ship_list.append(pt_boat)

    enemy_carrier = Ship(size=CARRIER, grid=ai_grid, name='Enemy Carrier', color=(255,255,0))
    enemy_battleship = Ship(size=BATTLESHIP, grid=ai_grid, name='Enemy Battleship', color=(0,255,255))
    enemy_submarine = Ship(size=SUBMARINE, grid=ai_grid, name='Enemy Submarine', color=(0,255,0))
    enemy_destroyer = Ship(size=DESTROYER, grid=ai_grid, name='Enemy Destroyer', color=(255,0,255))
    enemy_pt_boat = Ship(size=PT_BOAT, grid=ai_grid, name='Enemy PT Boat', color=(255,255,255))

    ai_ship_list = []

    ai_ship_list.append(enemy_carrier)
    ai_ship_list.append(enemy_battleship)
    ai_ship_list.append(enemy_submarine)
    ai_ship_list.append(enemy_destroyer)
    ai_ship_list.append(enemy_pt_boat)

    #implement text boxes that don't change as much as the prompts as a dict of the text and its position
    center_info = {'Enemy Fleet'    : pygame.Rect((ai_grid[GRID_WIDTH / 2][GRID_HEIGHT / 2].rect.x, SCREEN_HEIGHT - 150), (100, 50)),
                   'Player Fleet'   : pygame.Rect((player_grid[GRID_WIDTH / 2][GRID_HEIGHT / 2].rect.x - 50, SCREEN_HEIGHT - 150), (100, 50)),
                   'Fleet Status:'  : pygame.Rect((SCREEN_WIDTH / 2 - 50, 200), (100, 50))
                   }

    #add each ship's name ot the center so that the player will have an idea of what's still afloat
    for ship in range(len(player_ship_list)):
        center_info[player_ship_list[ship].name] = pygame.Rect((700, 300 + ship * 50),(100, 50))
        center_info[ai_ship_list[ship].name] = pygame.Rect((1000, 300 + ship * 50),(100, 50))

    #pygame's rect placing doesn't seem to allow me to center the rect upon creating it
    for key in center_info:
        center_info[key].centerx = center_info[key].x

    screen.blit(background, (0,0))

    msg = PLACE
    enemy_ship_place(ai_grid, ai_ship_list) #place the first round of enemy ships
    brain = Brain(player_grid)

    #through this whole shebang I assumed that too many calls to update and flip were better than too few
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()

    while True: #main loop, re-draws the original screen and resets the ships at every replay
        for key in center_info:
            background.blit(font.render(key, 0, WHITE), center_info[key])
        screen.blit(background, (0,0))
        top_prompt(screen, background, msg)

        for ship in range(len(player_ship_list)):
            player_ship_list[ship].health = player_ship_list[ship].size
            ai_ship_list[ship].health = ai_ship_list[ship].size

        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        
        playing = False
        ship_placing = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            #prompt player to place fleet
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                ship_placing = True
        if ship_placing:
            for ship in player_ship_list:
                place_ship(screen, background, player_grid, all_sprites, ship)
                playing = True
                msg = FIRE_WHEN_READY 
        #loop between player turns and computer turns
        while playing:
            play_again = False
            result = 0
            player_fired = False
            top_prompt(screen, background, msg)
            all_sprites.update()
            all_sprites.draw(screen)
            pygame.display.flip()
            for event in pygame.event.get(): #standard pygame event check
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = pygame.Rect((event.pos), (0, 0))
                    for i in range(GRID_WIDTH):
                        for j in range(GRID_HEIGHT):
                            if ai_grid[i][j].rect.contains(click) and not ai_grid[i][j].clicked:
                                #player has made a valid choice of target -- it's in the ai_grid and it hasn't already been targeted
                                ai_grid[i][j].clicked = True
                                player_fired = True
                                bot_prompt(screen, background, 'You shot: ' + str(ai_grid[i][j].coord[0]) + str(ai_grid[i][j].coord[1]))
                                result = attack_cell(ai_grid[i][j])
                                if result == 2:
                                    msg = 'SUNK! You sunk: ' + ai_grid[i][j].ship.name
                                    #redraw the sunken ship's name in red to signify its demise
                                    background.blit(font.render(ai_grid[i][j].ship.name, 0, RED), center_info[ai_grid[i][j].ship.name])
                                    screen.blit(background, (0,0))
                                    if check_vic(ai_ship_list): #after every ship sinking check to see if it was the last one afloat
                                        msg = 'VICTORY! Press \'P\' to play again!'
                                        top_prompt(screen, background, msg)
                                        all_sprites.update()
                                        all_sprites.draw(screen)
                                        pygame.display.flip()
                                        while not play_again:
                                            for event in pygame.event.get(): #event check for command to replay or quit
                                                if event.type == pygame.QUIT:
                                                    pygame.quit()
                                                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                                                    player_fired = False
                                                    playing = False
                                                    play_again = True
                                                    for i in range(GRID_WIDTH):
                                                        for j in range(GRID_HEIGHT):
                                                            player_grid[i][j].clear()
                                                            ai_grid[i][j].clear() #clear the board (couldn't do this in the main loop since
                                                                                  #that would wipe the board clean of ships on each iteration)
                                                    enemy_ship_place(ai_grid, ai_ship_list) #replace enemy ships
                                                    msg = PLACE
                    if player_fired: #player has completed turn
                        top_prompt(screen, background, msg)
                        all_sprites.update()
                        all_sprites.draw(screen)
                        pygame.display.flip()
                        if result == 2: #sleep a few seconds to let the player read the sinking prompt
                            time.sleep(3)
                        msg = INCOMING
                        top_prompt(screen, background, msg)
                        all_sprites.update()
                        all_sprites.draw(screen) #honestly I should start taking out chunks of this and seeing if the game breaks
                        pygame.display.flip()    #I forget what this is actually doing, but I suppose there was good reason at the time
                        time.sleep(1)
                        msg = FIRE_WHEN_READY
                        ai_fired = False
                        while not ai_fired: #haven't foudn a valid target yet
                            cell = brain.target_select() 
                            #pick a random cell like in placing a ship
                            if not cell.clicked:
                                ai_fired = True
                                cell.clicked = True
                                result = attack_cell(cell)
                                if result == 2:
                                    brain.reset()
                                    for cell in brain.list_of_contacts:
                                        if cell.ship.health == 0:
                                            brain.list_of_contacts.remove(cell)
                                    msg = 'SUNK! They sunk: ' + cell.ship.name
                                    #redraw the sunken ship's name in red
                                    background.blit(font.render(cell.ship.name, 0, RED), center_info[cell.ship.name])
                                    screen.blit(background, (0,0))
                                    top_prompt(screen, background, msg)
                                    all_sprites.update()
                                    all_sprites.draw(screen)
                                    pygame.display.flip()
                                    time.sleep(3) #moment of silence for fallen heroes
                                    msg = FIRE_WHEN_READY
                                    if check_vic(player_ship_list): #check to see if that was the last player ship afloat
                                        msg = 'DEFEAT! Press \'P\' to play again!'
                                        top_prompt(screen, background, msg)
                                        all_sprites.update()
                                        all_sprites.draw(screen)
                                        pygame.display.flip()
                                        while not play_again: #same reset process as before
                                            for event in pygame.event.get():
                                                if event.type == pygame.QUIT:
                                                    pygame.quit()
                                                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                                                    playing = False
                                                    play_again = True
                                                    for i in range(GRID_WIDTH):
                                                        for j in range(GRID_HEIGHT):
                                                            player_grid[i][j].clear()
                                                            ai_grid[i][j].clear()
                                                    enemy_ship_place(ai_grid, ai_ship_list)
                                                    msg = PLACE
                                elif result == 1:
                                    brain.list_of_contacts.append(cell)
                                    brain.last_target = cell
                                    if not brain.confirmed_hit:
                                        brain.confirmed_hit = cell
                                bot_prompt(screen, background, 'The enemy shot: ' + str(cell.coord[0]) + str(cell.coord[1]))
                        top_prompt(screen, background, msg)
                        all_sprites.update()
                        all_sprites.draw(screen)
                        pygame.display.flip()

#run main if program was called alone
if __name__ == '__main__':
    main()