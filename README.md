# QSL_QR_Label

Process QSOs to data that can be printed onto QSL labels for DARC's QSL card processing system. Implements DARC's QR code specification.

Experimental software, use with the some care and verify the results before batch printing.

**Currently only used for QSL cards within Germany. Cards with QR code within Germany have to be sorted seperately for the QSL bureau.**


## Workflow

1. Export ADIF file of QSOs to be printed onto QSL labels from your log software (tested with CQRLog and cloud log).
1. Run this script, e.g. `python3 main.py -i qsl.adif -o qsl.csv -q 4` creates label data with max. 4 QSOs per single label.
1. Import the csv into gLabels. Create your custom label template, for the `QR_Data` field use a QR code with approx. 30 x 30 mm² size, then print the labels.


## Usage

```
$ python main.py -h
usage: main.py [-h] [-i INPUT_ADIF] [-o OUTPUT] [-q QSOS_PER_LABEL] [-m]

Process QSOs to data that can be printed onto QSL labels.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_ADIF, --input-adif INPUT_ADIF
                        File name of the .adif file with the QSOs to be
                        processed.
  -o OUTPUT, --output OUTPUT
                        File name of the output .csv file to be processed in
                        gLabels.
  -q QSOS_PER_LABEL, --qsos-per-label QSOS_PER_LABEL
                        Maximum number of QSOs per label (max. 6).
  -m, --via-manager     Process QSLs via QSL manager
```

## Useful Info
Example SQL command to filter for multiple QSL conditions in CQRlog:
```
select * from view_cqrlog_main_by_qsodate where qsl_s = "SB" or qsl_s = "SD"
```

## To Do

- [x] Multi-line ADIF support
- [ ] Add examples
- [x] QSL Manager Support
- [ ] Test ADIF formats of more programs
- [ ] Publish gLabels template
