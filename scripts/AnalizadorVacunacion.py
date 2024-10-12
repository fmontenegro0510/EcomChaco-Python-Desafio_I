import csv
import os

class AnalizadorVacunacion:
    def __init__(self, archivo):
        self.datos = self.leer_datos(archivo)
        self.registros_erroneos = []

    def leer_datos(self, archivo):
        datos = []
        with open(archivo, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                datos.append(row)
                print(row)
        return datos

    def validar_datos(self):
        for registro in self.datos:
            if registro['sexo'] not in ['M', 'F']:
                registro['OBSERVACIÓN'] = 'Sexo inválido'
                self.registros_erroneos.append(registro)

    def contar_dosis(self):
        pass

    def guardar_resultados(self):
        pass

if __name__ == "__main__":
    ruta = os.path.join(os.getcwd(), 'data/modelo_muestra.csv')
    analizador = AnalizadorVacunacion(ruta)
    analizador.validar_datos()

