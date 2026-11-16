import copy
import io
import itertools
from pathlib import Path
import re
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lector_mt import leer_especificacion, ErrorFormato
from validador_mt import cargar_especificacion, validar_especificacion, ErrorValidacion
from simulador_mt import MaquinaTuring
from salida_mt import ejecutar, generar_salida
BASE = Path(__file__).resolve().parents[1]


class Integracion(unittest.TestCase):
    def setUp(self):
        self.d, self.t = cargar_especificacion(BASE/'especificacion_aceptacion.txt')

    def maquina(self, cadena):
        d=copy.deepcopy(self.d);d['cadena']=list(cadena)
        return MaquinaTuring(d,self.t)

    def test_archivos_incluidos_validos(self):
        for p in BASE.glob('especificacion*.txt'):
            with self.subTest(p=p.name):cargar_especificacion(p)

    def test_aceptacion_13_pasos_y_parada_idempotente(self):
        m=self.maquina('0011')
        self.assertEqual(ejecutar(m,100,io.StringIO()),('aceptacion',13))
        antes=m.configuracion()
        self.assertFalse(m.paso())
        self.assertEqual(m.configuracion(),antes)
        self.assertEqual(m.pasos,13)

    def test_rechazos_y_vacia(self):
        for cadena,pasos in [('001',8),('01011',5),('',1)]:
            with self.subTest(cadena=cadena):
                self.assertEqual(ejecutar(self.maquina(cadena),100,io.StringIO()),('rechazo',pasos))

    def test_ciclo_repite_configuracion(self):
        m=self.maquina('10');m.paso()
        antes=(m.configuracion(),m.cabezal)
        m.paso();m.paso()
        self.assertEqual((m.configuracion(),m.cabezal),antes)
        salida=io.StringIO()
        self.assertEqual(ejecutar(m,10,salida)[0],'limite')
        self.assertIn('No demuestra un ciclo infinito',salida.getvalue())

    def test_limite_exacto_no_oculta_aceptacion(self):
        self.assertEqual(ejecutar(self.maquina('0011'),13,io.StringIO()),('aceptacion',13))
        self.assertEqual(ejecutar(self.maquina('0011'),12,io.StringIO()),('limite',12))

    def test_limite_cero_y_negativo(self):
        self.assertEqual(ejecutar(self.maquina('0'),0,io.StringIO()),('limite',0))
        with self.assertRaises(ValueError):ejecutar(self.maquina('0'),-1,io.StringIO())

    def test_4095_cadenas(self):
        for n in range(12):
            for simbolos in itertools.product('01',repeat=n):
                w=''.join(simbolos);m=self.maquina(w)
                resultado,_=ejecutar(m,200,io.StringIO())
                esperado='limite' if w.startswith('1') else ('aceptacion' if re.fullmatch(r'0+1+',w) and w.count('0')==w.count('1') else 'rechazo')
                self.assertEqual(resultado,esperado,w)

    def test_cinta_no_cruza_borde_izquierdo(self):
        d=copy.deepcopy(self.d)
        t=[list(x) for x in self.t]
        for x in t:
            if x[:2]==['q1','0']:x[2:]=['q1','0','L']
        m=MaquinaTuring(d,t)
        for _ in range(5):m.paso()
        self.assertEqual(m.cabezal,0)

    def test_m2(self):
        d,t=cargar_especificacion(BASE/'especificacion_m2.txt')
        for n in (1,2,4,8,3,5,6):
            d['cadena']=list('0'*n)
            resultado,_=ejecutar(MaquinaTuring(d,t),500,io.StringIO())
            self.assertEqual(resultado,'aceptacion' if n in (1,2,4,8) else 'rechazo')

    def test_transicion_faltante_y_duplicada(self):
        for t in (self.t[:-1],self.t+[self.t[0]]):
            with self.assertRaises(ErrorValidacion):validar_especificacion(self.d,t)

    def test_simbolo_y_estado_invalidos(self):
        d=copy.deepcopy(self.d);d['cadena']=['2']
        with self.assertRaises(ErrorValidacion):MaquinaTuring(d,self.t)
        t=copy.deepcopy(self.t);t[0][2]='inexistente'
        with self.assertRaises(ErrorValidacion):MaquinaTuring(self.d,t)

    def test_exportacion(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'salida.txt'
            self.assertEqual(generar_salida(self.maquina('0011'),p,100),('aceptacion',13))
            lineas=p.read_text(encoding='utf-8').splitlines()
            self.assertEqual(lineas[0],'q1 0011')
            self.assertEqual(len([l for l in lineas if l and not l.startswith('Resultado:')]),14)

    def test_formato_duplicado_y_texto_tras_seccion(self):
        original=(BASE/'especificacion_aceptacion.txt').read_text(encoding='utf-8')
        for texto in (original+'\ntransiciones:\n',original.replace('transiciones:','transiciones: q1 0 q2 x R')):
            with tempfile.TemporaryDirectory() as folder:
                p=Path(folder)/'invalido.txt';p.write_text(texto,encoding='utf-8')
                with self.assertRaises(ErrorFormato):leer_especificacion(p)


if __name__=='__main__':unittest.main()
