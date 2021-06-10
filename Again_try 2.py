"""
Platformer Game
"""
import arcade
import random
import math
import PIL
from arcade.draw_commands import Texture

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"


# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_LASER_SCALING = 0.8

##

BULLET_SPEED = 5
##map indicators
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE*TILE_SCALING)

SPRITE_SIZE = int(SPRITE_PIXEL_SIZE*TILE_SCALING)
# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5

# Constant used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 64
PLAYER_START_Y = 225

# For Explosion

EXPLOSION_TEXTURE_COUNT = 60

#
def load_texture_pair(filename):
    """ Load a texture pair with the second being a mirror image.
    """
    return[
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()
        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        self.cur_texture = 0

        # for flipping between image sequences
        self.scale = CHARACTER_SCALING

        ## BE CAREFULLL
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        # IMAGES
        main_path = ":resources:images/animated_characters/female_adventurer/femaleAdventurer"

        # load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # load texture for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)
    def update_animation(self, delta_time: float = 1/60):
        # figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        # idle animation

        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]


        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

    def create_player_sprite(self) -> arcade.AnimatedWalkingSprite:
        """Creates the animated player sprite

        Returns:
            The properly set up player sprite
        """
        # Where are the player images stored?
        texture_path = ASSETS_PATH / "images" / "player"

        # Set up the appropriate textures
        walking_paths = [
            texture_path / f"alienGreen_walk{x}.png" for x in (1, 2)
        ]
        climbing_paths = [
            texture_path / f"alienGreen_climb{x}.png" for x in (1, 2)
        ]
        standing_path = texture_path / "alienGreen_stand.png"

        # Load them all now
        walking_right_textures = [
            arcade.load_texture(texture) for texture in walking_paths
        ]
        walking_left_textures = [
            arcade.load_texture(texture, mirrored=True)
            for texture in walking_paths
        ]

        walking_up_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]
        walking_down_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]

        standing_right_textures = [arcade.load_texture(standing_path)]

        standing_left_textures = [
            arcade.load_texture(standing_path, mirrored=True)
        ]

        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the proper textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.walk_up_textures = walking_up_textures
        player.walk_down_textures = walking_down_textures

        # Set the player defaults
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT

        # Set the initial texture
        player.texture = player.stand_right_textures[0]

        return player



