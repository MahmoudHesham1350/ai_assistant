from pynput import keyboard
import time
import threading

class RobustHotkeyManager:
    """
    A simplified, robust hotkey manager that focuses on reliability.
    """
    
    def __init__(self):
        # Dictionary to track which keys are currently pressed
        self.pressed_keys = {}
        
        # Dictionary of hotkeys {name: (keys, callback)}
        self.hotkeys = {}
        
        # Flag to indicate if the listener is running
        self.running = False
        
        # Debug mode
        self.debug = False
        
        # Listener reference
        self.listener = None
        
        # Track control key status separately
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.win_pressed = False
        
        # Track last pressed key for special handling
        self.last_pressed_key = None
        
        # Dictionary of pressed letters (by virtual key code or char)
        self.active_letters = {}
    
    def register(self, name, keys, callback):
        """
        Register a hotkey.
        
        Args:
            name: Name for this hotkey
            keys: List of key names as strings (e.g., ["ctrl", "s"])
            callback: Function to call when hotkey is pressed
        """
        self.hotkeys[name] = (keys, callback)
        if self.debug:
            print(f"Registered hotkey '{name}': {keys}")
    
    def _on_press(self, key):
        """Handle key press events."""
        # Save the key for debugging
        self.last_pressed_key = key
        
        # Try to get a string representation and track virtual key code
        try:
            # For regular character keys
            key_str = key.char
            if key_str:
                self.active_letters[key_str.lower()] = True
            
            # Also track by virtual key code if available (for Windows)
            if hasattr(key, 'vk') and 65 <= key.vk <= 90:  # A-Z range
                letter = chr(key.vk + 32)  # Convert to lowercase
                self.active_letters[letter] = True
                if self.debug:
                    print(f"Tracking letter by vk: {letter} (vk={key.vk})")
                
        except AttributeError:
            # For special keys
            key_str = str(key)
        
        # Debug output
        if self.debug:
            details = []
            if hasattr(key, 'vk'):
                details.append(f"vk={key.vk}")
            if hasattr(key, 'scan_code'):
                details.append(f"scan={key.scan_code}")
            
            detail_str = f" ({', '.join(details)})" if details else ""
            print(f"Key pressed: {key_str}{detail_str} (type: {type(key).__name__})")
        
        # Track modifier keys directly
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = True
            if self.debug:
                print("CTRL key pressed")
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = True
            if self.debug:
                print("ALT key pressed")
        elif key == keyboard.Key.cmd:
            self.win_pressed = True
            if self.debug:
                print("WIN key pressed")
        
        # Check active hotkeys
        self._check_hotkeys(key)
    
    def _check_hotkeys(self, key):
        """Check if any registered hotkey combinations are active."""
        # First, determine what single key this might be
        single_key = None
        
        # For special keys, use their name
        if hasattr(key, 'char'):
            if key.char:
                single_key = key.char.lower()
        else:
            single_key = str(key).replace('Key.', '')
        
        # Special case for empty characters on Windows with Ctrl pressed
        if not single_key or single_key == '' and isinstance(key, keyboard.KeyCode) and self.ctrl_pressed:
            # This is likely a Ctrl+Letter combination in Windows
            # Let's use the vk (virtual key code) if available
            if hasattr(key, 'vk'):
                # Convert virtual key codes to letters (ASCII: A=65, B=66, etc.)
                if 65 <= key.vk <= 90:  # A-Z range
                    single_key = chr(key.vk + 32)  # Convert to lowercase
                    if self.debug:
                        print(f"Converted empty key with vk={key.vk} to '{single_key}'")
        
        # Dump current key states if in debug mode
        if self.debug:
            print(f"Current state: CTRL={self.ctrl_pressed}, ALT={self.alt_pressed}, WIN={self.win_pressed}")
            print(f"Active letters: {self.active_letters}")
            print(f"Current key: {single_key}")
        
        # Check each hotkey
        for name, (keys, callback) in self.hotkeys.items():
            combination_active = True
            
            # First, check if all required modifier keys are pressed
            has_ctrl = 'ctrl' in [k.lower() for k in keys]
            has_alt = 'alt' in [k.lower() for k in keys]
            has_win = any(k.lower() in ('win', 'cmd') for k in keys)
            
            # If any required modifier is missing, skip this hotkey
            if (has_ctrl and not self.ctrl_pressed) or \
               (has_alt and not self.alt_pressed) or \
               (has_win and not self.win_pressed):
                continue
            
            # Check for the single key (letter/number/etc)
            for key_name in keys:
                key_name = key_name.lower()
                
                # Skip modifier keys, we already checked them
                if key_name in ('ctrl', 'alt', 'win', 'cmd'):
                    continue
                
                # Check if this letter key is active
                if key_name not in self.active_letters and key_name != single_key:
                    combination_active = False
                    break
            
            if combination_active:
                if self.debug:
                    print(f"Hotkey triggered: {name}")
                
                # Execute callback in a separate thread
                threading.Thread(target=callback).start()
    
    def _on_release(self, key):
        """Handle key release events."""
        # Try to get a string representation
        try:
            key_str = key.char
            # Remove released letter keys
            if key_str:
                self.active_letters.pop(key_str.lower(), None)
            
            # Also check by virtual key code
            if hasattr(key, 'vk') and 65 <= key.vk <= 90:  # A-Z range
                letter = chr(key.vk + 32)  # Convert to lowercase
                self.active_letters.pop(letter, None)
                
        except AttributeError:
            key_str = str(key)
        
        # Debug output
        if self.debug:
            print(f"Key released: {key_str}")
        
        # Track modifier keys directly
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
            if self.debug:
                print("CTRL key released")
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = False
            if self.debug:
                print("ALT key released")
        elif key == keyboard.Key.cmd:
            self.win_pressed = False
            if self.debug:
                print("WIN key released")
        
        # Stop listener if escape is pressed (unless in persistent mode)
        if key == keyboard.Key.esc and not getattr(self, 'persistent', False):
            self.running = False
            return False
    
    def start(self, debug=True, persistent=True):
        """
        Start the hotkey listener.
        
        Args:
            debug: If True, print debug information
            persistent: If True, don't stop on Escape key
        """
        if self.listener is not None:
            if self.debug:
                print("Hotkey manager is already running")
            return
        
        self.debug = debug
        self.persistent = persistent
        self.running = True
        
        # Create and start the listener
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False  # Set to True if you want to prevent other apps from receiving the keypresses
        )
        self.listener.daemon = True
        self.listener.start()
        
        if debug:
            print("Hotkey manager started")
            print("Debug mode enabled")
        if not persistent:
            print("Press Escape to stop")
    
    def stop(self):
        """Stop the hotkey listener."""
        self.running = False
        
        if self.listener:
            self.listener.stop()
            self.listener = None
            if self.debug:
                print("Hotkey manager stopped")


def ctrl_s_example():
    print("Ctrl+S was pressed!")

def ctrl_alt_win_example():
    print("Ctrl+Alt+Win was pressed!")

# Example usage
if __name__ == "__main__":
    # Create the hotkey manager
    manager = RobustHotkeyManager()
    
    # Register hotkeys with simpler string descriptions
    manager.register("save", ["ctrl", "s"], ctrl_s_example)
    manager.register("tri-key", ["ctrl", "alt", "win"], ctrl_alt_win_example)
    
    # Start with debug mode
    manager.start(debug=True)
    
    try:
        print("Press Ctrl+S or Ctrl+Alt+Win to test")
        print("Press Ctrl+C to exit")
        while manager.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    finally:
        manager.stop() 