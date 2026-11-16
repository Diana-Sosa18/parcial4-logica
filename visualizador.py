"""Interfaz Pygame: cinta, grafo, tabla y controles de ejecución."""
import math
import os
from pathlib import Path
from datetime import datetime
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
from validador_mt import cargar_especificacion
from simulador_mt import MaquinaTuring
from salida_mt import generar_salida
from detector_ciclos import DetectorCiclos

BASE = Path(__file__).resolve().parent
BG = '#0b1120'
PANEL = '#131e32'
BORDER = '#293750'
TEXT = '#e7eefc'
MUTED = '#97a9c5'
MINT = '#54dec3'
RED = '#ff8395'
GOLD = '#f4c676'


class Campo:
    def __init__(self, texto=''):
        self.texto = texto
        self.activo = False
        self.rect = pygame.Rect(0, 0, 1, 1)
        self.reemplazar = False

    def evento(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(e.pos)
        if self.activo and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_BACKSPACE:
                self.texto = '' if self.reemplazar else self.texto[:-1]
                self.reemplazar = False
            elif e.key == pygame.K_a and e.mod & pygame.KMOD_CTRL:
                self.reemplazar = True
            elif e.key not in (pygame.K_RETURN, pygame.K_TAB, pygame.K_ESCAPE):
                if e.unicode and e.unicode.isprintable():
                    if self.reemplazar:
                        self.texto = ''
                    self.texto += e.unicode
                    self.reemplazar = False


class Visualizador:
    def __init__(self, archivo=None):
        pygame.init()
        self.pantalla = pygame.display.set_mode((1320, 920), pygame.RESIZABLE)
        pygame.display.set_caption('Turing Studio | Proyecto Lógica')
        self.reloj = pygame.time.Clock()
        self.fuentes = {n: pygame.font.SysFont('DejaVu Sans,Segoe UI,Arial', n) for n in (12, 14, 16, 18, 20, 24, 30)}
        self.ruta = Campo(str(archivo or BASE / 'especificacion_aceptacion.txt'))
        self.entrada = Campo()
        self.limite = Campo('10000')
        self.campos = [self.ruta, self.entrada, self.limite]
        self.botones = []
        self.velocidades = [1, 2, 5, 10, 20, 50, 100]
        self.velocidad = 3
        self.ejecutando = False
        self.tiempo = 0
        self.scroll_tabla = 0
        self.seguir = True
        self.vista = 0
        self.error = ''
        self.aviso = ''
        self.maquina = None
        self.ultima = None
        self.detector = None
        self.alerta_ciclo = False
        self.cargar(self.ruta.texto)

    def texto(self, s, pos, size=16, color=TEXT, ancho=None, centro=False):
        s = str(s)
        fuente = self.fuentes[size]
        if ancho:
            while s and fuente.size(s)[0] > ancho:
                s = s[:-2] + '…' if not s.endswith('…') else s[:-2] + '…'
        imagen = fuente.render(s, True, color)
        rect = imagen.get_rect(center=pos) if centro else imagen.get_rect(topleft=pos)
        self.pantalla.blit(imagen, rect)
        return rect

    def panel(self, rect):
        pygame.draw.rect(self.pantalla, PANEL, rect, border_radius=14)
        pygame.draw.rect(self.pantalla, BORDER, rect, 1, border_radius=14)

    def boton(self, texto, rect, accion, activo=False, habilitado=True):
        rect = pygame.Rect(rect)
        hover = rect.collidepoint(pygame.mouse.get_pos())
        fondo = '#1d786e' if activo else ('#283d59' if hover and habilitado else '#1c2b43')
        pygame.draw.rect(self.pantalla, fondo, rect, border_radius=8)
        self.texto(texto, rect.center, 14, TEXT if habilitado else '#526580', centro=True)
        self.botones.append((rect, accion, habilitado))

    def campo(self, campo, rect):
        campo.rect = pygame.Rect(rect)
        pygame.draw.rect(self.pantalla, '#0d1627', campo.rect, border_radius=8)
        pygame.draw.rect(self.pantalla, MINT if campo.activo else BORDER, campo.rect, 1, border_radius=8)
        # Mostrar el final permite editar rutas largas.
        texto = campo.texto + ('|' if campo.activo and pygame.time.get_ticks() % 1000 < 500 else '')
        while self.fuentes[16].size(texto)[0] > campo.rect.w - 20 and texto:
            texto = texto[1:]
        self.texto(texto, (campo.rect.x + 10, campo.rect.y + 9), ancho=campo.rect.w - 20)
        if campo.reemplazar and campo.activo:
            pygame.draw.line(self.pantalla, MINT, (campo.rect.x+8,campo.rect.bottom-4),(campo.rect.right-8,campo.rect.bottom-4),2)

    def cargar(self, ruta):
        self.ejecutando = False
        try:
            d, t = cargar_especificacion(Path(ruta).expanduser())
            maquina = MaquinaTuring(d, t)
            self.datos, self.transiciones = d, t
            self.maquina = maquina
            self.detector = DetectorCiclos(maquina)
            self.alerta_ciclo = False
            self.entrada.texto = ''.join(d['cadena'])
            self.ruta.texto = str(Path(ruta).expanduser().resolve())
            self.scroll_tabla = 0
            self.ultima = None
            self.error = ''
            self.aviso = 'Especificación válida. Lista para simular.'
            self.seguir = True
        except (ValueError, OSError) as e:
            # Mantener la máquina válida anterior cuando la nueva carga falla.
            self.error = str(e)

    def ejemplo(self, nombre):
        self.cargar(BASE / f'especificacion_{nombre}.txt')

    def reiniciar(self, aplicar=False):
        self.ejecutando = False
        if not self.maquina:
            return
        try:
            d = dict(self.datos)
            if aplicar:
                d['cadena'] = list(self.entrada.texto)
            m = MaquinaTuring(d, self.transiciones)
            self.datos = d
            self.maquina = m
            self.detector = DetectorCiclos(m)
            self.alerta_ciclo = False
            self.entrada.texto = ''.join(d['cadena'])
            self.ultima = None
            self.error = ''
            self.aviso = 'Máquina reiniciada.'
            self.seguir = True
        except ValueError as e:
            self.error = str(e)

    def maximo(self):
        try:
            n = int(self.limite.texto)
            if not 1 <= n <= 100000:
                raise ValueError()
            return n
        except ValueError:
            raise ValueError('El límite debe ser un entero entre 1 y 100000.')

    def avanzar(self):
        if self.detector and self.detector.agotado:
            self.ejecutando = False
            self.alerta_ciclo = True
            return
        if not self.maquina or self.maquina.detenida():
            self.ejecutando = False
            return
        try:
            if self.maquina.pasos >= self.maximo():
                self.ejecutando = False
                self.aviso = 'Límite alcanzado: no demuestra ciclo infinito. Aumenta el límite para continuar.'
                return
            self.ultima = self.maquina.siguiente_transicion()
            self.maquina.paso()
            if self.detector.observar(self.maquina):
                self.ejecutando = False
                self.alerta_ciclo = True
                self.aviso = 'Ciclo infinito confirmado. Simulación detenida tras al menos 15 movimientos dentro del ciclo.'
            self.error = ''
            self.seguir = True
            if self.maquina.detenida():
                self.ejecutando = False
                self.aviso = 'Ejecución terminada.'
        except ValueError as e:
            self.ejecutando = False
            self.error = str(e)

    def atras(self):
        self.ejecutando = False
        if not self.maquina or self.maquina.pasos == 0:
            return
        objetivo = self.maquina.pasos - 1
        m = MaquinaTuring(self.datos, self.transiciones)
        self.ultima = None
        detector = DetectorCiclos(m)
        for _ in range(objetivo):
            self.ultima = m.siguiente_transicion()
            m.paso()
            detector.observar(m)
        self.detector = detector
        self.alerta_ciclo = False
        self.maquina = m
        self.seguir = True
        self.error = ''
        self.aviso = 'Paso anterior reconstruido desde la entrada original.'

    def alternar(self):
        if self.detector and self.detector.agotado:
            self.ejecutando = False
            self.alerta_ciclo = True
            return
        if self.maquina and not self.maquina.detenida():
            try:
                if self.maquina.pasos >= self.maximo():
                    self.aviso = 'Aumenta el límite o reinicia para continuar.'
                    return
                self.ejecutando = not self.ejecutando
                self.tiempo = 0
            except ValueError as e:
                self.error = str(e)

    def guardar(self):
        self.ejecutando = False
        if not self.maquina:
            return
        try:
            carpeta = BASE / 'exportaciones'
            carpeta.mkdir(exist_ok=True)
            ruta = carpeta / f'configuraciones_{datetime.now():%Y%m%d_%H%M%S_%f}.txt'
            generar_salida(MaquinaTuring(self.datos, self.transiciones), ruta, self.maquina.pasos, movimientos_ciclo=15)
            self.aviso = f'Traza guardada: exportaciones/{ruta.name}'
            self.error = ''
        except (ValueError, OSError) as e:
            self.error = str(e)

    def flecha(self, a, b, color=BORDER, ancho=2):
        pygame.draw.line(self.pantalla, color, a, b, ancho)
        ang = math.atan2(b[1]-a[1], b[0]-a[0])
        puntos = [b, (b[0]-10*math.cos(ang-.45), b[1]-10*math.sin(ang-.45)),
                  (b[0]-10*math.cos(ang+.45), b[1]-10*math.sin(ang+.45))]
        pygame.draw.polygon(self.pantalla, color, puntos)

    def grafo(self, rect):
        self.panel(rect)
        self.texto('DIAGRAMA DE ESTADOS', (rect.x+20, rect.y+16), 14, MUTED)
        self.texto('Se resalta la próxima transición · etiquetas en la tabla', (rect.x+20, rect.y+40), 12, MUTED)
        if not self.maquina:
            return
        estados = self.datos['estados']; n = len(estados)
        if n > 16:
            self.texto(f'{n} estados: usa la tabla de transiciones.', rect.center, 16, MUTED, centro=True)
            return
        cx, cy = rect.centerx, rect.y+rect.h*.57
        rx, ry = rect.w*.35, rect.h*.30
        posiciones = {q:(cx+rx*math.cos(-math.pi/2+2*math.pi*i/n), cy+ry*math.sin(-math.pi/2+2*math.pi*i/n)) for i,q in enumerate(estados)}
        radio = 28 if n <= 10 else 22
        prox = self.maquina.siguiente_transicion()
        pares = set((q,p) for q,a,p,b,m in self.transiciones)
        for q,p in sorted(pares):
            a,b = posiciones[q], posiciones[p]
            activo = bool(prox and (q,p)==(prox[0],prox[2]))
            color = MINT if activo else '#354762'
            if q==p:
                r = pygame.Rect(a[0]-17, a[1]-radio-27, 34, 35)
                pygame.draw.ellipse(self.pantalla, color, r, 2)
                self.flecha((a[0]+17,a[1]-radio-10),(a[0]+12,a[1]-radio+2),color)
            else:
                ang = math.atan2(b[1]-a[1],b[0]-a[0])
                # Desplazamiento lateral separa las direcciones opuestas.
                off=5 if (p,q) in pares else 0
                dx,dy=-math.sin(ang)*off,math.cos(ang)*off
                ini=(a[0]+radio*math.cos(ang)+dx,a[1]+radio*math.sin(ang)+dy)
                fin=(b[0]-radio*math.cos(ang)+dx,b[1]-radio*math.sin(ang)+dy)
                self.flecha(ini,fin,color,3 if activo else 1)
        for q,pos in posiciones.items():
            actual=q==self.maquina.estado
            color=MINT if actual else (RED if q==self.maquina.rechazo else '#7290b7')
            pygame.draw.circle(self.pantalla, '#1d4e50' if actual else '#17263e', pos, radio)
            pygame.draw.circle(self.pantalla,color,pos,radio,3 if actual else 1)
            if q==self.maquina.aceptacion:
                pygame.draw.circle(self.pantalla,color,pos,radio-5,1)
            self.texto(q,pos,12,color,ancho=radio*2-6,centro=True)
        self.texto(f'Actual: {self.maquina.estado}',(rect.x+20,rect.bottom-27),14,MINT,ancho=rect.w-40)

    def tabla(self, rect):
        self.panel(rect)
        self.rect_tabla=rect
        self.texto('FUNCIÓN DE TRANSICIÓN', (rect.x+18,rect.y+16),14,MUTED)
        self.texto('Estado    Lee    Escribe    Mueve    Destino', (rect.x+18,rect.y+44),12,MUTED)
        if not self.maquina:
            return
        filas=max(1,(rect.h-100)//25)
        prox=self.maquina.siguiente_transicion()
        indice=next((i for i,t in enumerate(self.transiciones) if prox and tuple(t)==prox),None)
        if self.seguir and indice is not None:
            self.scroll_tabla=max(0,min(indice-filas//2,len(self.transiciones)-filas))
        self.scroll_tabla=max(0,min(self.scroll_tabla,max(0,len(self.transiciones)-filas)))
        for i,t in enumerate(self.transiciones[self.scroll_tabla:self.scroll_tabla+filas]):
            q,a,p,b,m=t
            y=rect.y+74+i*25
            activa=bool(prox and tuple(t)==prox)
            if activa:
                pygame.draw.rect(self.pantalla,'#20504f',(rect.x+10,y-2,rect.w-20,24),border_radius=5)
            vals=[q,self.simbolo(a),self.simbolo(b),m,p]
            fracs=[.04,.29,.43,.61,.76]
            for val,f in zip(vals,fracs):
                self.texto(val,(rect.x+rect.w*f,y),14,MINT if activa else TEXT,ancho=rect.w*(.23 if f in (.04,.76) else .14))
        self.texto(f'{self.scroll_tabla+1}–{min(self.scroll_tabla+filas,len(self.transiciones))} de {len(self.transiciones)} · rueda para desplazar', (rect.x+18,rect.bottom-24),12,MUTED)

    def simbolo(self,a):
        return '⊔' if self.maquina and a==self.maquina.blanco else a

    def cinta(self, rect):
        self.panel(rect)
        self.texto('CINTA  ·  el cabezal permanece centrado', (rect.x+18,rect.y+10),12,MUTED)
        if not self.maquina:
            return
        m=self.maquina
        tam=48; cantidad=max(3,(rect.w-40)//tam)
        if cantidad%2==0:cantidad-=1
        inicio=m.cabezal-cantidad//2
        x0=rect.centerx-cantidad*tam//2
        for j in range(cantidad):
            idx=inicio+j; x=x0+j*tam; y=rect.y+35
            if idx<0:
                pygame.draw.rect(self.pantalla,'#101a2a',(x+2,y,tam-4,45),border_radius=5)
                continue
            actual=idx==m.cabezal
            pygame.draw.rect(self.pantalla,'#205951' if actual else '#1c2c45',(x+2,y,tam-4,45),border_radius=5)
            if actual:pygame.draw.rect(self.pantalla,MINT,(x+2,y,tam-4,45),2,border_radius=5)
            a=m.cinta[idx] if idx<len(m.cinta) else m.blanco
            self.texto(self.simbolo(a),(x+tam//2,y+22),24,MINT if actual else TEXT,centro=True)
            self.texto(idx,(x+tam//2,y+57),12,MUTED,centro=True)

    def dibujar(self):
        self.botones=[]
        w,h=self.pantalla.get_size()
        self.pantalla.fill(BG)
        self.texto('TURING / STUDIO', (24,16),30)
        self.texto('Proyecto de Lógica · simulación de una cinta', (340,29),14,MUTED)
        nombres=[('Aceptación','aceptacion'),('Rechazo','rechazo'),('Ciclo','ciclo'),('Máquina M2','m2')]
        for i,(label,nombre) in enumerate(nombres):
            self.boton(label,(24+i*142,63,132,32),lambda n=nombre:self.ejemplo(n))
        self.texto('ARCHIVO .TXT  ·  también puedes arrastrarlo a la ventana', (24,105),12,MUTED)
        self.campo(self.ruta,(24,125,w-174,38))
        self.boton('Cargar',(w-136,125,112,38),lambda:self.cargar(self.ruta.texto))
        self.texto('CADENA DE ENTRADA  ·  vacía = ε', (24,174),12,MUTED)
        self.campo(self.entrada,(24,194,310,36))
        self.boton('Aplicar entrada',(346,194,134,36),lambda:self.reiniciar(True),habilitado=bool(self.maquina))
        if self.maquina:
            m=self.maquina
            label={'aceptacion':'ACEPTADA','rechazo':'RECHAZADA','en_curso':'EJECUTANDO' if self.ejecutando else 'EN PAUSA'}[m.resultado]
            if self.detector and self.detector.agotado:
                label = 'CICLO INFINITO · DETENIDA'
            color=MINT if m.resultado=='aceptacion' else RED if m.resultado=='rechazo' else GOLD
            self.texto(label,(510,192),18,color)
            self.texto(f'Paso {m.pasos}  ·  Estado {m.estado}  ·  Cabezal {m.cabezal}',(510,215),14,MUTED,ancho=w-540)
        alto=h-495
        corte=int((w-62)*.56)
        self.grafo(pygame.Rect(24,247,corte,alto))
        self.tabla(pygame.Rect(38+corte,247,w-corte-62,alto))
        self.cinta(pygame.Rect(24,h-232,w-48,119))
        x=24
        for label,ancho,accion in [('Atrás',75,self.atras),('Paso →',88,self.avanzar),('Pausar' if self.ejecutando else 'Ejecutar',108,self.alternar),('Reiniciar',100,self.reiniciar),('Guardar traza',128,self.guardar)]:
            self.boton(label,(x,h-99,ancho,36),accion,activo=label=='Pausar',habilitado=bool(self.maquina))
            x+=ancho+8
        self.boton('−',(x+8,h-99,32,36),lambda:self.cambiar_velocidad(-1))
        self.texto(f'{self.velocidades[self.velocidad]} pasos/s',(x+50,h-90),14,MUTED)
        self.boton('+',(x+153,h-99,32,36),lambda:self.cambiar_velocidad(1))
        self.texto('LÍMITE',(w-185,h-116),12,MUTED)
        self.campo(self.limite,(w-185,h-99,160,36))
        mensaje=self.error.replace('\n','  ·  ') if self.error else self.aviso
        self.texto(mensaje,(24,h-53),14,RED if self.error else MUTED,ancho=w-48)
        self.texto('Espacio: ejecutar/pausar  ·  →: paso  ·  ←: atrás  ·  R: reiniciar  ·  Ctrl+S: guardar  ·  Ctrl+A: seleccionar campo', (24,h-26),12,MUTED,ancho=w-48)
        if self.alerta_ciclo:
            self.dibujar_alerta()
        pygame.display.flip()

    def dibujar_alerta(self):
        w,h=self.pantalla.get_size()
        velo=pygame.Surface((w,h),pygame.SRCALPHA)
        velo.fill((3,8,18,205))
        self.pantalla.blit(velo,(0,0))
        caja=pygame.Rect(w//2-350,h//2-150,700,300)
        self.panel(caja)
        self.texto('CICLO INFINITO DETECTADO',(caja.x+28,caja.y+28),24,GOLD)
        self.texto('Se repitieron el estado, la posición del cabezal y toda la cinta.',(caja.x+28,caja.y+80),16)
        periodo=self.detector.periodo if self.detector else '?'
        self.texto(f'Período confirmado: {periodo} movimientos.',(caja.x+28,caja.y+111),16,MINT)
        self.texto('La simulación se detuvo tras al menos 15 movimientos dentro del ciclo.',(caja.x+28,caja.y+144),16)
        self.texto('Puedes reiniciar, cambiar la entrada o retroceder.',(caja.x+28,caja.y+175),14,MUTED)
        self.cerrar_alerta=pygame.Rect(caja.right-150,caja.bottom-62,120,38)
        self.boton('Entendido',self.cerrar_alerta,lambda:setattr(self,'alerta_ciclo',False))

    def cambiar_velocidad(self,delta):
        self.velocidad=max(0,min(len(self.velocidades)-1,self.velocidad+delta))

    def evento(self,e):
        if e.type==pygame.QUIT:return False
        if e.type==pygame.VIDEORESIZE:
            self.pantalla=pygame.display.set_mode((max(1120,e.w),max(820,e.h)),pygame.RESIZABLE)
        if self.alerta_ciclo:
            if e.type==pygame.KEYDOWN and e.key in (pygame.K_RETURN,pygame.K_ESCAPE):
                self.alerta_ciclo=False
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                if hasattr(self,'cerrar_alerta') and self.cerrar_alerta.collidepoint(e.pos):
                    self.alerta_ciclo=False
            return True
        if e.type==pygame.DROPFILE:
            self.cargar(e.file)
        for c in self.campos:c.evento(e)
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            for rect,accion,habilitado in self.botones:
                if habilitado and rect.collidepoint(e.pos):
                    accion();break
        if e.type==pygame.MOUSEWHEEL and self.rect_tabla.collidepoint(pygame.mouse.get_pos()):
            self.scroll_tabla-=e.y*3
            self.seguir=False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                for c in self.campos:c.activo=False
                self.ejecutando=False
            elif e.key==pygame.K_RETURN:
                if self.ruta.activo:self.cargar(self.ruta.texto)
                elif self.entrada.activo:self.reiniciar(True)
                elif self.limite.activo:
                    try:self.maximo();self.error=''
                    except ValueError as err:self.error=str(err)
            elif not any(c.activo for c in self.campos):
                if e.key==pygame.K_SPACE:self.alternar()
                elif e.key==pygame.K_RIGHT:self.ejecutando=False;self.avanzar()
                elif e.key==pygame.K_LEFT:self.atras()
                elif e.key==pygame.K_r:self.reiniciar()
                elif e.key==pygame.K_s and e.mod & pygame.KMOD_CTRL:self.guardar()
        return True

    def ejecutar(self):
        activo=True
        while activo:
            dt=self.reloj.tick(60)/1000
            for e in pygame.event.get():
                if not self.evento(e):activo=False
            if self.ejecutando:
                self.tiempo+=dt
                intervalo=1/self.velocidades[self.velocidad]
                # Presupuesto acotado por cuadro: la ventana sigue respondiendo.
                for _ in range(min(20,int(self.tiempo/intervalo))):
                    if not self.ejecutando:break
                    self.avanzar();self.tiempo=max(0,self.tiempo-intervalo)
            self.dibujar()
        pygame.quit()
