import os
import datetime
import time
import pandas as pd
import serial
from collections import defaultdict
from twilio.rest import Client

dfname = 'tags.csv'
serialPath = '/dev/cu.usbmodem142101'
baudRate = 115200
textSent = False # protection condition var that prevents lots of texts from being sent

twilio_number = ''
my_number = ''
account_sid = ''
auth_token = ''

def check_timeouts():
		current_time = datetime.datetime.now()
		for item_name, epcs in list(seen_epcs.items()):
			for epc, last_seen in list(epcs.items()):
				if (current_time - last_seen).total_seconds() > 1:
					del seen_epcs[item_name][epc]
					item_occurrences[item_name] -= 1
					print(f"Timeout: Decremented count for {item_name}, New Count: {item_occurrences[item_name]}")
					if item_occurrences[item_name] == 0:
						del item_occurrences[item_name]
						sendText("no more itemA :(")

def sendText(msg):
	if not textSent:
		client = Client(account_sid, auth_token)
		message = client.messages.create(
    	to=twilio_number,  # The recipient's phone number (include the country code)
    	from_=my_number,  # Your Twilio phone number (include the country code)
    	body=msg  # The content of the message
)
	else:
		print("MSG already sent")


if __name__ == '__main__':
	
	# Manually Populate DB with tags, need to delete CSV to update tags
	global allTags
	if not os.path.exists(dfname):
		data = {
    		'EPC': ['E2 00 42 04 DA A0 64 11 03 1A 2B 16', 
					'E2 00 42 04 D4 10 64 11 03 1A 2A AD', 
					'E2 00 42 04 D4 50 64 11 03 1A 2A B1', 
					'E2 00 42 04 8A 00 64 11 03 1A 26 0C', 
					'E2 00 42 04 82 80 64 11 03 1A 25 94'],
    		'ItemName': ['Item A', 'Item A', 'Item A', 'Item A', 'Item A']
		}

		allTags = pd.DataFrame(data)
		allTags.to_csv(dfname, index=False) # save to CSV in CD
	else:
		allTags = pd.read_csv(dfname)

	item_occurrences = defaultdict(int)
	seen_epcs = defaultdict(lambda: defaultdict(datetime.datetime))
	ser = serial.Serial(serialPath, baudRate)

try:
    while True:
        check_timeouts()

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()  # Read from serial port
            if "epc[" in line:
                start = line.find('epc[') + 4  # Find start index of EPC value
                end = line.find(']', start)  # Find end index of EPC value
                epc = line[start:end].strip()  # Extract and strip EPC value
                # Check if the EPC is in the DataFrame
                item = allTags[allTags['EPC'] == epc]['ItemName'].values
                if item:
                    item_name = item[0]  # Get the corresponding item name
                    # Update the last seen time or increment if it's a new EPC
                    if epc not in seen_epcs[item_name]:
                        item_occurrences[item_name] += 1  # Increment the count for this item
                        print(f"Detected new EPC for {item_name}, Count: {item_occurrences[item_name]}")
                    seen_epcs[item_name][epc] = datetime.datetime.now()  # Update last seen time
                else:
                    print("EPC not found in the DataFrame.")
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    ser.close()  # Ensure the serial connection is closed on exit
                    print("EPC not found in the DataFrame.")
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    ser.close()  # Ensure the serial connection is closed on exit
