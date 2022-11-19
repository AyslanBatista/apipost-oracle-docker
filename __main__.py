from time import sleep
from datetime import datetime

from schedule import every
from schedule import repeat
from schedule import run_pending

from app import main

# Horario de inicio e Término do programa
hora_inicial = "07:45"
hora_final = "23:15"

# Tempo que será executado a função, de 1 em 1 minuto
@repeat(every(1).minutes)
def job():
    if __name__ == "__main__":
        main()


while (
    datetime.today().strftime("%H:%M") > hora_inicial
    and datetime.today().strftime("%H:%M") <= hora_final
):

    run_pending()
    sleep(10)