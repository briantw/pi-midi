import rtmidi
import random
import time

# Define chord patterns (intervals from root note)
chords = {
    'C': [0, 4, 7],   # C major
    'G': [7, 11, 14], # G major
    'D': [2, 6, 9],   # D minor
    'A': [9, 13, 16]  # A major
}

# Setup MIDI ports with error handling
try:
    # List available ports
    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()
    
    print("Available input ports:", midi_in.get_ports())
    print("Available output ports:", midi_out.get_ports())
    
    # Open ports
    midi_in.open_port(1) # adjust to your setup
    midi_out.open_port(3)# adjust to your setup
    
    # Optional: set callback for more reliable MIDI input handling
    # (alternative to polling with get_message)
    
    print("MIDI ready! Playing a chord for each note received...")
    
    # Main loop
    while True:
        msg = midi_in.get_message()
        
        if msg:
            message, delta_time = msg
            # Print received message for debugging
            print(f"Received: {message}, delta: {delta_time}")
            
            # Check if it's a note on message (status byte & 0xF0 == 0x90)
            if (message[0] & 0xF0) == 0x90 and message[2] > 0:  # Note on with velocity > 0
                note, velocity = message[1], message[2]
                # Choose a random chord type
                key = random.choice(list(chords.keys()))
                print(f"Playing {key} chord")
                
                # Send chord notes
                for interval in chords[key]:
                    chord_note = note + interval
                    # Keep notes in MIDI range (0-127)
                    if 0 <= chord_note <= 127:
                        # Send note on
                        midi_out.send_message([message[0], chord_note, velocity])
            
            # Handle note off messages (either note off status or note on with velocity 0)
            elif (message[0] & 0xF0) == 0x80 or ((message[0] & 0xF0) == 0x90 and message[2] == 0):
                note = message[1]
                # Turn off all possible chord notes
                for key in chords:
                    for interval in chords[key]:
                        chord_note = note + interval
                        if 0 <= chord_note <= 127:
                            # Send note off (with note off status byte)
                            midi_out.send_message([0x80 | (message[0] & 0x0F), chord_note, 0])
        
        # Short sleep to prevent CPU hogging
        time.sleep(0.001)

except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Clean up
    if 'midi_in' in locals() and midi_in.is_port_open():
        midi_in.close_port()
    if 'midi_out' in locals() and midi_out.is_port_open():
        midi_out.close_port()
    print("Ports closed")
