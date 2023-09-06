import os

def state_report(filename, values):
	'''
	A specific state breakdown report that uses the data from 'sum_field'

	Args:
		filename (string): The filename and path of the report
		values (array<dict>): An array of dictionaries that will create the report

	Return:
		bool: Success
	'''

	states = {}

	for val in values:
		state = val.get('patient_state') \
			if val.get('patient_state').strip() != '' else 'N/A'
		value = float(val.get('bill_amount')) \
			if val.get('bill_amount') != '' and val.get('bill_amount') != None else 0.0

		if states.get(state) != None:
			states[state] += value
		else:
			states[state] = value

	with open(filename, 'w') as file:
		total = 0.0
		for state in states.keys():
			file.write(f'{state}				-	{states[state]}\n')
			total += states[state]
		file.write(f'Total Billed	-	{total}')
		print(f'Billing report complete.')
		return True