import rtmidi
import numpy as np

midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()

midi_in.open_port(0)
midi_out.open_port(1)

velocity_history = []

def smooth_velocity(velocity, factor=0.2):
    velocity_history.append(velocity)
    if len(velocity_history) > 10:
        velocity_history.pop(0)
    return int((1 - factor) * velocity + factor * np.mean(velocity_history))

while True:
    msg = midi_in.get_message()
    if msg:
        note, velocity = msg[0][1], msg[0][2]
        new_velocity = smooth_velocity(velocity)
        midi_out.send_message([msg[0][0], note, new_velocity])
