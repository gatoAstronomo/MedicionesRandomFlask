import requests
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation


def pedirUltimaMedicion(device_name):
    try:
        response = requests.get(f'http://44.197.32.169:8081/mediciones?device_name={device_name}')
        medicion = response.json()
        medicion["epoch_time"] += 3600 * 3
        return medicion
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

def transformarEpochTime(medicion):
    return mdates.date2num(datetime.datetime.fromtimestamp(medicion.get("epoch_time")))

def graficarMediciones(mediciones):
    # Convertir los valores de epoch_time a un formato numérico que se pueda utilizar en el eje de las X
    epoch_times = [transformarEpochTime(medicion) for medicion in mediciones]
    temperatures = [medicion.get("temperature") for medicion in mediciones]

    fig, ax = plt.subplots()
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    line, = ax.plot(epoch_times, temperatures)
    plt.ylim(min(temperatures) - 0.5, max(temperatures) + 0.5)

    ultima_medicion = mediciones[-1]
    primera_medicion = mediciones[0]
    limite_superior = transformarEpochTime(ultima_medicion)
    limite_inferior = transformarEpochTime(primera_medicion)
    ax.set_xlim(limite_inferior, limite_superior)

    plt.title('Temperatura en tiempo real')
    plt.xlabel('Tiempo')
    plt.ylabel('Temperatura (ºC)')

    def actualizar(i):
        try:
            ultima_medicion = pedirUltimaMedicion("Nodo005")
            epoch_times.append(transformarEpochTime(ultima_medicion))
            temperatures.append(ultima_medicion.get("temperature"))
            if ultima_medicion.get("epoch_time") != mediciones[-1].get("epoch_time"):
                mediciones.append(ultima_medicion)
                line.set_xdata([transformarEpochTime(medicion) for medicion in mediciones])
                line.set_ydata([medicion.get("temperature") for medicion in mediciones])
                ax.relim()
                ax.autoscale_view()
                plt.ylim(min(temperatures) - 0.5, max(temperatures) + 0.5)

                ultima_medicion = mediciones[-1]
                primera_medicion = mediciones[0]
                limite_superior = transformarEpochTime(ultima_medicion)
                limite_inferior = transformarEpochTime(primera_medicion)
                ax.set_xlim(limite_inferior, limite_superior)
                
                ax.figure.canvas.draw()
        except Exception as e:
            print(f"Error al actualizar el gráfico: {e}")

    ani = animation.FuncAnimation(fig, actualizar, interval=100)
    plt.show()

mediciones = []
mediciones.append(pedirUltimaMedicion("Nodo005"))

def main():
    graficarMediciones(mediciones)
    """
    while True:
         medicion = pedirUltimaMedicion("Nodo005")
        ultimaMedicion = mediciones[-1]
        if medicion.get("epoch_time") != ultimaMedicion.get("epoch_time"):
            mediciones.append(medicion)
            imprimirMedicion(medicion)
    """
            
if __name__ == "__main__":
    main()