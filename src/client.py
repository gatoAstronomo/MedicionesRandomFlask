import requests
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation


def pedirUltimaMedicion(device_name):
    try:
        response = requests.get(f'http://44.197.32.169:8081/mediciones?device_name={device_name}')
        return response.json()
    except:
        print("no fue posible establecer conexión")
        return {}

def devolverDatos(medicion):
    epoch_time = medicion.get("epoch_time")
    temperature = medicion.get("temperature")
    return epoch_time, temperature

def formatEpochTime(epoch_time):
    dt_object = datetime.datetime.fromtimestamp(epoch_time)
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date

def imprimirMedicion(medicion):
    epoch_time, temperature = devolverDatos(medicion)
    print(f'{formatEpochTime(epoch_time)} {temperature}ºC')

def graficarMediciones(mediciones):
    epoch_times = [medicion.get("epoch_time") for medicion in mediciones]
    temperatures = [medicion.get("temperature") for medicion in mediciones]

    fig, ax = plt.subplots()
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    line, = ax.plot(epoch_times, temperatures)
    plt.ylim(min(temperatures) - 2, max(temperatures) + 2)
    plt.xlim(epoch_times[-len(epoch_times)//60], epoch_times[-1])
    plt.title('Temperatura en tiempo real')
    plt.xlabel('Tiempo')
    plt.ylabel('Temperatura (ºC)')

    def actualizar(i):
        try:
            ultima_medicion = pedirUltimaMedicion("Nodo005")
            if ultima_medicion.get("epoch_time") != mediciones[-1].get("epoch_time"):
                mediciones.append(ultima_medicion)
                line.set_xdata([medicion.get("epoch_time") for medicion in mediciones])
                line.set_ydata([medicion.get("temperature") for medicion in mediciones])
                ax.relim()
                ax.autoscale_view()
                plt.ylim(min(temperatures) - 2, max(temperatures) + 2)
                plt.xlim(epoch_times[-len(epoch_times)//60], epoch_times[-1])
        except Exception as e:
            print(f"Error al actualizar el gráfico: {e}")

    ani = animation.FuncAnimation(fig, actualizar, interval=1000)
    plt.show()


mediciones = []
mediciones.append(pedirUltimaMedicion("Nodo005"))

def mainloop():
    # graficarMediciones(mediciones)
    while True:
        medicion = pedirUltimaMedicion("Nodo005")
        ultimaMedicion = mediciones[-1]
        if medicion.get("epoch_time") != ultimaMedicion.get("epoch_time"):
            imprimirMedicion(medicion)
            mediciones.append(medicion)
        


if __name__ == "__main__":
    mainloop()