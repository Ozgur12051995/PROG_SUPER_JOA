import arcade

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


def load_texture_pair(filename):
    """ Load a texture pair with the second being a mirror image.
    """
    return[
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]
RIGHT_FACING = 0
LEFT_FACING = 1
CHARACTER_SCALING = 1
UPDATES_PER_FRAME = 5



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


