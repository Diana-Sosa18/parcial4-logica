"""Pruebas reales de Pygame sin requerir un monitor (SDL dummy)."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
DISPONIBLE=importlib.util.find_spec('pygame') is not None


@unittest.skipUnless(DISPONIBLE,'Pygame no está instalado en este entorno')
class Interfaz(unittest.TestCase):
    def setUp(self):
        from visualizador import Visualizador
        self.app=Visualizador()
        self.app.dibujar()

    def tearDown(self):
        import pygame
        pygame.quit()

    def test_avanzar_retroceder_reiniciar(self):
        a=self.app;a.avanzar();a.avanzar()
        self.assertEqual(a.maquina.pasos,2)
        a.atras();self.assertEqual(a.maquina.pasos,1)
        a.dibujar();a.reiniciar();self.assertEqual(a.maquina.pasos,0)

    def test_carga_invalida_conserva_maquina(self):
        a=self.app;m=a.maquina
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'mala.txt';p.write_text('seccion_falsa: 1',encoding='utf-8')
            a.cargar(p)
        self.assertIs(a.maquina,m)
        self.assertTrue(a.error)
        a.dibujar()

    def test_ejemplos_y_tamano_minimo(self):
        import pygame
        a=self.app
        for nombre in ('aceptacion','rechazo','ciclo','m2'):
            a.ejemplo(nombre);self.assertFalse(a.error);a.dibujar()
        a.evento(pygame.event.Event(pygame.VIDEORESIZE,w=1120,h=820))
        a.dibujar()

    def test_alerta_ciclo_y_bloqueo_hasta_reiniciar(self):
        a=self.app
        a.entrada.texto='11000111';a.reiniciar(True)
        for _ in range(16):a.avanzar()
        self.assertTrue(a.alerta_ciclo)
        self.assertFalse(a.ejecutando)
        self.assertEqual(a.maquina.pasos,16)
        a.dibujar()
        a.alerta_ciclo=False;a.alternar()
        self.assertFalse(a.ejecutando)
        a.atras()
        self.assertEqual(a.maquina.pasos,15)
        self.assertFalse(a.detector.agotado)
        a.avanzar();self.assertTrue(a.alerta_ciclo)
        a.reiniciar();self.assertFalse(a.alerta_ciclo)
        self.assertFalse(a.detector.agotado)

    def test_limite_y_entrada_invalida(self):
        a=self.app
        a.limite.texto='1';a.avanzar();a.avanzar()
        self.assertEqual(a.maquina.pasos,1)
        a.entrada.texto='2';a.reiniciar(True)
        self.assertTrue(a.error)
        a.limite.texto='hola';a.alternar();self.assertFalse(a.ejecutando)


if __name__=='__main__':unittest.main()
