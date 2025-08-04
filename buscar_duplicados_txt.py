import os
import hashlib
import argparse

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
                return True
    return False

def agrupar_por_hash_simple(archivo_entrada, archivo_salida):
    if os.path.exists(archivo_salida):
        os.remove(archivo_salida)

    with open(archivo_entrada, "r", encoding="utf-8") as f1:
        for linea1 in f1:
            partes1 = linea1.strip().split("|")
            if len(partes1) != 2:
                continue
            ruta1, hash1 = partes1
            if hash_ya_procesado(hash1, archivo_salida):
                continue

            if os.path.exists("temp_rutas.txt"):
                os.remove("temp_rutas.txt")

            with open("temp_rutas.txt", "w", encoding="utf-8") as temp:
                temp.write(ruta1 + "\n")
                with open(archivo_entrada, "r", encoding="utf-8") as f2:
                    for linea2 in f2:
                        partes2 = linea2.strip().split("|")
                        if len(partes2) != 2:
                            continue
                        ruta2, hash2 = partes2
                        if hash1 == hash2 and ruta2 != ruta1:
                            temp.write(ruta2 + "\n")

            count = 0
            with open("temp_rutas.txt", "r", encoding="utf-8") as temp:
                for _ in temp:
                    count += 1

            if count > 1:
                with open("temp_rutas.txt", "r", encoding="utf-8") as temp:
                    linea_out = hash1 + "|"
                    for ruta in temp:
                        linea_out += ruta.strip() + ";"
                    with open(archivo_salida, "a", encoding="utf-8") as out:
                        out.write(linea_out.strip(";") + "\n")

            if os.path.exists("temp_rutas.txt"):
                os.remove("temp_rutas.txt")

def registrar_eliminacion(ruta):
    with open("registro_eliminados.txt", "a", encoding="utf-8") as log:
        log.write("ELIMINADO: " + ruta + "\n")

