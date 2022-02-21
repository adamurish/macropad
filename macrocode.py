from adafruit_macropad import MacroPad

macropad = MacroPad()

class KeyColor:
    rgb = [0, 0, 0]
    delta_scale = 5
    def get_color(self):
        return tuple(self.rgb)
    
    def update_channel(self, channel, change):
        self.rgb[channel] += change * self.delta_scale
        if self.rgb[channel] > 255:
            self.rgb[channel] = 0
        elif self.rgb[channel] < 0:
            self.rgb[channel] = 255

class Action:
    p_func = None
    r_func = None
    name = ""
    #press_func and release_func take list of args
    def __init__(self, press_func, release_func, name):
        self.p_func = press_func
        self.r_func = release_func
        self.name = name
    
    def on_press(self, *args):
        if(self.p_func is not None):
            self.p_func(*args)
    
    def on_release(self, *args):
        if(self.r_func is not None):
            self.r_func(*args)

#KEYPRESS ACTION
keycodes_matrix = [macropad.Keycode.KEYPAD_SEVEN, macropad.Keycode.KEYPAD_EIGHT, macropad.Keycode.KEYPAD_NINE,
                   macropad.Keycode.KEYPAD_FOUR, macropad.Keycode.KEYPAD_FIVE, macropad.Keycode.KEYPAD_SIX,
                   macropad.Keycode.KEYPAD_ONE, macropad.Keycode.KEYPAD_TWO, macropad.Keycode.KEYPAD_THREE,
                   macropad.Keycode.KEYPAD_ZERO, None, None]

def press_key(key_num):
    keycode = keycodes_matrix[key_num]
    macropad.keyboard.press(keycode)

def release_key(key_num):
    keycode = keycodes_matrix[key_num]
    macropad.keyboard.release(keycode)

keypress_action = Action(press_key, release_key, "NumKey")

#ECE 391 GDB MACRO ACTION
breakpoints = []
def gdb_macro_press(key_num):
    macropad.keyboard_layout.write("gdb bootimg\n")
    macropad.keyboard_layout.write("target remote 10.0.2.2:1234\n")
    for bp_str in breakpoints:
        macropad.keyboard_layout.write("b " + bp_str + "\n")

def add_breakpoint_press(key_num):
    action = input("(A)dd, (R)emove, (L)ist, or (C)lear?: ")
    if(action[0] == "A"):
        for i in range(int(action[1]) if len(action) == 2 else 1):
            breakpoints.append(input("Where to set breakpoint? (GDB syntax): "))
            if(breakpoints[-1] == "fart"):
                breakpoints.pop()
                macropad.play_file("fart.wav")
    elif(action == "R"):
        for i in range(len(breakpoints)):
            print("{}: {}".format(i, breakpoints[i]))
        rm_idx = int(input("Remove which breakpoint?: "))
        if(rm_idx < len(breakpoints)):
            breakpoints.pop(rm_idx)
    elif(action == "L"):
        for i in range(len(breakpoints)):
            print("{}: {}".format(i, breakpoints[i]))
    elif(action == "C"):
        breakpoints.clear()
    else:
        print("Invalid option")

#This is a list of action lists to be performed on each keyevent
action_list = [[keypress_action] for i in range(10)]
action_list.append([Action(gdb_macro_press, None, "GDBMac")])
action_list.append([Action(add_breakpoint_press, None, "AddBP")])

text_lines = macropad.display_text()

for i in range(4):
    text_lines[i].text = "{:^6} {:^6} {:^6}".format(action_list[i * 3][0].name, 
                                                action_list[i * 3 + 1][0].name, 
                                                action_list[i * 3 + 2][0].name)
text_lines.show()

macropad.pixels.brightness = 1
fill = True
play = False
key_color = KeyColor()
key_color.rgb = [0, 0, 0]
key_color.delta_scale = 15
channel = 0
enc_last = 0
cur_step = 0


while True:
    #CALCULATE CURRENT COLOR
    enc_delta = macropad.encoder - enc_last
    if(enc_delta != 0):
        key_color.update_channel(channel, enc_delta)
        enc_last = macropad.encoder
    color = key_color.get_color()
    #PROCESS ENCODER PRESS
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        channel = channel + 1 if channel < 2 else 0
        play = True
        enc_delta = 1 #FORCES REDRAW OF DISPLAY
    elif macropad.encoder_switch_debounced.released:
        macropad.stop_tone()
        play = False
    if play:
        macropad.stop_tone()
        macropad.start_tone((2 ** (cur_step / 12)) * 440)
    #SET NEOPIXEL COLORS
    if fill:
        macropad.pixels.fill(color)
    macropad.pixels[0] = macropad.pixels[1] = macropad.pixels[2] = color
    #PROCESS KEY EVENTS
    key_event = macropad.keys.events.get()
    while key_event:
        for action in action_list[key_event.key_number]:
            if key_event.pressed:
                action.on_press(key_event.key_number)
                macropad.pixels[key_event.key_number] = color
            else:
                action.on_release(key_event.key_number)
                macropad.pixels[key_event.key_number] = 0
        key_event = macropad.keys.events.get()
    #UPDATE DISPLAY
    if(enc_delta != 0):
        text_lines[0].text = "{:>3}, {:>3}, {:>3}".format(color[0], color[1], color[2])
        text_lines[1].text = "{:^3}  {:^3}  {:^3}".format("^" if channel == 0 else " ",
                                                        "^" if channel == 1 else " ",
                                                        "^" if channel == 2 else " ")
        text_lines[2].text = "Tone: {} Hz".format((2 ** (cur_step / 12)) * 440)
        text_lines.show()