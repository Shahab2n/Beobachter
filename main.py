import configparser

import numpy as np
import csv


def StateOfCharge(I, t, t0, soc_t0, Q_n, ce):
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
    state_of_charge = 0.0

    integral = I * (t - t0) / Q_n

    state_of_charge = soc_t0 - ce * integral

    return state_of_charge

    # def StateOfHealth(R_Eol, R_init, U_OCV, U_bat, I_Pulse):
    """
      Beschreibung:
        State of Health ist der Grad der Batterieverschlechterung. Das wurde nach mehrere zyklys
        und über lange Zeit durch Berechnung der Innenwiederstand der Batterie bestimmen.


      Parameters:
        R_Eol ist den Innenwiderstand am Ende der Lebensdauer der Batterie in Ohm
        R_init ist der anfänglichen Batterie-Innenwiderstand in Ohm
        U_OCV ist Open Circuit Voltage für die Leerlaufspannungdie in Volt in Bestimmte SOC und Zeitpunkt t
        U_bat ist Spannung der Batterie in Volt
        I_Pulse ist der angelegte Strom in A
    """
    # R_b ist Innenwiderstand der Batterie in Ohm
    R_b = (U_OCV - U_bat) / I_Pulse

    SOH = (R_Eol - R_b) / (R_Eol - R_init)
    return SOH

    # def StateOfFunktion(U_OCV, t, I_max, R_01, R_02, Q_n):
    """
      Beschreibung:
        State of Function ist der Ausgangsleistung der Batterie. Nach Bestimmung der Strom und Innewiederstand
        der Batterie unter unterschiedlichen Zeitpunkten können der SOF durch Berechnung der SOP der Anfang und
        SOP während des Betriebs berechnen. 


      Parameters:
        R_01 ist Innenwiderstand der Batterie in Ohm
        R_02 ist Innenwiderstand der Batterie in Ohm
        U_OCV ist Open Circuit Voltage für die Leerlaufspannungdie in Volt in Bestimmte SOC un Zeitpunkt t
        V_bat ist Spannung der Batterie in Volt
        I_max ist der maximale Strom in A
        t ist der Zeitpunkt in Stunden
        Q_n
    """
    i_max_t = np.log(t * I_max)

    # U_max/min ist die Abschaltspannung der Batterie in Volt
    U_max_min = U_OCV + i_max_t + R_01 * I_max

    # SOP_init ist der anfängliche State of Power in Watt
    SOP_init = Q_n * U_max_min * I_max

    U_max_min = U_OCV + i_max_t ** 2 + i_max_t + R_02 * I_max
    # SOP ist State of Power in Watt
    SOP = Q_n * U_max_min * I_max

    SOF = SOP / SOP_init
    return SOF


if __name__ == '__main__':
    input_filename = "./sample-data/Dischargemode-3500mAh.csv"
    output_filename = input_filename + ".out.csv"

    parser = configparser.ConfigParser()
    parser.read("setup.txt")

    soc_t0 = int(parser.get("config", "state_of_charge"))
    Q_n = int(parser.get("config", "nominal_capacity"))
    ce = float(parser.get("config", "coulomb_efficient"))
    current_charged = int(parser.get("config", "current_charged"))
    laden_zyklus = bool(parser.get("config", "charge_cycle"))

    # Daten einlesen
    output_from_csv = []
    with open(input_filename, 'r+') as in_file:
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
        soc = StateOfCharge(current, output_from_csv[i + 1][0], output_from_csv[i][0], temp_soc, Q_n, ce)
        soc_list.append(soc)
        temp_soc = soc

    # State of health fuer alle zeitschritte bestimmen
    #  soh_list = []
    #  for i in range(len(output_from_csv)):
    #    soh_list.append(0.0)

    # State of function fuer alle zeitschritte bestimmen
    #  sof_list = []
    #  for i in range(len(output_from_csv)):
    #    sof_list.append(0.0)

    # alle berchenten daten abspeichern
    with open(output_filename, 'w+') as out_file:
        out_file.write("StateOfCharge,    StateOfHealth,    StateOfFunction\n")
        for i in range(len(soc_list)):
            out_file.write(str(soc_list[i]))
            out_file.write("\n")
