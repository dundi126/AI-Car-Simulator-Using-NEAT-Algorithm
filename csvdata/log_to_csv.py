import re
import csv

# Define the log file path and the output CSV file path
log_file_path = 'simulation_log.txt'
csv_file_path = 'abudhabi.csv'

# Regular expression to extract log components (Generation, Car ID, Speed, Angle, Distance, Alive status)
log_pattern = re.compile(r'Generation\s+(\d+)\s+-\s+Car\s+(\d+):\s+Speed:\s+(\d+),\s+Angle:\s+([-]?\d+),\s+Distance:\s+(\d+),\s+Alive:\s+(True|False)')

# Open the log file and the CSV file
with open(log_file_path, 'r') as log_file, open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the header for the CSV
    csv_writer.writerow(['Generation', 'Car ID', 'Speed', 'Angle', 'Distance', 'Alive'])

    # Process each line in the log file
    for line in log_file:
        match = log_pattern.search(line)
        if match:
            # Extract the components from the log using the regex
            generation, car_id, speed, angle, distance, alive = match.groups()
            # Write the extracted data to the CSV file
            csv_writer.writerow([generation, car_id, speed, angle, distance, alive])

print(f"Log data has been successfully written to {csv_file_path}.")
