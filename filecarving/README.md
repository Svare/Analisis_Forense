# File Carving

## Descripcion del Programa

Este programa se diseño para recuperar archivos dentro de una unidad de 
almacenamiento, puede recuperar archivos de tipo exe, zip, png, jpg y mp3.

Funciona a traves de una maquina de estados en donde los numeros magicos de
los archivos juegan un papel fundamental, ya que se busca la coincidencia de 
estos y a partir de que se encuetra una de las mismas se tienen dos opciones
para determinar en donde parar, la primera de ellas nos dice que tenemos que
parar por tamaño, cuando se alcance un determinado tamaño paramos y buscamos
otro archivo, la segunda opcion es parar por secuencia de terminacion, en este
caso muchos tipos de archivos tienen secuencias de bytes que indican el fin del
archivo por lo que si se encuentra dicha secuencia sabremos que hemos llegado
al fin del archivo, ejemplos de este tipo de formatos son zip, jpg y png.

## Archivo de Configuracion

El archivo de configuracion tiene la siguiente estructura:

{
    "exe" : [false, ""],
    "zip" : [true, ""],
    "png" : [true, "60K"],
    "jpg" : [false, "300K"],
    "mp3" : [true, "1M"],
    "default": 10
}

Observamos que por cada tipo de archivo tenemos dos elementos, el primero es
un valor booleano si es true va a buscar esos tipos de archivos en el disco que
proporcionemos, si es false no buscara ese tipo de archivo. El segundo es una
cadena de caracteres en donde indicamos que tan grandes queremos los archivos,
el programa trunca el tamaño de los archivos con base en esta cadena, cuando se
especifica una cadena vacia se tienen otros dos casos, para los tipos png, jpg y
zip si se especifica una cadena vacia entonces la condicion de paro sera la
secuencia de bytes de fin de archivo, para el caso de exe y mp3 si se especifica
cadena vacia la condicion de paro sera el valor default que es el numero de
bytes que se desean te tamaño maximo.

## Ejecucion

    python3 file_carving.py config.json disk

    *config.json: archivo de configuracion.
    *disk: el disco o archivo sobre el cual se va a buscar.

# Ejemplo

## Configuracion

![Config](https://raw.githubusercontent.com/Svare/Analisis_Forense/master/ejecucion.JPG)

## Resultado

![Res](https://raw.githubusercontent.com/Svare/Analisis_Forense/master/ejecucion.JPG)

## Abriendo JPG

![JPG](https://raw.githubusercontent.com/Svare/Analisis_Forense/master/ejecucion.JPG)