from multiprocessing import Process
from datan_kerays import collect_data
from data_analysointi import analyze_data

if __name__ == "__main__":
    # Luodaan prosessit
    process1 = Process(target=collect_data)
    process2 = Process(target=analyze_data)

    # Käynnistetään prosessit
    process1.start()
    process2.start()

    # Odotetaan, että prosessit valmistuvat
    process1.join()
    process2.join()

    print("Kaikki tehtävät suoritettu.")