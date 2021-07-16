import configparser

import numpy as np
import csv


def calculate_state_of_charge(current_discharge, time, prev_time, prev_state_of_charge, nominal_capacity,
                              coulomb_efficient):
    """
      Beschreibung:
        State of Charge ist der verfügbare Kapazität in vergleich der Nennkapazität.
        Während der Entladung oder Ladung können unter wissen Coulomb Wirkungsgrad 
        und Strom und bestimmung der Nennkapazität berechnen werden.


      Parameters:
        I ist der Strom in mA
        t ist der Zeitpunkt t\n
        t0 ist der Zeitpunkt t0\n
        soc_t0 zum Zeitpunkt t0\n
        Q_n ist die Nennkapazitaet in mAh0\n
        ce ist der Coulumb Wirkungsgrad [im Bereich 1.0 bis 0.0]\n


      Returns:
        State of Charge fuer den Zeitpunkt t\n
    """
    integral = current_discharge * (time - prev_time) / nominal_capacity

    state_of_charge = prev_state_of_charge - coulomb_efficient * integral

    return state_of_charge


if __name__ == '__main__':
    '''
         Read the program setup from setup.text
         NOTE: if boolean is false please leave the value empty for charge_cycle
     '''

    parser = configparser.ConfigParser()
    parser.read("setup.txt")

    input_filename = parser.get("config", "path")
    output_filename = input_filename + ".out.csv"

    soc_t0 = int(parser.get("config", "state_of_charge"))
    Q_n = int(parser.get("config", "nominal_capacity"))
    ce = float(parser.get("config", "coulomb_efficient"))
    current_charged = int(parser.get("config", "current_charged"))
    laden_zyklus = bool(parser.get("config", "charge_cycle"))

    # Daten einlesen
    output_from_csv = []
    with open(input_filename, 'r+') as in_file:
        print("Start reading csv file from {0}".format(parser.get("config", "path")))

        reader = csv.reader(in_file)

        csv_import = csv.reader(in_file, quoting=csv.QUOTE_NONNUMERIC)
        output_from_csv = list(csv_import)

        # State of charge fuer alle zeitschritte bestimmen
    if laden_zyklus:
        soc = 0.0  # bedenke, 0.0 ist fuer einen lade zyklus
        current = 0.0
    else:
        soc = 1.0  # bedenke, 1.0 ist fuer einen entlade zyklus
        current = current_charged  # ACHTUNG hier noch richtigen wert suchen!

    soc_list = []

    temp_soc = soc_t0

    fileLength = len(output_from_csv)
    for i in range(len(output_from_csv) - 1):
        soc = calculate_state_of_charge(current, output_from_csv[i + 1][0], output_from_csv[i][0], temp_soc, Q_n, ce)
        soc_list.append(soc)
        temp_soc = soc

    print("Creating the report to {0}".format(output_filename))
    # alle berchenten daten abspeichern
    with open(output_filename, 'w+') as out_file:
        out_file.write("StateOfCharge,    StateOfHealth,    StateOfFunction\n")
        for i in range(len(soc_list)):
            out_file.write(str(soc_list[i]))
            out_file.write("\n")
