import csv
import os
from datetime import datetime


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
        registros_erroneos = []
        for registro in self.datos:
            observaciones = []

            # Validación de 'sexo'
            if registro.get('sexo') not in ['M', 'F']:
                observaciones.append('Sexo inválido (debe ser M o F)')

            # Validación de 'grupo_etario'
            grupo_etario = registro.get('grupo_etario', '')
            if not isinstance(grupo_etario, str) or not (grupo_etario.startswith('<') or '-' in grupo_etario):
                observaciones.append('Grupo etario no válido')

            # Validación de 'jurisdiccion_residencia_id'
            try:
                int(registro.get('jurisdiccion_residencia_id', ''))
            except ValueError:
                observaciones.append('ID de jurisdicción de residencia no válido (debe ser un número entero)')

            # Validación de 'jurisdiccion_aplicacion_id'
            try:
                int(registro.get('jurisdiccion_aplicacion_id', ''))
            except ValueError:
                observaciones.append('ID de jurisdicción de aplicación no válido (debe ser un número entero)')

            # Validación de la 'fecha_aplicacion'
            fecha = registro.get('fecha_aplicacion', '')
            if not self.validar_fecha(fecha):
                observaciones.append("Fecha de aplicación no válida (debe estar en formato 'YYYY-MM-DD')")

            # Validación de 'vacuna'
            vacuna = registro.get('vacuna', '')
            if not vacuna or not isinstance(vacuna, str):
                observaciones.append('Vacuna no especificada o no válida')

            # Validación de 'cod_dosis_generica'
            cod_dosis = registro.get('cod_dosis_generica', '')
            try:
                cod_dosis = int(cod_dosis)
                if not (1 <= cod_dosis <= 14):
                    observaciones.append('Código de dosis genérica fuera de rango (1-14)')
            except ValueError:
                observaciones.append('Código de dosis genérica no válido (debe ser un número entero)')

            # Validar la relación entre 'cod_dosis_generica' y 'nombre_dosis_generica'
            nombre_dosis = registro.get('nombre_dosis_generica', '').lower()
            if cod_dosis == 3 and '2da' not in nombre_dosis:
                observaciones.append("Inconsistencia entre código y nombre de dosis (debe ser '2da' para código 3)")

            # Validación de 'id_persona_dw'
            try:
                float(registro.get('id_persona_dw', ''))
            except ValueError:
                observaciones.append('ID de persona DW no válido (debe ser un número)')

            # Campos obligatorios no vacíos
            campos_obligatorios = [
                'jurisdiccion_residencia', 'jurisdiccion_aplicacion',
                'depto_residencia', 'depto_aplicacion', 'fecha_aplicacion',
                'lote_vacuna', 'id_persona_dw'
            ]
            for campo in campos_obligatorios:
                if not registro.get(campo):
                    observaciones.append(f"{campo} es un campo obligatorio y está vacío")

            # Si hay observaciones, agregar el registro a registros_erroneos con la observación
            if observaciones:
                registro['OBSERVACIÓN'] = '; '.join(observaciones)
                registros_erroneos.append(registro)

        return registros_erroneos

    def validar_fecha(self, fecha):
        """Valida que la fecha esté en formato 'YYYY-MM-DD'."""
        try:
            anio, mes, dia = fecha.split('-')
            if len(anio) == 4 and len(mes) == 2 and len(dia) == 2:
                anio, mes, dia = int(anio), int(mes), int(dia)
                if 1 <= mes <= 12 and 1 <= dia <= 31:
                    return True
        except ValueError:
            pass
        return False
        
   


    # Función para contar segundas dosis por jurisdicción
    def contar_segundas_dosis(datos):
        segundas_dosis = {}
        for registro in datos:
            if registro['cod_dosis_generica'] == '3':  # Segunda dosis
                jurisdiccion = registro['jurisdiccion_residencia']
                if jurisdiccion not in segundas_dosis:
                    segundas_dosis[jurisdiccion] = 0
                segundas_dosis[jurisdiccion] += 1
        return segundas_dosis

    # Función para contar refuerzos para mayores de 60 años
    def contar_refuerzos_mayores_60(datos):
        total = 0
        for registro in datos:
            if registro['orden_dosis'] == '3' and int(registro['grupo_etario'].split('-')[-1]) >= 60:
                total += 1
        return total

    # Función para guardar registros erróneos
    def guardar_registros_erroneos(registros_erroneos):
        with open('registros_erroneos.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['sexo', 'grupo_etario', 'jurisdiccion_residencia', 'jurisdiccion_residencia_id',
                            'depto_residencia', 'depto_residencia_id', 'jurisdiccion_aplicacion',
                            'jurisdiccion_aplicacion_id', 'depto_aplicacion', 'depto_aplicacion_id',
                            'fecha_aplicacion', 'vacuna', 'cod_dosis_generica', 'nombre_dosis_generica',
                            'condicion_aplicacion', 'orden_dosis', 'lote_vacuna', 'id_persona_dw', 'OBSERVACIÓN'])
            for registro in registros_erroneos:
                writer.writerow(registro)

    # Función para guardar la segunda dosis por jurisdicción
    def guardar_segunda_dosis(segundas_dosis):
        with open('segunda_dosis_por_jurisdiccion.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['jurisdiccion_residencia', 'total_segunda_dosis'])
            for jurisdiccion, total in segundas_dosis.items():
                writer.writerow([jurisdiccion, total])

    # Función para guardar refuerzos mayores de 60
    def guardar_refuerzos_mayores_60(total_mayores_60_refuerzo):
        with open('refuerzos_mayores_60.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['total_mayores_60_refuerzo'])
            writer.writerow([total_mayores_60_refuerzo])

    #TRATAMIENTO DE ERRORES
    # Función para exportar registros erróneos a un archivo CSV con una columna "OBSERVACIÓN"
    def exportar_datos_erroneos(datos_erroneos, encabezados, archivo_salida):
        # Añadir la columna de observación
        encabezados.append('OBSERVACIÓN')
        
        with open(archivo_salida, 'w') as archivo:
            # Escribir el encabezado
            archivo.write(','.join(encabezados) + '\n')
            
            # Escribir los registros erróneos
            for registro in datos_erroneos:
                # Combinar registro con observación
                observacion = registro[-1]  # La observación está en la última posición
                archivo.write(','.join(map(str, registro[:-1])) + ',' + observacion + '\n')
    
if __name__ == "__main__":
    ruta = os.path.join(os.getcwd(), 'data/modelo_muestra.csv')
    analizador = AnalizadorVacunacion(ruta)
    analizador.validar_datos()

