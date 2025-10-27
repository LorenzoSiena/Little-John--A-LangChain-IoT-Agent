# =======================================================
# File: led_server_microdot_raspy.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: Microdot web server for remote LED control (Pin 17: Red, Pin 27: Blue).
# Requirements: 
#    A raspberry pi (2B or more)
#    python3 
#    pip install gpiozero microdot
# License: GNU General Public License v3.0 (GPLv3)
# =======================================================

from microdot import Microdot,redirect
from gpiozero import LED
from time import sleep


#Led setup
red = LED(17)
blue = LED(27)

app = Microdot()
@app.route('/')
def index(request):
    return redirect('/led')


@app.route('/led', methods=['POST','GET'])
def led(request):
    """
    Endpoint for LED control 
    A valid request can be: 
    curl -X POST -H "Content-Type: application/json" -d '[{"color": "red", "status": "high"}, {"color": "blue", "status": "low"}]' "$URL"
    """

    if request.method == 'POST':
        try:
            # 1. Waiting for the commands as JSON
            commands = request.json

            if not isinstance(commands, list):
                return {'error': 'Commands must be a list .'}, 400

            results = []

            # 2. Iterate the commands 
            for command in commands:
        
                color = command.get('color', '').lower()
                status = command.get('status', '').lower()

                # 3. Case for led type
                if color == 'red':
                    target_led = red
                elif color == 'blue':
                    target_led = blue
                else:
                    results.append({'color': color, 'status': 'skipped', 'message': 'Not a valid color.'})
                    continue  # Next command

                # 4. Case for led status
                if status == 'high':
                    target_led.on()
                    action = 'ON'
                elif status == 'low':
                    target_led.off()
                    action = 'OFF'
                else:
                    results.append({'color': color, 'status': 'skipped', 'message': 'Not a valid status.'})
                    continue

                # Feedback
                results.append({'color': color, 'status': action, 'message': 'Success'})
                print(f"Command executed: LED {color.upper()} set {action}") 

            # 5. Return the results
            return {'status': 'completed', 'results': results}

        except Exception as e:
           print(f"Error during POST request: {e}")
           return {'error': f'Error during POST request: {e}'}, 500

    else:
        # GET endpoint test sequence
        for i in range(5):
            red.on()
            blue.on()
            sleep(0.2) 
            red.off()
            blue.off()
            sleep(0.2)
        return "Test sequence completed."

app.run(debug=True)