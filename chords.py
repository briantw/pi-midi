import rtmidi
import random

chords = {
    'C': [0, 4, 7],
    'G': [0, 4, 7],
    'D': [0, 3, 7],
    'A': [0, 4, 7]
}

midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()

midi_in.open_port(0)
midi_out.open_port(1)

while True:
    msg = midi_in.get_message()
    if msg:
        note, velocity = msg[0][1], msg[0][2]
        key = random.choice(list(chords.keys()))
        for interval in chords[key]:
            midi_out.send_message([msg[0][0], note + interval, velocity])