def eliminar_duplicados_internos_agrupado_simple(archivo_agrupado, solo_listar, archivo_conservados):
    archivo_hashes_duplicados = "hashes_duplicados.txt"

    if os.path.exists(archivo_conservados):
        os.remove(archivo_conservados)
    if os.path.exists(archivo_hashes_duplicados):
        os.remove(archivo_hashes_duplicados)

    if not os.path.exists(archivo_agrupado):
        return

    with open(archivo_agrupado, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split("|")
            if len(partes) != 2:
                continue

            hash_valor, rutas_str = partes

            # Registrar hash duplicado
            with open(archivo_hashes_duplicados, "a", encoding="utf-8") as h:
                h.write(hash_valor + "\n")

            print(f"\n🔁 Hash: {hash_valor}")

            # Procesar rutas sin usar listas ni diccionarios
            ruta_actual = ""
            contador = 1

            # Mostrar las rutas para que el usuario elija
            for c in rutas_str + ";":  # Agregar ';' para terminar última ruta
                if c != ";":
                    ruta_actual += c
                else:
                    print(f"  [{contador}] {ruta_actual}")
                    contador += 1
                    ruta_actual = ""

            if solo_listar:
                print("  (Solo listado activado, no se eliminará nada.)")
                # Guardar la primera ruta conservada
                primera_ruta = ""
                for c in rutas_str + ";":
                    if c != ";":
                        primera_ruta += c
                    else:
                        with open(archivo_conservados, "a", encoding="utf-8") as cfile:
                            cfile.write(primera_ruta + "\n")
                        break
                continue

            eleccion = input("👉 ¿Cuál archivo deseas conservar? (número, por defecto 1): ").strip()
            if not eleccion.isdigit():
                eleccion = "1"

            ruta_actual = ""
            contador = 1
            for c in rutas_str + ";":
                if c != ";":
                    ruta_actual += c
                else:
                    if str(contador) == eleccion:
                        with open(archivo_conservados, "a", encoding="utf-8") as cfile:
                            cfile.write(ruta_actual + "\n")
                    else:
                        try:
                            os.remove(ruta_actual)
                            registrar_eliminacion(ruta_actual)
                            print(f"🗑️  Eliminado: {ruta_actual}")
                        except Exception as e:
                            print(f"⚠️  Error al eliminar {ruta_actual}: {e}")
                    contador += 1
                    ruta_actual = ""

def hash_en_archivo(hash_valor, archivo):
    if not os.path.exists(archivo):
        return False
    with open(archivo, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip() == hash_valor:
                return True
    return False

def ruta_en_archivo(ruta, archivo):
    if not os.path.exists(archivo):
        return False
    with open(archivo, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip() == ruta:
                return True
    return False

def generar_hashes_final(archivo_raw, archivo_final, archivo_conservados):
    if os.path.exists(archivo_final):
        os.remove(archivo_final)

    with open(archivo_final, "w", encoding="utf-8") as _:
        pass  # crear archivo vacío

    if not os.path.exists(archivo_conservados):
        return

    with open(archivo_raw, "r", encoding="utf-8") as f_raw:
        for linea in f_raw:
            partes = linea.strip().split("|")
            if len(partes) != 2:
                continue
            ruta_raw, hash_raw = partes
            with open(archivo_conservados, "r", encoding="utf-8") as f_cons:
                for linea_cons in f_cons:
                    if linea_cons.strip() == ruta_raw:
                        with open(archivo_final, "a", encoding="utf-8") as out:
                            out.write(f"{ruta_raw}|{hash_raw}\n")
                        break

def archivo_ya_usado(ruta, archivo_usados):
    if not os.path.exists(archivo_usados):
        return False
    with open(archivo_usados, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip() == ruta:
                return True
    return False

def registrar_usado(ruta, archivo_usados):
    with open(archivo_usados, "a", encoding="utf-8") as f:
        f.write(ruta + "\n")

def buscar_duplicados_entre(archivo1, archivo2, salida, directorio1, directorio2):
    usados = "usados_entre.txt"
    if os.path.exists(salida):
        os.remove(salida)
    if os.path.exists(usados):
        os.remove(usados)
    print(f"\n📁 Procesando directorios: {directorio1} y {directorio2}...")
    with open(archivo1, "r", encoding="utf-8") as f1:
        for linea1 in f1:
            partes1 = linea1.strip().split("|")
            if len(partes1) != 2:
                continue
            ruta1, hash1 = partes1
            with open(archivo2, "r", encoding="utf-8") as f2:
                for linea2 in f2:
                    partes2 = linea2.strip().split("|")
                    if len(partes2) != 2:
                        continue
                    ruta2, hash2 = partes2
                    if hash1 == hash2 and not archivo_ya_usado(ruta2, usados):
                        with open(salida, "a", encoding="utf-8") as out:
                            out.write(f"{ruta1}|{ruta2}|{hash1}\n")
                        registrar_usado(ruta2, usados)
                        break

def eliminar_duplicados_entre(archivo_duplicados, solo_listar):
    if not os.path.exists(archivo_duplicados):
        return
    with open(archivo_duplicados, "r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split("|")
            if len(partes) != 3:
                continue
            f1, f2, hash_valor = partes
            print(f"\n🔁 Duplicado entre carpetas (hash: {hash_valor})")
            print(f"  [1] {f1}")
            print(f"  [2] {f2}")
            if solo_listar:
                print("  (Solo listado activado, no se eliminará nada.)")
                continue
            eleccion = input("👉 ¿Cuál deseas eliminar? (1/2/0 para ignorar): ").strip()
            if eleccion == "1":
                try:
                    os.remove(f1)
                    registrar_eliminacion(f1)
                    print(f"🗑️  Eliminado: {f1}")
                except Exception as e:
                    print(f"⚠️  Error al eliminar {f1}: {e}")
            elif eleccion == "2":
                try:
                    os.remove(f2)
                    registrar_eliminacion(f2)
                    print(f"🗑️  Eliminado: {f2}")
                except Exception as e:
                    print(f"⚠️  Error al eliminar {f2}: {e}")
            else:
                print("⏩  Ignorado.")

def procesar_directorio(nombre, solo_listar):
    raw = f"hashes_{nombre}_raw.txt"
    agrupado = f"agrupados_internos_{nombre}.txt"
    conservados = f"conservados_{nombre}.txt"
    final = f"hashes_{nombre}.txt"
    archivo_hashes_duplicados = "hashes_duplicados.txt"

    if not any(os.scandir(nombre)):
        print(f"⚠️  El directorio '{nombre}' está vacío. Se omite.")
        return

    print(f"\n📁 Procesando {nombre}...")
    generar_hashes(nombre, raw)
    agrupar_por_hash_simple(raw, agrupado)
    eliminar_duplicados_internos_agrupado_simple(agrupado, solo_listar, conservados)

    # Agregar a conservados los archivos sin duplicados
    if os.path.exists(raw):
        with open(raw, "r", encoding="utf-8") as f_raw:
            for linea in f_raw:
                partes = linea.strip().split("|")
                if len(partes) != 2:
                    continue
                ruta, hash_valor = partes

                # Si hash no está en hashes_duplicados.txt, agregar ruta a conservados (si no está ya)
                if not hash_en_archivo(hash_valor, archivo_hashes_duplicados):
                    if not ruta_en_archivo(ruta, conservados):
                        with open(conservados, "a", encoding="utf-8") as f_out:
                            f_out.write(ruta + "\n")

    generar_hashes_final(raw, final, conservados)

    # Limpieza archivo temporal
    if os.path.exists(archivo_hashes_duplicados):
        os.remove(archivo_hashes_duplicados)

def main():
    parser = argparse.ArgumentParser(description="Detecta y elimina archivos duplicados entre dos carpetas.")
    parser.add_argument("directorio1", help="Primer directorio a analizar")
    parser.add_argument("directorio2", help="Segundo directorio a analizar")
    parser.add_argument("--solo-listar", action="store_true", help="Solo listar duplicados sin eliminar")
    args = parser.parse_args()

    if os.path.exists("registro_eliminados.txt"):
        os.remove("registro_eliminados.txt")

    procesar_directorio(args.directorio1, args.solo_listar)
    procesar_directorio(args.directorio2, args.solo_listar)

    buscar_duplicados_entre(f"hashes_{args.directorio1}.txt", f"hashes_{args.directorio2}.txt", "duplicados_entre.txt", args.directorio1, args.directorio2)
    eliminar_duplicados_entre("duplicados_entre.txt", args.solo_listar)

    if os.path.exists("registro_eliminados.txt"):
        print("\n✅ Proceso completo. Consulta 'registro_eliminados.txt' para ver los eliminados.")
    else:
        print("\n🔍 Proceso de listado completo. No se eliminó ningún archivo y no se generó ningún registro.")

if __name__ == "__main__":
    main()
