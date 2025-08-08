import os
import hashlib
import argparse
import time

def procesar_argumentos():
    parser = argparse.ArgumentParser(description="Detecta y elimina archivos duplicados entre dos carpetas.")
    parser.add_argument("directorio1", help="Primer directorio a analizar")
    parser.add_argument("directorio2", help="Segundo directorio a analizar")
    parser.add_argument("--solo-listar", action="store_true", help="Solo listar duplicados sin eliminar")
    argumentos_parseados = parser.parse_args()
    return argumentos_parseados

def calcular_hash(ruta_archivo, bloque=8192):
    h = hashlib.sha256()
    try:
        with open(ruta_archivo, 'rb') as f:
            while True:
                b = f.read(bloque)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except:
        return "ERROR"

def generar_hashes(directorio, archivo_salida):
    if os.path.exists(archivo_salida):
        os.remove(archivo_salida)
    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            hash_archivo = calcular_hash(ruta)
            if hash_archivo != "ERROR":
                with open(archivo_salida, "a", encoding="utf-8") as f:
                    f.write(f"{ruta}|{hash_archivo}\n")

def hash_ya_procesado(hash_valor, archivo_salida):
    if not os.path.exists(archivo_salida):
        return False
    with open(archivo_salida, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.startswith(hash_valor + "|"):
                # Si la variable linea empieza con el valor de hash_valor seguido de "|" devuelve verdadero
                return True
    return False

def agrupar_por_hash_en_directorio(archivo_entrada, archivo_salida):
    with open(archivo_entrada, "r", encoding="utf-8") as f1:
        for linea1 in f1:
            partes1 = linea1.strip().split("|")
            if len(partes1) != 2:
                continue
            ruta1, hash1 = partes1
            if hash_ya_procesado(hash1, archivo_salida):
                # Pasa al siguiente si ya se proceso previamente
                continue
            else:
                # tratamiento en caso de varios archivos con mismo hash
                with open("temp_rutas_del_hash.txt", "w", encoding="utf-8") as temp:
                    temp.write(ruta1 + "\n")
                    with open(archivo_entrada, "r", encoding="utf-8") as f2:
                        # Segunda pasada para detectar archivos con hash1
                        for linea2 in f2:
                            partes2 = linea2.strip().split("|")
                            if len(partes2) != 2:
                                continue
                            ruta2, hash2 = partes2
                            if hash1 == hash2 and ruta2 != ruta1:
                                temp.write(ruta2 + "\n")
                cantidad = 0
                with open("temp_rutas_del_hash.txt", "r", encoding="utf-8") as temp:
                    for _ in temp:
                        cantidad += 1
                        # Optimizacion+++
                        if cantidad > 1:
                            break
                if cantidad > 1:
                    with open("temp_rutas_del_hash.txt", "r", encoding="utf-8") as temp:
                        linea_salida = hash1 + "|"
                        for ruta in temp:
                            # concateno todas las rutas y almaceno en linea_salida
                            linea_salida += ruta.strip() + ";"
                        with open(archivo_salida, "a", encoding="utf-8") as salida:
                            salida.write(linea_salida.strip(";") + "\n")    # quito el último ; y agrego un salto de línea.
                if os.path.exists("temp_rutas_del_hash.txt"):
                    os.remove("temp_rutas_del_hash.txt")

def marcar_como_emparejado(ruta, archivo_usados):
    with open(archivo_usados, "a", encoding="utf-8") as f:
        f.write(ruta + "\n")

def esta_emparejado(ruta, archivo_usados):
    if not os.path.exists(archivo_usados):
        return False
    with open(archivo_usados, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip() == ruta:
                return True
    return False

def agrupar_por_hash_entre_directorios(conservados_txt_de_dir1, conservados_txt_de_dir2, salida):
    emparejados = "temp_emparejados_entre_directorios.txt"
    if os.path.exists(emparejados):
        os.remove(emparejados)
    
    with open(conservados_txt_de_dir1, "r", encoding="utf-8") as conservados1:
        for conservado1 in conservados1:
            partes1 = conservado1.strip().split("|")
            if len(partes1) != 2:
                continue
            ruta1, hash1 = partes1
            with open(conservados_txt_de_dir2, "r", encoding="utf-8") as conservados2:
                for conservado2 in conservados2:
                    partes2 = conservado2.strip().split("|")
                    if len(partes2) != 2:
                        continue
                    ruta2, hash2 = partes2
                    if hash1 == hash2 and not esta_emparejado(ruta2, emparejados):
                        with open(salida, "a", encoding="utf-8") as out:
                            out.write(f"{ruta1}|{ruta2}|{hash1}\n")
                        marcar_como_emparejado(ruta2, emparejados)
                        break    # salir del for de dir2 y continuar con la siguiente ruta1
        if os.path.exists(emparejados):
            os.remove(emparejados)

def registrar_eliminacion(ruta):
    with open("registro_eliminados.txt", "a", encoding="utf-8") as log:
        log.write("ELIMINADO: " + ruta + "\n")

def eliminar_duplicados_del_directorio(directorio, solo_listar, hashes_agrupados_txt, archivo_conservados):
    if not os.path.exists(hashes_agrupados_txt):
        time.sleep(2)  
        print(f"✅ No se encontraron archivos duplicados en {directorio}.")
        return
# de aca para abajo
    with open(hashes_agrupados_txt, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()    #.strip() elimina espacios en blanco al inicio y al final, incluyendo saltos de línea (\n), tabulaciones, etc.
            if not linea:
                # si la línea no tiene contenido útil, salto a la siguiente
                continue

            partes = linea.split("|")
            if len(partes) != 2:
                continue
# hasta aca trato la lectura del txt y devuelvo partes
            hash_valor, rutas_str = partes
            rutas = rutas_str.split(";")    # Subdividimos la cadena rutas_str en las subcadenas rutas.

            time.sleep(1) 
            print(f"\n🔁 Hash: {hash_valor}")

            # Muestro las rutas
            for i, ruta in enumerate(rutas, start=1):
                time.sleep(1) 
                print(f"  [{i}] {ruta}")
                if solo_listar:
                    with open(archivo_conservados, "a", encoding="utf-8") as conservado:
                        conservado.write(ruta + "|" + hash_valor + "\n")

            if solo_listar:
                time.sleep(1) 
                print("  (Solo listado activado, no se eliminará nada.)")
                continue

            eleccion = input("👉 ¿Cuál archivo deseas conservar? (número, por defecto 1): ").strip()
            if not eleccion.isdigit() or not (1 <= int(eleccion) <= len(rutas)):
                eleccion = "1"

            eleccion = int(eleccion)

            for i, ruta in enumerate(rutas, start=1):
                if i == eleccion:
                    with open(archivo_conservados, "a", encoding="utf-8") as conservado:
                        conservado.write(ruta + "|" + hash_valor + "\n")
                else:
                    try:
                        os.remove(ruta)
                        registrar_eliminacion(ruta)
                        print(f"🗑️  Eliminado: {ruta}")
                    except Exception as e:
                        print(f"⚠️  Error al eliminar {ruta}: {e}")

def eliminar_duplicados_entre_directorios(directorio1, directorio2, solo_listar, archivo_duplicados):
    if not os.path.exists(archivo_duplicados):
        time.sleep(2)  
        print(f"✅ No se encontraron archivos duplicados entre {directorio1} y {directorio2}.")
        return

    with open(archivo_duplicados, "r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split("|")
            if len(partes) != 3:
                continue
            f1, f2, hash_valor = partes
            print(f"\n🔁 Hash: {hash_valor}")
            print(f"  [1] {f1}")
            print(f"  [2] {f2}")
            if solo_listar:
                print("  (Solo listado activado, no se eliminará nada.)")
                continue

            eleccion = input("👉 ¿Cuál archivo deseas conservar? (número, por defecto 0 para ignorar): ").strip()
            if not eleccion.isdigit() or not (0 <= int(eleccion) <= 2):
                eleccion = "0"

            eleccion = int(eleccion)

            if eleccion == 1:
                try:
                    os.remove(f2)
                    registrar_eliminacion(f2)
                    print(f"🗑️  Eliminado: {f2}")
                except Exception as e:
                    print(f"⚠️  Error al eliminar {f2}: {e}")
            elif eleccion == 2:
                try:
                    os.remove(f1)
                    registrar_eliminacion(f1)
                    print(f"🗑️  Eliminado: {f1}")
                except Exception as e:
                    print(f"⚠️  Error al eliminar {f1}: {e}")
            else:
                print("⏩  Ignorado.")

def hash_en_archivo(hash_valor, archivo_txt):
    if not os.path.exists(archivo_txt):
        return False
    with open(archivo_txt, "r", encoding="utf-8") as f:
        for linea in f:

            linea = linea.strip()    
            if not linea:
                continue

            partes = linea.split("|")
            if len(partes) != 2:
                continue

            linea_hash_valor, rutas_str = partes

            if linea_hash_valor == hash_valor:
                return True
    return False

def ruta_en_archivo(ruta, archivo_txt):
    if not os.path.exists(archivo_txt):
        return False
    with open(archivo_txt, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()    
            if not linea:
                continue

            partes = linea.split("|")
            if len(partes) != 2:
                continue

            ruta_en_linea, linea_hash_valor = partes
            if ruta_en_linea == ruta:
                return True
    return False

def limpiar(directorio1, directorio2, solo_listar):
    if not solo_listar:
        for archivo_txt in (f"duplicados_entre_directorios.txt",
                        f"hashes_de_{directorio1}.txt",
                        f"hashes_de_{directorio1}_conservados.txt",
                        f"hashes_de_{directorio1}_duplicados.txt",
                        f"hashes_de_{directorio2}.txt",
                        f"hashes_de_{directorio2}_conservados.txt",
                        f"hashes_de_{directorio2}_duplicados.txt"):
            if os.path.exists(archivo_txt):
                os.remove(archivo_txt)

def procesar_directorio(directorio, solo_listar):
    time.sleep(1) 
    print(f"\n📁 Iniciando procesamiento de {directorio}...")
    if not any(os.scandir(directorio)):
        time.sleep(1) 
        print(f"⚠️  El directorio '{directorio}' está vacío. Se omite busqueda de duplicados.")
        return
    
    raw = f"hashes_de_{directorio}.txt"
    agrupados = f"hashes_de_{directorio}_duplicados.txt"
    conservados = f"hashes_de_{directorio}_conservados.txt"
    # Eliminar archivos previos si existen
    for archivo in (raw, agrupados, conservados):
        if os.path.exists(archivo):
            os.remove(archivo)
      
    generar_hashes(directorio, raw)

    agrupar_por_hash_en_directorio(raw, agrupados)

    eliminar_duplicados_del_directorio(directorio, solo_listar, agrupados, conservados)

    # Agregar a conservados los archivos sin duplicados
    if os.path.exists(raw):
        with open(raw, "r", encoding="utf-8") as f_raw:
            for linea in f_raw:
                partes = linea.strip().split("|")
                if len(partes) != 2:
                    continue
                ruta, hash_valor = partes

                # Si hash_valor no está en agrupados y ruta en no esta en conservados, agrego ruta+hash a conservados
                if not hash_en_archivo(hash_valor, agrupados):
                    if not ruta_en_archivo(ruta, conservados):  
                        with open(conservados, "a", encoding="utf-8") as f_conservados:
                            f_conservados.write(ruta + "|" + hash_valor + "\n")

def procesar_directorios(directorio1, directorio2, solo_listar):
    time.sleep(1) 
    print(f"\n📁 Iniciando procesamiento de directorios: {directorio1} y {directorio2}...")
    for directorio in (directorio1, directorio2):
        if not any(os.scandir(directorio)):
            time.sleep(1) 
            print(f"⚠️  El directorio '{directorio}' está vacío. Se omite proceso de comparacion entre directorios {directorio1} y {directorio2}.")
            return
    
    conservados1 = f"hashes_de_{directorio1}_conservados.txt"
    conservados2 = f"hashes_de_{directorio2}_conservados.txt"
    duplicados_en_1y2 = f"duplicados_entre_directorios.txt"
    if os.path.exists(duplicados_en_1y2):
        os.remove(duplicados_en_1y2)

    agrupar_por_hash_entre_directorios(conservados1, conservados2, duplicados_en_1y2)
        
    eliminar_duplicados_entre_directorios(directorio1, directorio2, solo_listar, duplicados_en_1y2)    
    
    limpiar(directorio1, directorio2, solo_listar)
    #A MEJORAR: deberia actualizar los conservados de cada directorio quitando los eliminados

def cierre_final(se_muestra_o_no):
    if se_muestra_o_no == False :
        time.sleep(3)
        print("\nThank you for supporting")
        print("Sustainable software practices")
        print("""─────────────────────░███░
────────────────────░█░░░█░
───────────────────░█░░░░░█░
──────────────────░█░░░░░█░
───────────░░░───░█░░░░░░█░
──────────░███░──░█░░░░░█░
────────░██░░░██░█░░░░░█░
───────░█░░█░░░░██░░░░░█░
─────░██░░█░░░░░░█░░░░█░
────░█░░░█░░░░░░░██░░░█░
───░█░░░░█░░░░░░░░█░░░█░
───░█░░░░░█░░░░░░░░█░░░█░
───░█░░█░░░█░░░░░░░░█░░█░
──░█░░░█░░░░██░░░░░░█░░█░
──░█░░░░█░░░░░██░░░█░░░█░
──░█░█░░░█░░░░░░███░░░░█░
─░█░░░█░░░██░░░░░█░░░░░█░
─░█░░░░█░░░░█████░░░░░█░
─░█░░░░░█░░░░░░░█░░░░░█░
─░█░█░░░░██░░░░█░░░░░█░
──░█░█░░░░░████░░░░██░
──░█░░█░░░░░░░█░░██░█░
───░█░░██░░░██░░█░░░█░
────░██░░███░░██░█░░█░
─────░██░░░███░░░█░░░█░
───────░███░░░░░░█░░░█░
───────░█░░░░░░░░█░░░█░
───────░█░░░░░░░░░░░░█░
───────░█░░░░░░░░░░░░░█░
───────░█░░░░░░░░░░░░░█░
─████──░█░████░░░░░░░░█░
─█──█──████──████░░░░░█░
─█──█──█──█──█──████████
─█──█──████──█──█──────█
─█──█──█──█────██──██──█
─█──████──█──█──█──────█
─█─────█──█──█──█──█████
─███████──████──█──────█
───────████──██████████
""")
    else:
        print("\n📣 NOTA: Ganate un like eliminando tus archivos duplicados.\n")


def main():
    argumentos = procesar_argumentos()
    if not argumentos:
        return

    if os.path.exists("registro_eliminados.txt"):
        os.remove("registro_eliminados.txt")

    procesar_directorio(argumentos.directorio1, argumentos.solo_listar)

    procesar_directorio(argumentos.directorio2, argumentos.solo_listar)

    procesar_directorios(argumentos.directorio1, argumentos.directorio2, argumentos.solo_listar)
 
    #podria agregar para borrar .txt's por defecto en cuenta regresiva y con un ENTER interrumpir

    if os.path.exists("registro_eliminados.txt"):
        time.sleep(1)
        print("\n✅ Proceso completo. Consulta 'registro_eliminados.txt' para ver los eliminados.")
    else:
        time.sleep(1)
        print("\n🔍 Proceso de listado completo. No se eliminó ningún archivo.")

    cierre_final(argumentos.solo_listar)

if __name__ == "__main__":
    main()
