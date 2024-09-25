#!/bin/bash

# Step 1: Ensure the script is running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root. Re-running with sudo..."
    sudo bash "$0" "$@"
    exit
fi

# Step 2: Log file setup
LOGFILE="/home/Automata/install_log.txt"
exec > >(tee -i "$LOGFILE") 2>&1
echo "Installation started at: $(date)"

# Step 3: Install necessary dependencies for Tkinter, Chromium, and Pillow
echo "Installing dependencies for GUI and Chromium..."
sudo apt-get update
sudo apt-get install -y python3-tk python3-pil python3-pil.imagetk chromium-browser

# Step 4: Create the Python GUI script for the installation progress (Start GUI earlier)
INSTALL_GUI="/home/Automata/install_progress_gui.py"

cat << 'EOF' > $INSTALL_GUI
import tkinter as tk
from tkinter import ttk
import subprocess
import threading

# Create the main window
root = tk.Tk()
root.title("Automata Installation Progress")

# Set window size and position
root.geometry("600x400")
root.configure(bg='#2e2e2e')  # Dark grey background

# Title message
label = tk.Label(root, text="Automata Installation Progress", font=("Helvetica", 18, "bold"), fg="#00b3b3", bg="#2e2e2e")
label.pack(pady=20)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress.pack(pady=20)

# Status message
status_label = tk.Label(root, text="Starting installation...", font=("Helvetica", 12), fg="orange", bg="#2e2e2e")
status_label.pack(pady=10)

# Update progress function
def update_progress(step, total_steps, message):
    progress['value'] = (step / total_steps) * 100
    status_label.config(text=message)
    root.update_idletasks()

# Function to run shell commands in a separate thread
def run_shell_command(command, step, total_steps, message):
    update_progress(step, total_steps, message)
    result = subprocess.Popen(command, shell=True).wait()
    if result != 0:
        status_label.config(text=f"Error during: {message}. Check logs for details.")
        root.update_idletasks()

def run_installation_steps():
    total_steps = 10

    # Step 1: Set Internet Time with Eastern Standard Time
    run_shell_command("bash /home/Automata/AutomataBuildingManagment-HvacController/set_internet_time_rpi4.sh", 1, total_steps, "Setting system time to Eastern Standard Time...")

    # Step 2: Install Sequent Microsystems drivers
    run_shell_command("bash /home/Automata/AutomataBuildingManagment-HvacController/SequentMSInstall.sh", 2, total_steps, "Installing Sequent Microsystems drivers...")

    # Step 3: Install Node-RED and its palettes
    run_shell_command("lxterminal -e 'bash /home/Automata/AutomataBuildingManagment-HvacController/install_node_red.sh'", 3, total_steps, "Installing Node-RED interactively...")
    
    # Step 4: Install Node-RED palettes
    run_shell_command("bash /home/Automata/AutomataBuildingManagment-HvacController/InstallNodeRedPallete.sh", 4, total_steps, "Installing Node-RED palettes...")

    # Step 5: Set FullLogo.png as wallpaper and splash screen
    run_shell_command("sudo -u Automata DISPLAY=:0 pcmanfm --desktop & sleep 5 && sudo -u Automata DISPLAY=:0 pcmanfm --set-wallpaper='/home/Automata/FullLogo.png' && sudo cp /home/Automata/FullLogo.png /usr/share/plymouth/themes/pix/splash.png", 5, total_steps, "Setting wallpaper and splash screen...")

    # Step 6: Enable I2C, SPI, RealVNC, 1-Wire, disable serial port
    run_shell_command("sudo raspi-config nonint do_i2c 0 && sudo raspi-config nonint do_spi 0 && sudo raspi-config nonint do_vnc 0 && sudo raspi-config nonint do_onewire 0 && sudo raspi-config nonint do_serial 1", 6, total_steps, "Enabling I2C, SPI, RealVNC, disabling serial port...")

    # Step 7: Install Mosquitto
    run_shell_command("sudo apt-get install -y mosquitto mosquitto-clients && sudo mosquitto_passwd -b /etc/mosquitto/passwd Automata Inverted2", 7, total_steps, "Installing Mosquitto...")

    # Step 8: Increase swap size
    run_shell_command("bash /home/Automata/AutomataBuildingManagment-HvacController/increase_swap_size.sh", 8, total_steps, "Increasing swap size...")

    # Step 9: Add board update to auto-start for first reboot
    run_shell_command("bash /home/Automata/update_sequent_boards.sh", 9, total_steps, "Setting up board updates...")

    # Step 10: Installation complete
    update_progress(10, total_steps, "Installation complete. Please reboot.")

    # Show final message after reboot
    show_reboot_prompt()

# Function to show final reboot prompt
def show_reboot_prompt():
    root.withdraw()  # Hide the main window
    final_window = tk.Tk()
    final_window.title("Installation Complete")
    final_window.geometry("600x400")
    final_window.configure(bg='#2e2e2e')

    final_label = tk.Label(final_window, text="Automata Building Management & HVAC Controller", font=("Helvetica", 18, "bold"), fg="#00b3b3", bg="#2e2e2e")
    final_label.pack(pady=20)

    final_message = tk.Label(final_window, text="A New Realm of Automation Awaits!\nPlease reboot to finalize settings and config files.\n\nReboot Now?", font=("Helvetica", 14), fg="orange", bg="#2e2e2e")
    final_message.pack(pady=20)

    # Reboot and Exit buttons
    button_frame = tk.Frame(final_window, bg='#2e2e2e')
    button_frame.pack(pady=20)

    reboot_button = tk.Button(button_frame, text="Yes", font=("Helvetica", 12), command=lambda: subprocess.Popen('sudo reboot', shell=True), bg='#00b3b3', fg="black", width=10)
    reboot_button.grid(row=0, column=0, padx=10)

    exit_button = tk.Button(button_frame, text="No", font=("Helvetica", 12), command=final_window.destroy, bg='orange', fg="black", width=10)
    exit_button.grid(row=0, column=1, padx=10)

    final_window.mainloop()

# Start the installation in a separate thread to keep GUI responsive
threading.Thread(target=run_installation_steps).start()

# Tkinter loop runs in the background while install runs
root.mainloop()
EOF

# Step 5: Start the Tkinter GUI in the background
python3 $INSTALL_GUI

# Step 6: Ensure Chromium doesn't leave the desktop blank after closing
cat << 'EOF' > /home/Automata/launch_chromium.sh
#!/bin/bash

# Wait for the network to be connected
while ! ping -c 1 127.0.0.1 &>/dev/null; do
    sleep 1
done

# Wait for an additional 10 seconds after network connection
sleep 10

# Ensure the desktop environment is running
pcmanfm --desktop &

# Launch Chromium in windowed mode (not full-screen or kiosk mode)
chromium-browser --new-window http://127.0.0.1:1880/ http://127.0.0.1:1880/ui &

# Keep the script running to preventsession from closing
wait
EOF

# Make the script executable
chmod +x /home/Automata/launch_chromium.sh

# Add the script to autostart for the current user
AUTOSTART_FILE="/home/Automata/.config/lxsession/LXDE-pi/autostart"

# Ensure the autostart directory exists
mkdir -p $(dirname "$AUTOSTART_FILE")

# Add the launch script to autostart
if ! grep -q 'launch_chromium.sh' "$AUTOSTART_FILE"; then
    echo "@/home/Automata/launch_chromium.sh" >> "$AUTOSTART_FILE"
fi

echo "Chromium launch script has been added to autostart."
