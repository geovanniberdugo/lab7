from io import StringIO, BytesIO
import xlsxwriter
import collections
import datetime
import re


def DEBUG(*args):
    print("******************************")
    print([arg for arg in args])
    print("******************************")


class Debug(object):
    """Clase para funciones de debug."""

    INITIAL = 'Escribe el nombre de una variable: \n'

    def __init__(self):
        self._run = True

    def shell(self, *args, **kwargs):
        run = True
        if self._run:
            try:
                while run:
                    var = input(self.INITIAL)
                    if var != 'salir' and var != 'exit':
                        try:
                            if hasattr(self, var):
                                value = getattr(self, var)
                            else:
                                value = eval(var)
                            print(var + ' = ' + value.__str__())
                        except Exception as e:
                            print(e)
                            print("Ha hecho una accion incorrecta")
                    else:
                        break
                        if 'exitall' == var:
                            self._run = False
                        raise KeyboardInterrupt('Salida')
            except KeyboardInterrupt:
                # sigue ejecutanto el programa
                run = False


class Excel(Debug):
    """
    Clase que maneja la creacion de archivos de excel
    """

    START_ROW = 1  # Fila donde inciaria a dibujar en el excel
    START_COL = 1  # Columna donde empezaria a dibujar el excel
    MAXIMUN_TITLE_LENGTH = 27  # define el tamaño maximo que puede tener un titulo
    DEFAULT_ORDER = ['resultado', 'frecuencia', 'porcentaje', 'acumulado']
    # orden de impresion de resultados, de la forma = [(resultado, RESULTADO), (frecuencia, FRECUENCIA)]
    ACEPTED_FOR_TABLE = list(map(lambda x, y: (x, y), DEFAULT_ORDER, [l.upper() for l in DEFAULT_ORDER]))
    DETALLE = ['DETALLE', 'DETALLES']  # variables de 'detalle' para los datos de las hojas aparte
    # INFORMES = [
    #     'tipo_resultado', 'motivo_rechazo', 'muestras_rechazadas',
    #     'cumplimiento_productividad', 'solicitudes_recepcionadas', 'pendiente_aceptacion',
    #     'informes_resultados', 'ingreso_parcial', 'multiconsulta'
    # ]  # nombre de las funciones que deberian llamar a esta clase
    _LETTERS = [x for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']  # letras del abecedario para los formatos

    # patterns
    NUM_PAGES_PATTERN = re.compile(r'(\([\d+]\))')
    DIGIT_PATTERN = re.compile(r'\d+')

    PAGE_NAME = 'title'  # titulo, variable string

    # Formulas
    AVERAGE = '=average({0}:{1})'
    SUM = '=sum({0}:{1})'

    MAPA = {
        'radicado': {
            'tipo_resultado': 'muestra.registro_recepcion.radicado',
            'motivo_rechazo': 'registro_recepcion.radicado',
            'muestras_rechazadas': 'registro_recepcion.radicado',
            'cumplimiento_productividad': 'radicado',
            'solicitudes_recepcionadas': 'radicado',
            'productividad_recepcion': 'radicado',
            'pendiente_aceptacion': 'radicado',
            'informes_resultados': 'radicado',
            'ingreso_parcial': 'radicado',
            'multiconsulta': 'muestra.registro_recepcion.radicado',
        },
        'recepcion': {
            'tipo_resultado': 'muestra.registro_recepcion.fecha_recepcion',
            'motivo_rechazo': 'registro_recepcion.fecha_recepcion',
            'muestras_rechazadas': 'registro_recepcion.fecha_recepcion',
            'cumplimiento_productividad': 'recepcion',
            'solicitudes_recepcionadas': 'fecha_recepcion',
            'productividad_recepcion': 'fecha_recepcion',
            'pendiente_aceptacion': 'fecha_recepcion',
            'informes_resultados': 'fecha_recepcion',
            'ingreso_parcial': 'fecha_recepcion',
            'multiconsulta': 'muestra.registro_recepcion.fecha_recepcion',
        },
        'resultados': {
            'tipo_resultado': 'ultima_modificacion',
            'motivo_rechazo': 'Ninguno',
            'multiconsulta': 'ultima_modificacion',
        },
        'solicitante': {
            'tipo_resultado': 'muestra.registro_recepcion.solicitante',
            'motivo_rechazo': 'registro_recepcion.solicitante',
            'productividad_recepcion': 'solicitante',
            'muestras_rechazadas': 'registro_recepcion.solicitante',
            'cumplimiento_productividad': 'solicitante',
            'solicitudes_recepcionadas': 'solicitante',
            'pendiente_aceptacion': 'solicitante',
            'informes_resultados': 'solicitante',
            'ingreso_parcial': 'solicitante',
            'multiconsulta': 'muestra.registro_recepcion.solicitante',
        },
        'corresponde': {
            'solicitudes_recepcionadas': 'nombre',
            'pendiente_aceptacion': 'nombre',
            'informes_resultados': 'nombre',
        }
    }  # Diccionario de llamadas a la base de datos de acuerdo a la funcion

    def __init__(self, titulo=None, data=None, graphic=None, function=None, *args, **kwargs):
        super(self.__class__, self).__init__()
        self._pages = {}  # guardara las paginas de acuerdo al tamaño de data
        self.pages = {}  # guarda las paginas por datos
        self.data = data  # datos, lista de diccionario o vacio
        self._titulo = titulo  # titulo principal del grafico
        self.function = function  # funcion de la cual es llamada la clase
        self.type_chart = None  # se define el tipo de chart
        self._charts = {}  # guarda los charts creados
        self.calculated_order = []  # guarda el orden calculado por el programa

        # self.titulo = self._titulo[0:27]  # titulo con tamaño maximo para la hoja principal
        self.last_row = self.START_ROW  # se inicializan las filas
        self.last_col = self.START_COL  # se inicializan las columnas

        self.schema = kwargs.pop('schema', None)  # se intenta obtener el orden en los graficos
        if self.schema is not None:
            self.MAPA = collections.OrderedDict([(z, self.MAPA[z]) for z in self.schema])  # se ordena por el esquema
        else:
            self.MAPA = collections.OrderedDict(sorted(self.MAPA.items()))  # se ordena por orden alfabetico

        # se genera el buffer
        self._buffer = BytesIO()
        # se crea el libro de trabajo con el buffer de bytes
        self.workbook = xlsxwriter.Workbook(self._buffer)

        # se crean las configuraciones que vengan de la instancia de la clase
        kwargs.update(_titulo=self._titulo)
        self.config(**kwargs)

        if self.data is not None:
            self.generar_tabla()

    @staticmethod
    def format_data(value):
        """Funcion statica para formatear los datos, con un orden"""
        if isinstance(value, str):
            # si es un string, retorna el valor en mayuscula
            return value.upper()
        elif isinstance(value, int):
            # si es un entero, retorna el valor
            return value
        elif isinstance(value, float):
            # si es flotante, retorna el flotante con 2 decimas
            return float("%.2f" % value)
        elif isinstance(value, datetime.datetime):
            # si es una fecha, retorna en el formato 'AAAA-MM-DD'
            # return datetime.datetime.strptime(value, '%Y-%m-%d').date()
            return value.strftime('%Y-%m-%d')
        elif callable(value):
            # si es una funcion, retorna el nombre de la funcion
            return value.__name__
        try:
            # de lo contrario, intentara, retornar el objeto en string
            return value.__str__()
        except:
            # lanza una excepcion con el tipo de dato no encontrado
            raise ValueError('DataType found not expected "%s"' % value.__class__.__name__)

    def get_attr(self, obj, value):
        """
        Funcion que retorna el atributo deseado, y de no ser encontrado el atributo, retorna
        el atributo como parametro que fue buscado
        """
        _attrs = value.split('.')  # se separa el string por puntos
        for attr in _attrs:
            # obtiene el valor del atributo
            val = getattr(obj, attr, False)
            if val is False:
                # sale del ciclo
                break
            # sobreescribe el objeto, es una forma de avanzar por cada atributo
            obj = val
        if val is False:
            # retorna el patron de busqueda
            return value
        # retorna lo encontrado
        return self.format_data(val)

    def write(self):
        """
        Funcion que crea un documento de excel.
        """
        # cierra el documento
        self.close()
        return self._buffer.getvalue()  # retorna el contenido de el libro

    def close(self):
        """
        Metodo que cierra el documento de excel.
        """
        # Metodo que intenta cerrar el libro
        try:
            return self.workbook.close()
        except TypeError:
            return self.workbook.close()
        finally:
            pass

    def write_line(self, text, *args, **kwargs):
        """
        Metodo para escribir de acuerdo a posicion en fila/columna.
        """
        # se obtiene un estilo, o se deja uno por defecto
        style = kwargs.pop('style', None) or self.style_body
        # se obtienen las filas y columnas o se deja por defecto
        row = kwargs.pop('row', None) or self.last_row
        col = kwargs.pop('col', None) or self.last_col

        # se obtiene el tamaño
        length = kwargs.pop('length', None)

        # se obtiene la hoja de trabajo actual
        sheet = self.get_actual_sheet()

        # se escribe en la posicion indicada
        sheet.write(row, col, self.format_data(text), style)

        # se corrigen los formatos para los tamaños de los campos
        if isinstance(self.format_data(text), str):
            length = length or (2 * len(self.format_data(text)))
        else:
            length = length or (2 * 6)
        # se corrige el formato con un tamaño unico
        sheet.set_column('{0}:{0}'.format(self._LETTERS[col]), length)

    def get_actual_sheet(self, assign=None):
        """Retorna la hoja de trabajo actual Y/O Asigna una."""
        if assign is None:
            # si no hay nada que asignar
            if not self._actual_sheet:
                # si _actual_sheet no fue encontrado, retorna la primera pagina creada
                self._actual_sheet = self._pages[self.titulo]
        else:
            # si no, retorna la pagina que se quizo escoger
            if assign not in self._pages:
                # lanza un error
                raise IndexError(
                    'Pagina "%s"" no está entre las paginas "%s"' % (assign, ', '.join([x for x in self._pages]))
                )
            self._actual_sheet = self._pages[assign]
        # retorna la pagina actual
        return self._actual_sheet

    def _add_sheet(self, name):
        """Agrega una pagina al workbook."""
        # se sacan las paginas con similitudes
        pages = [x for x in self._pages if x.startswith(name)]
        # si no hay paginas similares
        if len(pages) == 0:
            # se crea una pagina inicial
            self._pages[name] = self.workbook.add_worksheet(name)
            # se crea la pagina para la data
            self.pages[name] = self._pages[name]
            # se devuelve la pagina
            return self._pages[name]
        else:
            length = len(pages)

            if length == 1:
                pagina = pages[0]
                changed_name = pagina + '({})'.format(length)
                # self._pages[changed_name] = self._pages.pop(pagina)
                # self._pages[changed_name].name = changed_name
                self._pages[pagina].name = changed_name
                if pagina in self.pages:
                    # self.pages[changed_name] = self.pages.pop(pagina)
                    # self.pages[changed_name].name = changed_name
                    self.pages[pagina].name = changed_name

                # se busca si la pagina tiene charts
                if pagina in self._charts:
                    # se saca el chart de la pagina
                    chart = self._charts.pop(pagina)
                    # se borra el chart
                    del chart['chart']
                    # self.workbook.charts.remove(chart['chart'])
                    # se vuelve a dibujar otro chart con la informacion ya dada
                    self.draw_chart(
                        order=[x for x in self.ACEPTED_FOR_TABLE if x[0].lower() in chart['data'][0]],
                        data=chart['data'],
                        sheet=pagina  # se asigna a la pagina nueva
                    )

            new_name = name + '({})'.format(length + 1)
            self._pages[new_name] = self.workbook.add_worksheet(new_name)
            self.pages[new_name] = self._pages[new_name]
            return self._pages[new_name]

            # # se saca la ultima página
            # pagina = pages.pop()
            # # se pasa por el filtro a ver si es una pagina repetida
            # regex = self.NUM_PAGES_PATTERN.search(pagina)
            # # si encontró algo
            # if regex is not None:
            #     regex = regex.group()
            #     # saca el numero de pagina
            #     digit = self.DIGIT_PATTERN.search(regex).group()
            #     # crea un nuevo nombre reemplazando el valor anterior, por un nuevo valor
            #     new_name = pagina.replace(digit, str(int(digit) + 1))
            #     # crea la nueva pagina
            #     self._pages[new_name] = self.workbook.add_worksheet(new_name)
            #     self.pages[new_name] = self._pages[new_name]
            #     # retorna la nueva pagina
            #     return self._pages[new_name]
            # else:
            #     # nombre cambiado
            #     changed_name = pagina + '(1)'
            #     # si no encontró nada en el filtro, reemplaza la pagina como si fuera la primera
            #     self._pages[changed_name] = self._pages.pop(pagina)
            #     self._pages[changed_name].name = changed_name
            #     self.pages[changed_name] = self.pages.pop(pagina)
            #     self.pages[changed_name].name = changed_name

            #     # se busca si la pagina tiene charts
            #     if pagina in self._charts:
            #         # se saca el chart de la pagina
            #         chart = self._charts.pop(pagina)
            #         # se borra el chart
            #         del chart['chart']
            #         # self.workbook.charts.remove(chart['chart'])
            #         # se vuelve a dibujar otro chart con la informacion ya dada
            #         self.draw_chart(
            #             order=[x for x in self.ACEPTED_FOR_TABLE if x[0].lower() in chart['data'][0]],
            #             data=chart['data'],
            #             sheet=self._pages[changed_name].name  # se asigna a la pagina nueva
            #         )
            #     # hace recursion
            #     return self._add_sheet(name)

    def add_sheets(self):
        """Agrega las paginas a el workbook"""
        if self.data is None:  # verifica que data no esté vacio
            raise TypeError('"data" no puede ser None')
        if isinstance(self.data, list):  # si es una lista
            for dicc in self.data:
                # se agrega una pagina por cada resultado encontrado en data
                if 'resultado' in dicc:
                    self.RESULTADO = 'resultado'
                elif 'Resultado' in dicc:
                    self.RESULTADO = 'Resultado'
                else:
                    # se lanza una excepcion
                    raise IndexError('"Resultado" or "resultado" not found in %s' % dicc.__str__())
                sheet = self._add_sheet(dicc[self.RESULTADO][0:self.MAXIMUN_TITLE_LENGTH])
                dicc[self.PAGE_NAME] = sheet.name
        else:
            # se lanza una excepcion
            raise NotImplementedError('Solo se aceptan listas para data')

    def generar_titulo(self, titulo, posicion):
        """Metodo para generar titulos."""
        # espera recibir una posicion en string, y genera un titulo, con campos unidos
        self.get_actual_sheet().merge_range(posicion, titulo, self.style_title)

    def get_string_position(self, col=None, row=None):
        """Retorna la posicion en string de acuerdo a el formato de Excel."""
        # si no hay col o row, las inicializa a default
        if col is None:
            col = self.START_COL
        if row is None:
            row = self.START_ROW
        # retorna un string de la forma 'A1'
        return '{0}{1}'.format(self._LETTERS[col], row + 1)

    def generar_tabla(self, data=None, row=None, col=None, **kwargs):
        """
        Metodo para generar una tabla. Usualmente este método se encarga de escribir
        el encabezado de la tabla, y a partir de otros metodos genera los otros campos
        con la informacion.
        """
        # se verifican que haya data para generar las tablas
        if data is None and self.data is None:
            # si no hay data
            raise TypeError('"data" no puede ser None')
        elif data is not None:
            # se asigna la nueva data
            # self.data = data
            kwargs.update({'data': data})
            self.config(**kwargs)

        # se crea la primera pagina
        self._actual_sheet = self._add_sheet(self.titulo)
        self.titulo = self._actual_sheet.name

        # se agregan las hojas
        self.add_sheets()

        # se recorre cada hoja
        for sheet in self.pages:
            actual_sheet = self.get_actual_sheet(sheet)  # se selecciona la hoja actual
            self.normalize_fields()  # se resetean las filas y columnas al defecto
            data = self.data

            for info in data:
                if sheet != self.titulo:
                    # si no es la primera hoja, buscará el detalle
                    if info[self.PAGE_NAME] == sheet:
                        # se guarda la informacion
                        INFO = info
                        # se sale del ciclo
                        break

            if sheet == self.titulo:  # entra en la primera página
                # order = self.ACEPTED_FOR_TABLE
                order = [x for x in self.ACEPTED_FOR_TABLE if x[0].lower() in data[0]]  # el orden depende de los parametros de la lista
                self.calculated_order = order
                # se agrega el titulo general
                titulo = self._titulo
            else:  # cualquier otra pagina
                # order = self._schema  # el orden depende de esta lista
                detalle = [x.lower() for x in self.DETALLE if x.lower() in INFO][0]  # se consigue la variable de detalle
                # si los detalles son una lista
                if isinstance(INFO[detalle], list) and isinstance(INFO[detalle][0], dict):
                    # buscará las llaves del primer diccionario de detalles con el orden del schema
                    order = [
                        x for x in self._schema
                        if self.MAPA[x.lower()][self.format_data(self.function)] in INFO[detalle][0]
                    ]
                else:
                    # el orden será el schema
                    order = self._schema
                titulo = None
                for info in data:
                    if info[self.PAGE_NAME] == sheet:
                        # se busca un titulo
                        titulo = info[self.RESULTADO].upper()

            # se agrega el titulo a la hoja
            if titulo is not None:
                self.generar_titulo(
                    titulo, '{0}:{1}'.format(
                        self.get_string_position(
                            col=self.last_col,
                            row=self.last_row
                        ),
                        self.get_string_position(
                            col=self.last_col + len(order) - 1,
                            row=self.last_row
                        )
                    )
                )
                self.normalize_fields(row=self.last_row + 1)  # agrega una fila, y vuelve al inicio la columna

            # se agrega la matriz de tamaño
            self.MATRIZ = []

            # se agregan los encabezados de las tablas
            for title in order:  # se recorre en el orden indicado
                if isinstance(title, tuple):
                    text = title[1].upper()
                else:
                    text = title.upper()
                # se escribe la linea
                self.write_line(text, style=self.style_header)
                # se agrega el tamaño de acuerdo a la palabra
                self.MATRIZ.append(len(self.format_data(text)))
                # se agrega una columna
                self.last_col += 1
            # se suma una fila
            self.normalize_fields(row=self.last_row + 1)

            _pass = False
            if sheet == self.titulo:  # si es la primera hoja
                for info in data:
                    # inserta los datos del resumen
                    self._insert_data_by_dict(info, order=order)
                    self.normalize_fields(row=self.last_row + 1)
                _pass = True
                self.add_total_row(order=order)
                self.draw_chart(order=order)
            else:
                # si no, busca los datos de la pagina actual
                if INFO[self.PAGE_NAME] == sheet:
                    # inserta los datos de las hojas de detalles
                    self._insert_data_by_queryset(INFO[detalle])
                else:
                    _pass = True
            if not _pass:
                self.normalize_fields(row=self.last_row + 1)

    def _insert_data_by_dict(self, data, order=None):
        """Inserta los datos en la tabla principal"""
        # data is a 'dict' instances
        if order is None:
            order = self.ACEPTED_FOR_TABLE  # se define el orden

        for word in order:
            try:
                if isinstance(word, tuple):
                    _word = data[word[0].lower()]
                else:
                    _word = data[word.lower()]
                # se asigna el tamaño
                self.update_column_length(word)
            except:
                raise ValueError('Asegurate de enviar todas las llaves en minuscula para %s' % data.__str__())
            self.write_line(self.format_data(_word))
            self.last_col += 1

    def _insert_data_by_queryset(self, detalles):
        """Inserta los valores de acuerdo a la tabla en las hojas de detalles."""
        # self.normalize_fields(row=False)
        entering_row = self.last_row
        for title in self._schema:
            # self.normalize_fields(row=False)
            self.last_row = entering_row
            for detalle in detalles:
                if isinstance(detalle, dict):
                    try:
                        value = self.format_data(detalle[self.MAPA[title.lower()][self.format_data(self.function)]])
                    except KeyError:
                        continue
                else:
                    value = self.get_attr(detalle, self.MAPA[title.lower()][self.format_data(self.function)])
                self.write_line(value)
                #  se corrige el tamaño
                self.update_column_length(value)
                self.last_row += 1
            self.last_col += 1

    def normalize_fields(self, col=True, row=True):
        """Metodo para volver a la ultima fila y columna a su posicion inicial"""
        # si es un entero
        if isinstance(col, int) and not isinstance(col, bool):
            # se setea la ultima columna a el valor
            self.last_col = col
        else:
            # si es un bool
            if col is True:
                # se resetea a default
                self.last_col = self.START_COL
        # si es un entero
        if isinstance(row, int) and not isinstance(row, bool):
            # se sete la ultima fila a el valor
            self.last_row = row
        else:
            # si es un bool
            if row is True:
                # se resetea a default
                self.last_row = self.START_ROW

        if self.last_row is True or self.last_col is True:
            raise ValueError("self.last_row is: %d and self.last_col is: %d" % (self.last_row, self.last_col))

    def get_chart(self, _type):
        """Metodo que retorna un chart."""
        return self.workbook.add_chart({'type': _type})

    def draw_chart(self, order, **kwargs):
        """Dibuja un Chart"""
        # if not hasattr(self, 'graphic_data'):
        #     raise NotImplementedError('No se han enviado datos para generar un gráfico')
        # pass
        data = kwargs.pop('data', None) or self.data
        sheet = self.get_actual_sheet(kwargs.pop('sheet', None))
        type = self.type_chart or 'pie'

        chart = self.get_chart(type)

        # Configure the series. Note the use of the list syntax to define ranges:
        TITULO = 1
        ENCABEZADO = 1
        END_COL = self.START_COL + len(order)
        chart.add_series({
            'name': 'Serie 1',
            'categories': [
                sheet.name,
                self.START_ROW + TITULO + ENCABEZADO,
                self.START_COL + order.index([x for x in order if x[0] == 'resultado'][0]),
                (self.START_ROW + TITULO + ENCABEZADO) + (len(data) - 1),
                self.START_COL + order.index([x for x in order if x[0] == 'resultado'][0])
            ],
            'values': [
                sheet.name,
                self.START_ROW + TITULO + ENCABEZADO,
                self.START_COL + order.index([x for x in order if x[0] == 'frecuencia'][0]),
                (self.START_ROW + TITULO + ENCABEZADO) + (len(data) - 1),
                self.START_COL + order.index([x for x in order if x[0] == 'frecuencia'][0]),
            ],
        })

        # Add a title.
        chart.set_title({'name': self._titulo})

        # Set an Excel chart style. Colors with white outline and shadow.
        chart.set_style(10)

        # Insert the chart into the worksheet (with an offset).
        sheet.insert_chart(
            self.get_string_position(col=END_COL + 2, row=self.START_ROW),
            chart,
            {'x_offset': 25, 'y_offset': 10}
        )

        self._charts[sheet.name] = {
            'chart': chart,
            'data': data
        }

    def add_total_row(self, fields=None, **kwargs):
        """Metodo para agregar un una fila de total una vez se haya creado la tabla"""

        order = kwargs.pop('order', None) or self.calculated_order or self.ACEPTED_FOR_TABLE  # se busca el orden
        default = (x[0] for x in order if x[0].lower() in ['frecuencia', 'porcentaje'])  # ('frecuencia', 'porcentaje')

        if fields is None:  # si no hay campos especificos a los cuales agregarle una sumatoria usa por defecto
            fields = [x for x in default if x.lower() in self.data[0]]  # se asegura que esten en data

        sheet = self.get_actual_sheet(kwargs.pop('sheet', None))  # se escoge la hoja actual, o la deseada

        self.normalize_fields(row=self.last_row)  # no se agrega + 1, porque por defecto ya está en una nueva fila

        ROW = kwargs.pop('row', None) or self.last_row  # a partir de esta fila, se empieza a escribir

        for field in fields:
            TUPLE = tuple()  # se crea una tupla para pasar por valores posicionales

            for indx, title in enumerate(order):  # se recorre por index
                if title[0] == field:  # si el orden corresponde al campo que se escogio
                    _col = self.START_COL + indx  # se saca la columna donde esta el campo
                    _start = self.get_string_position(
                        col=_col,
                        row=self.START_ROW + 2
                    )  # se saca en string, donde empieza
                    _end = self.get_string_position(
                        col=_col,
                        row=self.START_ROW + 1 + len(self.data)
                    )  # se saca en string, donde termina
                    TUPLE = (_start, _end, _col)  # se agrega en la tupla
            if TUPLE:  # si la tupla no llegó vacia
                # escribe la formula en la hoja
                sheet.write_formula(
                    ROW, TUPLE[2], self.SUM.format(*TUPLE), self.style_body
                )

    def update_column_length(self, word):
        """Metodo para solucionar los problemas con las columnas que no se expanden bien"""
        index = self.last_col - (self.START_COL)  # se busca el indice de la columna
        if self.MATRIZ[index] < len(self.format_data(word)):
            self.MATRIZ[index] = len(self.format_data(word))

        for indx, size in enumerate(self.MATRIZ):
            self.get_actual_sheet().set_column('{0}:{0}'.format(self._LETTERS[indx + self.START_COL]), size)

    def config(self, **kwargs):
        """Metodo de configuraciones generales de la clase"""

        __protected__ = [
            '_LETTERS', 'INFORMES', '_buffer', 'workbook'
        ]  # atributos protegidos

        __accepted__ = [
            'order', 'type'
        ]  # atributos aceptados

        for arg in kwargs:
            # para cada argumento
            if hasattr(self, arg) and arg not in __protected__ or arg in __accepted__:  # si existe el atributo y no está protegido
                if not callable(getattr(self, arg, None)):  # si no es un metodo de la clase
                    try:
                        if hasattr(self, arg):
                            setattr(self, arg, kwargs[arg])  # setea el argumento al valor escogido
                        if arg == 'data':
                            self.pages = {}
                            self.calculated_order = []
                        elif arg == '_order':
                            self.DEFAULT_ORDER = kwargs[arg]
                            self.ACEPTED_FOR_TABLE = list(
                                map(lambda x, y: (x, y), self.DEFAULT_ORDER, [l[1] for l in self.ACEPTED_FOR_TABLE])
                            )
                        elif arg == 'order':
                            # self.ACEPTED_FOR_TABLE = kwargs[arg]
                            self.ACEPTED_FOR_TABLE = list(map(lambda x, y: (x, y), self.DEFAULT_ORDER, kwargs[arg]))
                        elif arg == 'type':
                            self.type_chart = kwargs[arg]
                    except AttributeError:
                        pass
                else:
                    raise AttributeError('No se puede configurar %s, porque es un método' % arg.__str__())

        # configuraciones
        self.titulo = self._titulo[0:self.MAXIMUN_TITLE_LENGTH]
        self.data = self.data or None

        self.INFORMES = []
        for key in self.MAPA:
            for informe in self.MAPA[key]:
                # se agregan los informes aceptados gracias a MAPA
                self.INFORMES.append(informe)

        # si no se ha definido una funcion
        if 'function' not in kwargs and self.function is None:
            raise ValueError('No se ha definido una funcion para trabajar')
        elif self.function.__name__ not in self.INFORMES:
            raise NameError(
                'No hay soporte para la funcion "%s", asegurate de enviar un diccionario con el atributo MAPA' %
                self.function.__name__
            )

    @property
    def _schema(self):
        """Retrona el esquema con el que se trabajara"""
        if self.schema:  # si hay esquema
            return self.schema  # se retorna el esquema existente
        # se crea un esquema, basado en la funcion
        return [x for x in self.MAPA if self.format_data(self.function) in self.MAPA[x]]

    @property
    def style_title(self):
        return self.workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

    @property
    def style_header(self):
        return self.workbook.add_format({
            'bg_color': '#F0F0F0',
            'color': 'black',
            'align': 'center',
            'valign': 'top',
            'border': 1,
            'font_size': 10.5
        })

    @property
    def style_body(self):
        return self.workbook.add_format({
            'bg_color': '#F7F7F7',
            'color': 'black',
            'align': 'center',
            'valign': 'top',
            'border': 1,
            'italic': True,
            'font_size': 10.5
        })
