import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os
from time import sleep

# Create the main window
root = tk.Tk()
root.title("Automata Installation Progress")
root.geometry("600x400")
root.configure(bg='#2e2e2e')

# Title message
label = tk.Label(root, text="Automata Installation Progress", font=("Helvetica", 18, "bold"), fg="#00b3b3", bg="#2e2e2e")
label.pack(pady=20)

# Footer message (Developed by A. Jewell Sr. 2023)
footer_label = tk.Label(root, text="Developed by A. Jewell Sr, 2023", font=("Helvetica", 10), fg="#00b3b3", bg="#2e2e2e")
footer_label.pack(side="bottom", pady=5)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress.pack(pady=20)

# Status message
status_label = tk.Label(root, text="Starting installation...", font=("Helvetica", 12), fg="orange", bg="#2e2e2e")
status_label.pack(pady=10)

# Function to update progress
def update_progress(step, total_steps, message):
    progress['value'] = (step / total_steps) * 100
    status_label.config(text=message)
    root.update_idletasks()

# Function to run shell commands
def run_shell_command(command, step, total_steps, message):
    update_progress(step, total_steps, message)
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        status_label.config(text=f"Error during: {message}. Check logs for details.")
        print(f"Error output: {result.stderr}")
        root.update_idletasks()
    else:
        print(f"Command output: {result.stdout}")

# Run all installation steps in order
def run_installation_steps():
    total_steps = 15
    step = 1

    # Step 1: Slightly overclock the Raspberry Pi
    run_shell_command("echo -e 'over_voltage=2\narm_freq=1750' | sudo tee -a /boot/config.txt", step, total_steps, "Overclocking CPU...Turning up to 11 Meow!")
    sleep(15)
    step += 1

    # Step 2: Clone Sequent Microsystems drivers
    run_shell_command("bash /home/Automata/AutomataBuildingManagment-HvacController/SequentMSInstall.sh", step, total_steps, "Cloning Sequent Microsystems board repositories...")
    sleep(15)
    step += 1

    # Step 3: Install Sequent Microsystems drivers
    boards = ["megabas-rpi", "megaind-rpi", "16univin-rpi", "16relind-rpi", "8relind-rpi"]
    for board in boards:
        board_path = f"/home/Automata/AutomataBuildingManagment-HvacController/{board}"
        if os.path.isdir(board_path):
            update_progress(step, total_steps, f"Cloning {board}... Success!")
            run_shell_command(f"cd {board_path} && sudo make install", step, total_steps, f"Installing {board} driver...")
            update_progress(step, total_steps, f"Make install {board}... Success!")
            step += 1
        else:
            update_progress(step, total_steps, f"Board {board} not found, skipping...")
            step += 1
        sleep(15)

    # Step 4: Install Node-RED
    run_shell_command("curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered | bash", step, total_steps, "Installing Node-RED...")
    sleep(15)
    step += 1

    # Step 5: Install Node-RED palettes (list each palette)
    palettes = [
        "node-red-contrib-ui-led",
        "node-red-dashboard",
        "node-red-contrib-sm-16inpind",
        "node-red-contrib-sm-16relind",
        "node-red-contrib-sm-8inputs",
        "node-red-contrib-sm-8relind",
        "node-red-contrib-sm-bas",
        "node-red-contrib-sm-ind",
        "node-red-node-openweathermap",
        "node-red-contrib-influxdb",
        "node-red-node-email",
        "node-red-contrib-boolean-logic-ultimate",
        "node-red-contrib-cpu",
        "node-red-contrib-bme280-rpi",
        "node-red-contrib-bme280",
        "node-red-node-aws",
        "node-red-contrib-themes/theme-collection"
    ]
    for palette in palettes:
        run_shell_command(f"cd ~/.node-red && npm install {palette}", step, total_steps, f"Installing {palette} palette...")
        step += 1
        sleep(15)

    # Step 6: Move splash screen
    run_shell_command("sudo mv /home/Automata/AutomataBuildingManagment-HvacController/splash.png /home/Automata/splash.png", step, total_steps, "Moving splash.png...")
    sleep(15)
    step += 1

    # Step 7: Set boot splash screen
    run_shell_command("sudo python3 /home/Automata/AutomataBuildingManagment-HvacController/set_boot_splash_screen.py", step, total_steps, "Setting boot splash screen...")
    sleep(15)
    step += 1

    # Step 8: Configure interfaces (i2c, spi, vnc, etc.)
    run_shell_command("sudo raspi-config nonint do_i2c 0 && sudo raspi-config nonint do_spi 0 && sudo raspi-config nonint do_vnc 0 && sudo raspi-config nonint do_onewire 0 && sudo raspi-config nonint do_serial 1", step, total_steps, "Configuring interfaces...")
    sleep(15)
    step += 1

    # Step 9: Install Mosquitto
    run_shell_command("sudo apt-get install -y mosquitto mosquitto-clients", step, total_steps, "Installing Mosquitto...")
    run_shell_command("sudo touch /etc/mosquitto/passwd && sudo mosquitto_passwd -b /etc/mosquitto/passwd Automata Inverted2", step, total_steps, "Setting Mosquitto password file...")
    sleep(15)
    step += 1

    # Step 10: Increase swap size
    run_shell_command("bash /home/Automata/AutomataBuildingManagment-HvacController/increase_swap_size.sh", step, total_steps, "Increasing swap size...")
    sleep(15)
    step += 1

    # Final step: Installation complete
    update_progress(total_steps, total_steps, "Installation complete. Please reboot.")
    show_reboot_prompt()

# Function to show the reboot prompt
def show_reboot_prompt():
    root.withdraw()
    final_window = tk.Tk()
    final_window.title("Installation Complete")
    final_window.geometry("600x400")
    final_window.configure(bg='#2e2e2e')

    final_label = tk.Label(final_window, text="Automata Building Management & HVAC Controller", font=("Helvetica", 18, "bold"), fg="#00b3b3", bg="#2e2e2e")
    final_label.pack(pady=20)

    final_message = tk.Label(final_window, text="A New Realm of Automation Awaits!\nPlease reboot to finalize settings and configuration files.\n\nReboot Now?", font=("Helvetica", 14), fg="orange", bg="#2e2e2e")
    final_message.pack(pady=20)

    button_frame = tk.Frame(final_window, bg='#2e2e2e')
    button_frame.pack(pady=20)

    reboot_button = tk.Button(button_frame, text="Yes", font=("Helvetica", 12), command=lambda: os.system('sudo reboot'), bg='#00b3b3', fg="black", width=10)
    reboot_button.grid(row=0, column=0, padx=10)

    exit_button = tk.Button(button_frame, text="No", font=("Helvetica", 12), command=final_window.destroy, bg='orange', fg="black", width=10)
    exit_button.grid(row=0, column=1, padx=10)

    final_window.mainloop()

# Start the installation steps in a separate thread to keep the GUI responsive
threading.Thread(target=run_installation_steps).start()

# Tkinter main loop to keep the GUI running
root.mainloop()

