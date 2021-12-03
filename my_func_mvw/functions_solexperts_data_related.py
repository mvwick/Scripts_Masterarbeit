import pandas as pd


def import_temp_sol(path_DTS_processed = r"..\Alsdorf\Daten\DTS_processed"):
    """"""
    path_to_solexperts = path_DTS_processed + "\..\Solexperts_EGRT"
    filename=r"\alle Messungen_TEMP.txt"

    #encoding= 'unicode_escape': for reading non asci characters
    temp_sol = pd.read_csv(path_to_solexperts + filename, delimiter="\t", index_col=0, encoding= 'unicode_escape')
    temp_sol.index.names = ["Length [m]"]
    temp_sol.index = temp_sol.index.astype(int)
    temp_sol.columns.names = ["Date"]
    temp_sol.columns= pd.to_datetime(temp_sol.columns)
    temp_sol = temp_sol.T

    return temp_sol

def import_solexpert_tlogger(path_DTS_processed = r"..\Alsdorf\Daten\DTS_processed"):
    """"""
    path_to_solexperts = path_DTS_processed + "\..\Solexperts_EGRT"
    filename = "\wagoTemperatur_korigiert.txt"

    tlogger_sol = pd.read_csv(path_to_solexperts + filename, delimiter="\t", index_col=0)
    tlogger_sol.columns.names = ["Dates"]
    tlogger_sol.columns= pd.to_datetime(tlogger_sol.columns)
    tlogger_sol.index=["Watertank"]
    tlogger_sol.index.names = [""]
    tlogger_sol = tlogger_sol.T

    return tlogger_sol