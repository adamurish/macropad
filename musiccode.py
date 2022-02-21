from adafruit_macropad import MacroPad
import array
import digitalio
import audiopwmio
import audiocore
import audiomixer
import math
import board

def generate_sample(frequency):
    length = 32000 // frequency
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int(((2**15)-1)*math.sin(math.pi * 2 * i / length) + 2**15)
    return audiocore.RawSample(sine_wave, sample_rate=32000)
    
def generate_tones_samples(center):
    tones = []
    samples = []
    for i in range((-4 + center), (5 + center)):
        tones.append(int((2 ** (i / 12)) * 440))
        samples.append(generate_sample(tones[-1]))
    return tones, samples

pressed = [ False, False, False,
            False, False, False,
            False, False, False ]

macropad = MacroPad()

text_lines = macropad.display_text(title='Tone PAD')
cur_step = 0
tones, samples = generate_tones_samples(0)

while True:
    update_display = False
    #PROCESS KEY EVENTS
    key_event = macropad.keys.events.get()
    if key_event:
        if key_event.pressed:
            if key_event.key_number == 0:
                cur_step -= 1
                update_display = True
            elif key_event.key_number == 2:
                cur_step += 1
                update_display = True
            elif key_event.key_number >= 3:
                pressed[key_event.key_number-3] = True
                if pressed.count(True) > 1:
                    macropad.stop_tone()
                macropad.start_tone(tones[key_event.key_number-3])
        else:
            if key_event.key_number >= 3:
                pressed[key_event.key_number-3] = False
                if pressed.count(True) == 0:
                    macropad.stop_tone()
                else:
                    macropad.stop_tone() 
                    macropad.start_tone(tones[pressed.index(True)])
    #UPDATE DISPLAY
    if update_display:
        tones, samples = generate_tones_samples(cur_step)
        text_lines[0].text = "{} {} {}".format(tones[0], tones[1], tones[2])
        text_lines[1].text = "{} {} {}".format(tones[3], tones[4], tones[5])
        text_lines[2].text = "{} {} {}".format(tones[6], tones[7], tones[8])
        text_lines.show()