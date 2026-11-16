import copy
import io
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validador_mt import cargar_especificacion
from simulador_mt import MaquinaTuring
from detector_ciclos import DetectorCiclos, configuracion_exacta
from salida_mt import ejecutar
BASE=Path(__file__).resolve().parents[1]


class Ciclos(unittest.TestCase):
    def maquina(self,cadena):
        d,t=cargar_especificacion(BASE/'especificacion_aceptacion.txt')
        d['cadena']=list(cadena)
        return MaquinaTuring(d,t)

    def test_entrada_del_usuario_se_detiene_tras_15_movimientos_del_ciclo(self):
        m=self.maquina('11000111');detector=DetectorCiclos(m)
        for paso in range(1,17):
            m.paso();parar=detector.observar(m)
            self.assertEqual(parar,paso==16)
        self.assertEqual(detector.periodo,2)
        self.assertEqual(detector.inicio,1)
        self.assertEqual(m.pasos-detector.inicio,15)
        self.assertFalse(m.detenida())  # Detiene el observador, no cambia δ.

    def test_ciclo_con_blanco_y_entrada_corta(self):
        for w in ('1','10','111'):
            m=self.maquina(w);d=DetectorCiclos(m)
            for _ in range(16):m.paso();d.observar(m)
            self.assertTrue(d.agotado)

    def test_no_detecta_ciclo_en_aceptacion_o_rechazo(self):
        for w in ('0011','001','01011',''):
            m=self.maquina(w);d=DetectorCiclos(m)
            while not m.detenida():
                m.paso();self.assertFalse(d.observar(m))
            self.assertIsNone(d.periodo)

    def test_no_basta_repetir_estado_sin_repetir_cinta_y_cabezal(self):
        m=self.maquina('0')
        m.delta['q1','0']=('q1','0','R')
        m.delta['q1','_']=('q1','_','R')
        d=DetectorCiclos(m)
        for _ in range(200):m.paso();self.assertFalse(d.observar(m))
        self.assertIsNone(d.periodo)

    def test_ignora_solo_blancos_finales_almacenados(self):
        m=self.maquina('10');antes=configuracion_exacta(m)
        m.cinta.extend(['_']*3)
        self.assertEqual(configuracion_exacta(m),antes)
        m.cabezal=1
        self.assertNotEqual(configuracion_exacta(m),antes)

    def test_exportacion_informa_ciclo_confirmado(self):
        out=io.StringIO()
        resultado,pasos=ejecutar(self.maquina('11000111'),1000,out,movimientos_ciclo=15)
        self.assertEqual((resultado,pasos),('ciclo',16))
        self.assertIn('Ciclo infinito confirmado',out.getvalue())
        self.assertNotIn('Límite alcanzado',out.getvalue())


if __name__=='__main__':unittest.main()
