from django.test import TestCase



# class TestAdmin():
    # def test_page_returns_correct_html(self):
    #     """ Verifica que la pagina devuelva el html correspondiente"""
    #     request = HttpRequest()
    #     request.user = User.objects.get(username='testadmin')
    #     response = ListaPruebasView.as_view()(request)
    #     expected_html = render_to_string('administracion/lista_pruebas.html', {'prueba_list': Prueba.objects.all()})
    #     print(response.content.title().decode())
    #     self.assertEqual(response.content.decode(), expected_html)


    # def test_pruebas_realizadas(self):
    #     programas = Programa.objects.create(nombre="programa",codigo='123')
    #     recepciones= Recepcion.objects.create(programa=programas,fecha_recepcion=timezone.now(),recepcionista=self.user,estado='Rechazado')
    #     areas = Area.objects.create(nombre="area",programa=programas)
    #     resultados = ResultadoPrueba.objects.create(nombre="resultado")
    #     metodos = Metodo.objects.create(nombre="metodo",objeto="objeto_metodo")
    #     pruebas = Prueba.objects.create(nombre="prueba",area=areas,duracion=12,resultados=resultados,metodos=metodos)
    #     muestras = Muestra.objects.create(registro_recepcion=recepciones, pruebas=pruebas, observacion="ninguna")
    #
    #     pruebas_realizadas = PruebasRealizadas.objects.create(prueba=pruebas, muestra=muestras, estado='Conservación',fecha_pre_analisis=timezone.now(),
    #                                                           observacion_semaforo='none', resultado=resultados, resultado_numerico=12, metodo=metodos,
    #                                                           )
    #
    #     self.assertEqual(pruebas_realizadas.cumplimiento, PruebasRealizadas.CONSERVACION)