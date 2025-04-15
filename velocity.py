import rtmidi
import numpy as np
import time

# Setup MIDI ports with error handling
try:
    # List available ports
    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()
    
    print("Available input ports:", midi_in.get_ports())
    print("Available output ports:", midi_out.get_ports())
    
    # Open ports
    midi_in.open_port(1) # adjust to your setup
    midi_out.open_port(2)# adjust to your setup
    
    # Initialize velocity history dictionary (per note)
    velocity_histories = {}
    
    def smooth_velocity(note, velocity, factor=0.2):
        # Create history for this note if it doesn't exist
        if note not in velocity_histories:
            velocity_histories[note] = []
            
        # Add current velocity to history
        velocity_histories[note].append(velocity)
        
        # Keep history at a reasonable size
        if len(velocity_histories[note]) > 10:
            velocity_histories[note].pop(0)
            
        # Calculate smoothed velocity
        smoothed = int((1 - factor) * velocity + factor * np.mean(velocity_histories[note]))
        
        # Ensure velocity stays within MIDI range (1-127)
        # Note: 0 is a special case for note-off, so we preserve it
        if velocity > 0 and smoothed < 1:
            smoothed = 1
        elif smoothed > 127:
            smoothed = 127
            
        return smoothed
    
    print("MIDI velocity smoother running! Press Ctrl+C to exit.")
    
    # Main loop
    while True:
        msg = midi_in.get_message()
        
        if msg:
            message, delta_time = msg
            
            # If it's a valid message with at least 3 bytes
            if len(message) >= 3:
                status, note, velocity = message[0], message[1], message[2]
                
                # For note-on messages, smooth the velocity
                if (status & 0xF0) == 0x90 and velocity > 0:
                    new_velocity = smooth_velocity(note, velocity)
                    print(f"Note: {note}, Original vel: {velocity}, Smoothed vel: {new_velocity}")
                    midi_out.send_message([status, note, new_velocity])
                else:
                    # Pass through other messages unchanged (note-offs, CC, etc.)
                    midi_out.send_message(message)
            else:
                # Pass through other message types unchanged
                midi_out.send_message(message)
        
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
