
# Buscador de Archivos Duplicados

___

## Problema que Buscamos Resolver

Con el uso diario de computadoras, es muy común que se acumulen archivos duplicados sin que el usuario se dé cuenta: fotos repetidas, versiones viejas de documentos, copias de respaldo que ya no se usan, etc. Todo esto termina ocupando espacio de almacenamiento que podría aprovecharse mejor.

En algunos casos, como en computadoras compartidas o servidores, los archivos duplicados pueden llegar a ocupar varios gigas de forma innecesaria. Además, cuando hay muchos archivos innecesarios, el sistema puede volverse más lento, y se tarda más en hacer tareas como buscar archivos o hacer backups.

___

## Solución Propuesta

Nuestra idea fue desarrollar un script en Python que analice dos carpetas raiz (y todas sus subcarpetas), calcule un hash único para cada archivo (por ejemplo usando SHA-256) y detecte cuáles archivos tienen exactamente el mismo contenido. Una vez que el programa encuentra los duplicados, le va a mostrar al usuario una lista y le va a preguntar si quiere borrarlos para liberar espacio.

De esta forma, se puede limpiar el sistema de forma controlada y sin riesgo de borrar archivos importantes por error. La herramienta también se podría usar periódicamente para mantener ordenado el sistema de archivos y evitar acumulación de contenido redundante.

___

## Relación con el Green Software

Este proyecto está relacionado con el concepto de Green Software porque apunta a usar mejor los recursos digitales. Aunque no parece tan grave, guardar archivos duplicados innecesarios en computadoras o servidores implica:

- Más consumo de energía (especialmente en discos físicos o almacenamiento en la nube)

-  Más uso de recursos de hardware (lo que, a gran escala, también tiene impacto ambiental)

- Menor eficiencia general del sistema

Al ayudar a reducir esta acumulación de datos, nuestro script contribuye indirectamente a un uso más sustentable de la tecnología. Si muchas personas o empresas usaran este tipo de herramientas, se podría ahorrar una buena cantidad de energía y espacio digital, lo cual va en línea con los objetivos del Green Software: hacer que el software sea más responsable con el medio ambiente.

___

## 🧪 Modos de uso:

Listar duplicados sin eliminar nada:
```bash
python3 buscar_duplicados.py ruta-carpeta1 ruta-carpeta2 --solo-listar
```
Buscar y eliminar interactivo:
```bash
python3 buscar_duplicados.py ruta-carpeta1 ruta-carpeta2
```