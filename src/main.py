import argparse
import re


# Parse command line arguments
parser = argparse.ArgumentParser(description='Process QSOs to data that can be printed onto QSL labels.')

parser.add_argument('-i', '--input-adif', action='store',
	help='File name of the .adif file with the QSOs to be processed.')
parser.add_argument('-o', '--output', action='store',
	help='File name of the output .csv file to be processed in gLabels.')
parser.add_argument('-q', '--qsos-per-label', action='store',
	help='Maximum number of QSOs per label (max. 6).')
parser.add_argument('-m', '--via-manager', action='store_true',
	help='Process QSLs via QSL manager')

args = parser.parse_args()


if int(args.qsos_per_label) > 6:
	raise argparse.ArgumentTypeError("Too many QSOs per label. Maximum is 6.")
else:
	MAX_QSOS_PER_QSL = int(args.qsos_per_label)


# Compile all regular expressions used to parse ADIF
RE_FROM_CALL = re.compile(r"^.*<STATION_CALLSIGN:\d+>([^<]*)<.*$")
RE_VIA_CALL = re.compile(r"^.*<CHANGEME:\d+>([^<]*)<.*$")
RE_TO_CALL = re.compile(r"^.*<CALL:\d+>([^<]*)<.*$")
RE_DATE = re.compile(r"^.*<QSO_DATE:\d+>([^<]*)<.*$")
RE_TIME_ON = re.compile(r"^.*<TIME_ON:\d+>([^<]*)<.*$")
RE_BAND = re.compile(r"^.*<BAND:\d+>([^<]*)<.*$")
RE_MODE = re.compile(r"^.*<MODE:\d+>([^<]*)<.*$")
RE_RST = re.compile(r"^.*<RST_SENT:\d+>([^<]*)<.*$")
RE_QSL = re.compile(r"^.*<QSL_RCVD:\d+>([^<]*)<.*$")
RE_FREQ = re.compile(r"^.*<FREQ:\d+>([^<]*)<.*$")


# Read ADIF file line by line and fill the QSO list
qso_list = []

for line in open(args.input_adif, "r"):
	if RE_TO_CALL.match(line):
		# Leave QSL Manager empty if there is none
		if RE_VIA_CALL.match(line):
			via_call = RE_VIA_CALL.match(line).groups()[0]
		else: via_call = ""

		# Leave Frequency empty if there is none
		if RE_FREQ.match(line):
			freq = RE_FREQ.match(line).groups()[0]
		else: freq = ""

		qso = dict(
			to_call = RE_TO_CALL.match(line).groups()[0],
			from_call = RE_FROM_CALL.match(line).groups()[0],
			date_ymd = RE_DATE.match(line).groups()[0],
			time_hm = RE_TIME_ON.match(line).groups()[0],
			band = RE_BAND.match(line).groups()[0],
			mode = RE_MODE.match(line).groups()[0],
			rst = RE_RST.match(line).groups()[0],
			qsl = RE_QSL.match(line).groups()[0],
			via_call = via_call,
			freq = freq,
		)

		qso_list.append(qso)

# Sort QSO list by to callsign
qso_list = sorted(qso_list, key=lambda d: d['to_call']) 


class qslLabel:
	def __init__(self, to_call, via_call, from_call):
		self.to_call = to_call
		self.via_call = via_call
		self.from_call = from_call

		self.qso_list = []


	def __repr__(self):
		return self.to_call


	def qsos_on_label(self):
		return len(self.qso_list)


	def qr_string(self):
		qr = "From: " + self.from_call + " "

		if self.via_call != "":
			qr += "Via: " + self.via_call + " "

		qr += "To: " + self.to_call

		for qso in self.qso_list:
			qr += "\n"
			qr += "Date: " + qso["date_ymd"][6:8] + "." + qso["date_ymd"][4:6] + "." + qso["date_ymd"][2:4] + " "
			qr += "Time: " + qso["time_hm"][:2] + ':' + qso["time_hm"][2:] + " "
			qr += "Band: " + qso["band"].lower() + " "
			qr += "Mode: " + qso["mode"] + " "
			qr += "RST: " + qso["rst"] + " "
			qr += "QSL: "
			if qso["qsl"] == "Y":
				qr += "TNX"
			elif qso["qsl"] == "N":
				qr += "PSE"
			else:
				qr += "-|-"

		return qr


# Go through QSOs and create label objects
label_list = []
last_call = ""

for qso in qso_list:
	# Create new label if the callsign is different or if the last label is full
	if (qso["to_call"] != last_call) or (label_list[-1].qsos_on_label() >= MAX_QSOS_PER_QSL):
		label_list.append(qslLabel(qso["to_call"], qso["via_call"], qso["from_call"]))

	label_list[-1].qso_list.append(qso)
	last_call = qso["to_call"]


# Go through label objects and write a line to the output CSV for each label
with open(args.output, "w", encoding="utf8") as f:
	# Write CSV header
	csv_str = '"To";"Via";'
	for i in range(1, MAX_QSOS_PER_QSL+1):
		csv_str += '"D'+str(i)+'";"T'+str(i)+'";"F'+str(i)+'";"M'+str(i)+'";"R'+str(i)+'";"Q'+str(i)+'";'
	csv_str += '"QR_Data"\n'
	f.write(csv_str)

	for lbl in label_list:
		# Output Label only if it matches wether or not to create labels via QSL manager
		if args.via_manager == (len(lbl.via_call) > 0):
			# Replace 0 with zero with Stroke
			csv_str = '"' + lbl.to_call.replace("0", "Ø") + '";' + '"' + lbl.via_call.replace("0", "Ø") + '";'
			for qso in lbl.qso_list:
				csv_str += '"' + qso["date_ymd"][:4] + '-' + qso["date_ymd"][4:6] + '-' + qso["date_ymd"][6:8] + '";'
				csv_str += '"' + qso["time_hm"][:2] + ':' + qso["time_hm"][2:] + '";'
				csv_str += '"' + qso["freq"] + '";'
				csv_str += '"' + qso["mode"] + '";'
				csv_str += '"' + qso["rst"] + '";'

				if qso["qsl"] == "Y":
					csv_str += '"TNX";'
				elif qso["qsl"] == "N":
					csv_str += '"PSE";'
				else:
					csv_str += '"-|-";'

			# Fill up empty QSOs so that all lines of the CSV have the same number of columns
			for i in range(6 * (MAX_QSOS_PER_QSL - lbl.qsos_on_label())):
				csv_str += '"";'
			
			# Add QR code
			csv_str += '"' + lbl.qr_string() + '"\n'
			print(csv_str)
			f.write(csv_str)
