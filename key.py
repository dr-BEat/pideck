from adafruit_hid.keycode import Keycode
from time import sleep


def convert_hex_to_rgb(value):
    """ Converts a hex value to RGB values """

    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def convert_rgb_to_hex(r: int, g: int, b: int):
    """ Converts RGB values into a Hex string """

    hex = "{:02x}{:02x}{:02x}".format(r, g, b).upper()
    return hex


class Key():
    """ Models a single Key on the keypad """
    _off = ""
    _on = ""
    _effect = ""  # pulse
    _command = ""
    _button_type = ""  # press, toggle
    _pulse_count = 10
    _pulse_up = False
    _toggle = False

    def __init__(self):
        self._type = "press"

    @property
    def command(self):
        """ Gets the current keystrokes to be sent on keypress """
        return self._command

    @command.setter
    def command(self, value):
        """ Sets the current keystrokes to be sent on keypress """
        self._command = value

    @property
    def on(self):
        """ Gets the current colour value for the button when its pressed """
        return self._on

    @on.setter
    def on(self, value):
        """ Sets the current colour value for the button when its pressed """
        self._on = value

    @property
    def off(self):
        """ Gets the current colour value for the button when its not pressed """
        return self._off

    @off.setter
    def off(self, value):
        """ Sets the current colour value for the button when its not pressed """
        self._off = value

    @property
    def effect(self):
        """ Gets the button effect (pulse) """
        return self._effect

    @effect.setter
    def effect(self, value):
        """ Sets the button effect (pulse, flash, none) """
        if value in ["pulse", "flash", "none"]:
            self._effect = value
        else:
            print(f"{value} is not a valid effect type")

    @property
    def button_type(self):
        """ Gets the button type (toggle or press) """
        return self._button_type

    @button_type.setter
    def button_type(self, value: str):
        """ Sets the button type (toggle or press) """
        if value in ["press", "toggle"]:
            self._button_type = value
        else:
            print("not a valid button_type")

    @property
    def toggle(self) -> bool:
        """ Gets the current toggle state (True or False) and flips the state """
        if self._toggle:
            self._toggle = False
            return True
        else:
            self._toggle = True
            return False

    def fade_colour(self, percent: float):
        '''assumes color is rgb between (0, 0, 0) and (255, 255, 255)'''

#         print (f"on: {self._on}, off: {self.off}, percent: {percent}")
        color_from_r, color_from_g, color_from_b = convert_hex_to_rgb(
            self._off)
        color_to_r, color_to_g, color_to_b = convert_hex_to_rgb(self._on)

        r_vector = color_from_r - color_to_r
        g_vector = color_from_g - color_to_g
        b_vector = color_from_b - color_to_b

        r = int(color_to_r + r_vector * percent)
        g = int(color_to_g + g_vector * percent)
        b = int(color_to_b + b_vector * percent)

        # return the colours
        return convert_rgb_to_hex(r, g, b)

    def pulse_tick(self):
        """ cycles the pulse animation through one step """
        if self._pulse_up:
            if self._pulse_count < 10:
                self._pulse_count += 1
            else:
                self._pulse_up = False
        else:
            if self._pulse_count > 0:
                self._pulse_count -= 1
            else:
                self._pulse_up = True
#         print(f"pulse_count: {self._pulse_count}")
        return self.fade_colour(self._pulse_count/10)

    def flash_tick(self):
        if self._pulse_count < 10:
            self._pulse_count += 1

        else:
            self._pulse_count = 0
            if self._pulse_up:
                self._pulse_up = False
            else:
                self._pulse_up = True

        if self._pulse_up:
            return self._on
        else:
            return self._off

    def send(self, keyb):
        """ Sends the current command to the attached computer """
        # split the string into separate strings
        keys = self._command.upper().replace("+", " ").split()

        aliasMap = {
            'CTRL': 'CONTROL',
            'OPT': 'OPTION',
            'CMD': 'COMMAND',
            '1': 'ONE',
            '2': 'TWO',
            '3': 'THREE',
            '4': 'FOUR',
            '5': 'FIVE',
            '6': 'SIX',
            '7': 'SEVEN',
            '8': 'EIGHT',
            '9': 'NINE',
            '0': 'ZERO',
            'ESC': 'ESCAPE',
            '.': 'PERIOD',
            ',': 'COMMA',
            ';': 'SEMICOLON',
            '\\': 'BACKSLASH',
            '/': 'FORWARD_SLASH',
            'LEFT': 'LEFT_ARROW',
            'RIGHT': 'RIGHT_ARROW',
            'UP': 'UP_ARROW',
            'DOWN': 'DOWN_ARROW',

            '[': 'LEFT_BRACKET',
            '{': 'LEFT_BRACKET',
            ']': 'RIGHT_BRACKET',
            '}': 'RIGHT_BRACKET',

            'MINUS': 'KEYPAD_MINUS',
            'PLUS': 'KEYPAD_PLUS'
        }

        for command in keys:
            # Try to get the command directly from a Keycode attribute
            keycode = getattr(Keycode, aliasMap.get(command, command), None)
            if keycode:
                keyb.press(keycode)
                # If we have a modifier key, do not release
                if Keycode.modifier_bit(keycode) == 0:
                    keyb.release_all()
            elif command == "COLON":
                keyb.press(Keycode.SHIFT)
                keyb.press(Keycode.SEMICOLON)
                keyb.release_all()
            elif command == "THUMBS-UP":
                keyb.press(Keycode.SHIFT)
                keyb.press(Keycode.SEMICOLON)
                keyb.release_all()
                keyb.press(Keycode.KEYPAD_PLUS)
                keyb.release_all()
                keyb.press(Keycode.ONE)
                keyb.release_all()
                keyb.press(Keycode.SHIFT)
                keyb.press(Keycode.SEMICOLON)
                keyb.release_all()
        keyb.release_all()
