from app import main
from datetime import datetime
import schedule
import time

# Horario de inicio e Término do programa
hora_inicial = "07:45"
hora_final = "23:15"

# Tempo que será executado a função, de 1 em 1 minuto
schedule.every(1).minutes.do(main)

while (
    datetime.today().strftime("%H:%M") > hora_inicial
    and datetime.today().strftime("%H:%M") <= hora_final
):
    if __name__ == "__main__":
        if main() == True:
            schedule.run_pending()
            time.sleep(30)
        else:
            time.sleep(30)
