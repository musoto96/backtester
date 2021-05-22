# Moving Average Backtester

## Configuración
Para poder utilizar el extractor de precios editar 
script de **api_credentials.py** con credenciales.

## Extracción de precios
Extraer datos históricos usando **price_extractor.py**

## Backtesting
Realizar prueba de backtesting con **ma_backtest.py**

## Notas:
El script de backtesting imprime a la terminal cada una de las operaciones si el parametro `quiet=False`, si queremos guardar los resultados, se tiene que [redireccionar la salida](https://en.wikipedia.org/wiki/Redirection_(computing)) con el operador **>** tanto en windows como linux, e.g.

Linux:<br>
`python3 ma_backtester > saved_results/resultados.txt`