class Explosion(arcade.Sprite):
    """ This class is for explosion animation
    """
    def __init__(self,texture_list):
        super().__init__()
        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list
    def update(self):
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):

        # Call the parent class and set up the window
        super().__init__(width,height,title)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        #self.item_list = None
        self.coin_list = None
        self.wall_list = None
        #self.lava_list = None
        self.player_list = None
        #self.player_list1 = None
        self.enemy_list = None
        self.bullet_list = None
        self.player = None

        # Explosion
        self.explosion_list = None

        # Dont show the mouse cursor
        #self.set_mouse_visible(False)

        ## Pre-load the animation frames.
        self.explosion_texture_list = []
        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = f":resources:images/spritesheets/explosion.png"

        # Load the explosion from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width,sprite_height,columns,count)


        ## FOREGROUND, BACKGROUND , DO NOT TOUCH LIST

        self.background_list = None
        self.foreground_list = None
        self.dont_touch_list = None

        # Keep track of the score (Özgür)
        self.score = 0


        # Separate variable that holds the player sprite
        #self.player_sprite = None
        #self.player_sprite1 = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # right edge of the map
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds (+ Game over + gun sound)
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")


        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        ## ADD TIMER

        self.total_time = 0.0


    def setup(self,level): # we add level next to self
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score (Özgür)
        self.score = 0

        # Create the Sprite lists (added foreground, background)
        self.player_list = arcade.SpriteList()
        #self.player_list1 = arcade.SpriteList()  # sprite 2
        self.wall_list = arcade.SpriteList()
        #self.lava_list = arcade.SpriteList()
        #self.item_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()


        # Set up the player, specifically placing it at these coordinates.
        #image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        #self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        #self.player_sprite.center_x = PLAYER_START_X
        #self.player_sprite.center_y = PLAYER_START_Y
        #self.player_list.append(self.player_sprite)

        self.player = PlayerCharacter()
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player_list.append(self.player)

        # sprite 2
       # image_source1 = "images/player_1/player_stand.png"
        #self.player_sprite1 = arcade.Sprite(image_source1, CHARACTER_SCALING)
        #self.player_sprite1.center_x = 200
        #self.player_sprite1.center_y = 180
        #self.player_list1.append(self.player_sprite1)

        ## --- load in a map from the tilled editor

        #map_name = ":resources:tmx_maps/map.tmx"
        platform_layer_name = "Platforms"
        coins_layer_name = "Coins"
        #Name of the layer that has items for foreground
        foreground_layer_name = "Foreground"
        # Name of the layer that has items for background
        background_layer_name = "Background"
        # name of the layer that has items we should not touch
        dont_touch_layer_name = "Don't Touch"

        # MAp name
        map_name = f":resources:tmx_maps/map2_level_{level}.tmx"

        # read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # calculate the right edge of my_map
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # -- Background
        self.background_list = arcade.tilemap.process_layer(my_map, background_layer_name, TILE_SCALING)

        # -- Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,foreground_layer_name,TILE_SCALING)



        # read in the tiled map
        #my_map = arcade.tilemap.read_tmx(map_name)

        # Platforms

        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platform_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING, use_spatial_hash=True)


        # --- Dont touch layer

        self.dont_touch_list = arcade.tilemap.process_layer(my_map,dont_touch_layer_name,TILE_SCALING,use_spatial_hash=True)

        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create "physic engine"

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list, GRAVITY)

        # Add items
        #coin = arcade.Sprite("images/items/coinBronze.png", TILE_SCALING)
        #coin.center_x = 150
        #coin.center_y = 500
        #self.item_list.append(coin)


        # Add gold coins
        coordinate_list0 = [[256, 400],
                            [512, 400],
                            [768, 400]]

        for coordinate in coordinate_list0:
            coinG = arcade.Sprite("images/items/coinGold.png", TILE_SCALING)
            coinG.position = coordinate
            self.coin_list.append(coinG)

             #Add Blue gems
            coordinate_list1 = [[400, 400],
                                [600, 400],
                                [1080, 400]]

            for coordinate in coordinate_list1:
                gem = arcade.Sprite("images/items/gemBlue.png", TILE_SCALING)
                gem.position = coordinate
                self.coin_list.append(gem)


        # ADD SOME ENEMY MOVING

        enemy = arcade.Sprite(":resources:images/enemies/wormGreen.png", TILE_SCALING)

        enemy.bottom = SPRITE_SIZE
        enemy.left = SPRITE_SIZE*2

        # Gİve some speed
        enemy.change_x = 2
        self.enemy_list.append(enemy)

        # Enemy on the plateform

        enemy = arcade.Sprite("images/enemies/bee.png")
        enemy.bottom = SPRITE_SIZE*4
        enemy.left = SPRITE_SIZE*4

        # Boundaries

        enemy.boundary_right = SPRITE_SIZE*8
        enemy.boundary_left = SPRITE_SIZE *3
        enemy.change_x = 2
        self.enemy_list.append(enemy)


        # Add enemey - bee
        #for x in range(100, 1000, 250):
            #bee = arcade.Sprite(":resources:images/enemies/bee.png", TILE_SCALING)
            #bee.center_x = x
            #bee.center_y = 600
            #self.enemey_list.append(bee)

        # Add more enemeys
        #coordinate_list1 = [[256, 250],
                           #[512, 250],
                           #[768, 250]]

        #for coordinate in coordinate_list1:
            # Add a crate on the ground
            #frog = arcade.Sprite("images/enemies/frog.png", TILE_SCALING)
            #frog.position = coordinate
           # self.enemey_list.append(frog)




        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        #for x in range(100, 3000, 64):
            #wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            #wall.center_x = x
            #wall.center_y = 100
            #self.wall_list.append(wall)

        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        #coordinate_list = [[256, 160],
                           #[512, 160],
                           #[768, 160]]

        #for coordinate in coordinate_list:
            # Add a crate on the ground
            #wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
            #wall.position = coordinate
            #self.wall_list.append(wall)

            # The floor is lava!!!
            # This shows using a loop to place multiple sprites horizontally
            # Put some lava on the ground
            # This shows using a coordinate list to place sprites
        #for x in range(0, 3000, 64):
            #lava = arcade.Sprite(":resources:images/tiles/lavaTop_high.png", TILE_SCALING)
            #lava.center_x = x
            #lava.center_y = 1
            #self.wall_list.append(lava)

        # Create the 'physics engine'
        #self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             #self.wall_list,
                                                             #GRAVITY)
        ## Timers

        self.total_time = 0.0

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        ## Calculates minutes
        minutes = int(self.total_time) // 60

        ## Calculates seconds:

        seconds = int(self.total_time)%60

        ## Output
        output = f"Time {minutes:02d}:{seconds:02d}"

        # Output the timer text
        arcade.draw_text(output,10+self.view_left,30+self.view_bottom, arcade.color.BLACK,20)

        # Draw our sprites (add background, dont touch and foreground)
        self.wall_list.draw()
        self.background_list.draw()
        self.foreground_list.draw()
        self.dont_touch_list.draw()
        #self.lava_list.draw()
        #self.item_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        #self.player_list1.draw()
        self.coin_list.draw()
        self.explosion_list.draw()

        self.bullet_list.draw()

        # Draw our score on the screen , scrolling it with the viewport

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text,10+self.view_left, 10+self.view_bottom,arcade.csscolor.WHITE,18)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked.
        """

        arcade.sound.play_sound(self.gun_sound)
        # create a bullet
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png",SPRITE_LASER_SCALING)

        # POSITION THE BULLET
        start_x = self.player.center_x
        start_y = self.player.center_y

        bullet.center_x = start_x
        bullet.center_y = start_y

        # mouse destination
        dest_x = x + self.view_left
        dest_y = y + self.view_bottom


        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        #Angle the bullet sprite
        bullet.angle = math.degrees(angle)
        print(f"Bullet angle: {bullet.angle: .2f}")

        bullet.change_x = math.cos(angle)*BULLET_SPEED
        bullet.change_y = math.sin(angle)*BULLET_SPEED

        # Add the bullet to the appropriate list

        self.bullet_list.append(bullet)






    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE: # we can jump either with W or space or UP
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # update time

        self.total_time += delta_time

        self.player_list.update_animation()

        # Move the player with the physics engine
        self.physics_engine.update()
        self.explosion_list.update()


        if not self.game_over:
            self.enemy_list.update()

            for enemy in self.enemy_list:
                if len(arcade.check_for_collision_with_list(enemy,self.wall_list))> 0 :
                    enemy.change_x *= -1
                elif enemy.boundary_left is not None and enemy.left < enemy.boundary_left:
                    enemy.change_x *=-1
                elif enemy.boundary_right is not None and enemy.right > enemy.boundary_right:
                    enemy.change_x *= -1


        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player,
                                                             self.coin_list)
        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score(!!!)
            self.score +=1

        # Bullet
        self.bullet_list.update()

        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet,self.coin_list)
            hit_enemy = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            if len(hit_list)>0:
                # play a sound
                arcade.play_sound(self.gun_sound)
                bullet.remove_from_sprite_lists()

            for coin in hit_list:
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.collect_coin_sound)
                self.score += 1

            if len(hit_enemy) > 0:
                # Make an explosion
                explosion = Explosion(self.explosion_texture_list)
                # Move it to the location of the enemy
                explosion.center_x = hit_enemy[0].center_x
                explosion.center_y = hit_enemy[0].center_y
                # Call update
                explosion.update()
                self.explosion_list.append(explosion)

                arcade.play_sound(self.gun_sound)
                bullet.remove_from_sprite_lists()

            for enemy in hit_enemy:
                arcade.sound.play_sound(self.hit_sound)
                enemy.remove_from_sprite_lists()


            # if the bullet flies off screen, remove it
            if bullet.bottom > self.width+self.view_bottom or bullet.top <0 or bullet.right <0 or bullet.left > self.width+self.view_left:
                bullet.remove_from_sprite_lists()


        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        ## Did The player fall of the map ?

        if self.player.center_y < -100:
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y
            # set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed = True
            arcade.play_sound(self.game_over)

        # Did player touched smt that they should not
        if arcade.check_for_collision_with_list(self.player,self.dont_touch_list):
            self.player.change_x=0
            self.player.change_y = 0
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y
            # Set the camera to the start

            self.view_left=0
            self.view_bottom=0
            changed  =True
            arcade.play_sound(self.game_over)

        # See if the user got the end of the level
        if self.player.center_x >= self.end_of_map:
            # Advance to the next level
            self.level +=1
            # load the next level
            self.setup(self.level)
            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed = True

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)



def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup(window.level)
    arcade.run()


if __name__ == "__main__":
    main()
