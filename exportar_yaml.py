"""Exporta el formato del proyecto al lenguaje de turingmachine.io (sin dependencias)."""
from pathlib import Path
from validador_mt import cargar_especificacion


def comillas(s):
    return "'" + s.replace("'", "''") + "'"


def exportar_yaml(entrada, salida):
    d,t=cargar_especificacion(entrada)
    blanco=d['blanco'][0]
    def simbolo(s):return comillas(' ' if s==blanco else s)
    lineas=['# Exportación para turingmachine.io',
            '# En Pygame, la primera celda es el límite izquierdo de la cinta.',
            '# La web permite cinta hacia ambos lados; los ejemplos incluidos no cruzan ese borde.',
            'input: '+comillas(''.join(d['cadena'])),"blank: ' '",
            'start state: '+comillas(d['estado_inicial'][0]),'table:']
    for q in d['estados']:
        lineas.append('  '+comillas(q)+':')
        for estado,a,p,b,m in t:
            if estado==q:
                lineas.append('    '+simbolo(a)+': {write: '+simbolo(b)+', '+m+': '+comillas(p)+'}')
    Path(salida).write_text('\n'.join(lineas)+'\n',encoding='utf-8')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('entrada');p.add_argument('salida')
    a=p.parse_args()
    try:
        exportar_yaml(a.entrada,a.salida)
        print('YAML generado:',a.salida)
    except (ValueError,OSError) as e:
        p.exit(1,f'Error: {e}\n')
