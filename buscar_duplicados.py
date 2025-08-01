# Aqui importamos los modulos estandar de python necesarios
import os
import hashlib
import argparse     # Crear interfaces de línea de comandos
import time

def procesar_argumentos():
    # Objeto que se encarga de procesar los argumentos
    parser = argparse.ArgumentParser(
        description="Busca archivos duplicados en dos directorios comparando su contenido."
    )
    parser.add_argument("directorio1", help="Primer directorio a analizar")
    parser.add_argument("directorio2", help="Segundo directorio a analizar")
    parser.add_argument("--solo-listar", action="store_true",
                        help="Solo mostrar duplicados sin ofrecer opción de eliminar")
    
    # Leo, valido y convierto los argumentos del terminal en un objeto
    args = parser.parse_args()
    
    # Valido existencia de ambos directorios
    if not os.path.isdir(args.directorio1) or not os.path.isdir(args.directorio2):
        print(" ❌ Ambos caminos deben ser directorios válidos.")
        return
    return args

# Tamaño común de buffer 8KB (2^13)
def calcular_hash(ruta_del_archivo, tamanio_de_bloque=8192):
    """Calcula el hash SHA-256 de UN(1) archivo en bloques."""
    # Inicializo el objeto hash vacio, por medio de la función sha256() 
    objeto = hashlib.sha256()
    try:
        # Abro archivo para lectura binaria
        with open(ruta_del_archivo, 'rb') as f:
            # := Asigna y evalúa al mismo tiempo, valido desde la version 3.8 de py , sino deberia asignar antes y despues del mientras
            while bloque := f.read(tamanio_de_bloque):
                objeto.update(bloque)
        return objeto.hexdigest()
    except Exception as e:
        print(f"[ERROR] No se pudo leer {ruta_del_archivo}: {e}")
        return None

def obtener_archivos_con_hashes(directorio):
    """Obtiene un diccionario de {"ruta_completa": hash_archivo} para todos los archivos en el directorio dado."""
    dic_archivos_hash = {}
    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            hash_archivo = calcular_hash(ruta_completa)
            if hash_archivo:
                dic_archivos_hash[ruta_completa] = hash_archivo

    return dic_archivos_hash

def obtener_duplicados_en_directorio(dic_del_directorio):
    dic_hash_lista_de_rutas = {}
    for ruta_en_directorio, valor_hash in dic_del_directorio.items():
        # Genero diccionario de CLAVE valor_hash y VALOR lista de rutas de archivos con ese valor_hash (Diccionario invertido de hashes a rutas en 1)
        dic_hash_lista_de_rutas.setdefault(valor_hash, []).append(ruta_en_directorio)
    return dic_hash_lista_de_rutas

def obtener_duplicados_entre_directorios(dic_hash_lista_de_rutas1, dic_hash_lista_de_rutas2):
    duplicados_entre = []
    hashes_comunes = set(dic_hash_lista_de_rutas1.keys()) & set(dic_hash_lista_de_rutas2.keys())
    for h in hashes_comunes:
        for r1 in dic_hash_lista_de_rutas1[h]:
            for r2 in dic_hash_lista_de_rutas2[h]:
                duplicados_entre.append((r1, r2)) # si quiero mostrar el valor hash deberia agregar ->, hash <-
    return duplicados_entre

def hay_duplicados(diccionario):
    return any(len(rutas) > 1 for rutas in diccionario.values())

def buscar_duplicados_en_directorio(dir1, dir2):
    dic_archivos1 = obtener_archivos_con_hashes(dir1)
    dic_hash_lista_de_rutas1 = obtener_duplicados_en_directorio(dic_archivos1)

    dic_archivos2 = obtener_archivos_con_hashes(dir2) 
    dic_hash_lista_de_rutas2 = obtener_duplicados_en_directorio(dic_archivos2)
   
    return [dic_hash_lista_de_rutas1, dic_hash_lista_de_rutas2]

def buscar_duplicados_entre_directorios(dic_hash_lista_de_rutas1, dic_hash_lista_de_rutas2):
    lista_duplicado_entre_directorios = []
    lista_duplicado_entre_directorios = obtener_duplicados_entre_directorios(dic_hash_lista_de_rutas1, dic_hash_lista_de_rutas2)

    return lista_duplicado_entre_directorios

def tratar_duplicados_en_directorio(dic_hash_lista_de_rutas, solo_listar=True):
    for hash_valor, lista_rutas in dic_hash_lista_de_rutas.items():
        if len(lista_rutas) > 1:
            time.sleep(1)
            print(f" 🔁 Duplicados encontrados para hash: {hash_valor}")
            for indice, ruta in enumerate(lista_rutas, 1):
                print(f"  [{indice}] {ruta}")
            
            if solo_listar:
                print("  (Solo listado activado, no se eliminará nada)")
                continue  # Solo mostramos, no borramos

            # Elegir cuál conservar
            try:
                opcion = int(input(" Ingrese el número del archivo que desea conservar: "))
                if opcion < 1 or opcion > len(lista_rutas):
                    print(" ❌ Opción inválida. Se conservará el primero por defecto.")
                    opcion = 1
            except ValueError:
                print(" ❌ Entrada no válida. Se conservará el primero por defecto.")
                opcion = 1

            ruta_a_conservar = lista_rutas[(opcion-1)]
            rutas_a_eliminar = [ruta for indice, ruta in enumerate(lista_rutas) if indice != (opcion-1)]

            for ruta in rutas_a_eliminar:
                try:
                    os.remove(ruta)
                    print(f" 🗑️  Eliminado: {ruta}")
                except Exception as e:
                    print(f" ⚠️  Error al eliminar {ruta}: {e}")

            # Actualizamos el diccionario con solo el que se conserva, resultado dicc. sin duplicados
            dic_hash_lista_de_rutas[hash_valor] = [ruta_a_conservar]

    return dic_hash_lista_de_rutas

def tratar_duplicados_entre_directorio(duplicados_entre, solo_listar=True):
    for (f1, f2) in (duplicados_entre):
        time.sleep(1)
        print(f"  {os.path.basename(f1)}  ⟷  {os.path.basename(f2)}", end="")

        if solo_listar:
            print("")
            continue

        while True:
            eleccion = input("   ¿Cuál deseas eliminar? ➟ (1/2/0): ").strip()
            if eleccion == '1':
                try:
                    os.remove(f1)
                    print(f"   🗑️   Eliminado: {f1}")
                    break
                except Exception as e:
                    print(f"[ERROR] No se pudo eliminar {f1}: {e}")
            elif eleccion == '2':
                try:
                    os.remove(f2)
                    print(f"   🗑️   Eliminado: {f2}")
                    break
                except Exception as e:
                    print(f"[ERROR] No se pudo eliminar {f2}: {e}")
            elif eleccion == '0':
                print("   ⏩   Ignorados.")
                break
            else:
                print("   ❌  Opción inválida...", end="")

def mostrar_duplicados_en_directorio(dic_duplicados, solo_listar=False, directorio=None):
    time.sleep(2)
    print(f" 📁 Revisando duplicados en: {directorio}")
    resultado = tratar_duplicados_en_directorio(dic_duplicados, solo_listar=solo_listar)
    return resultado

def mostrar_duplicados_entre_directorios(duplicados_entre, solo_listar=False, dir1=None, dir2=None):
    time.sleep(2)
    print(f" 📂 Comparando entre:  [1] {dir1}  ⇆  [2] {dir2}")
    tratar_duplicados_entre_directorio(duplicados_entre, solo_listar=solo_listar)

def cierre_final(se_muestra_o_no):
    if se_muestra_o_no == False :
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

    print(" 🔎 Buscando duplicados...") 
    duplicados = buscar_duplicados_en_directorio(argumentos.directorio1, argumentos.directorio2)
    # Chequeo duplicados de forma real, o sea mas de 1 (una) ruta por hash
    if not (hay_duplicados(duplicados[0])):
        time.sleep(2)  
        print(f" ✅ No se encontraron archivos duplicados en {argumentos.directorio1}.")
    else:
        duplicados[0] = mostrar_duplicados_en_directorio(duplicados[0], solo_listar=argumentos.solo_listar, directorio=argumentos.directorio1)
    # Chequeo duplicados de forma real, o sea mas de 1 (una) ruta por hash
    if not (hay_duplicados(duplicados[1])):
        time.sleep(2)  
        print(f" ✅ No se encontraron archivos duplicados en {argumentos.directorio2}.")
    else:
        duplicados[1] = mostrar_duplicados_en_directorio(duplicados[1], solo_listar=argumentos.solo_listar, directorio=argumentos.directorio2)

    duplicados = buscar_duplicados_entre_directorios(duplicados[0], duplicados[1])
    # Chequeando duplicados de forma real, o sea mas de 1 (una) ruta por hash
    if not (len(duplicados) > 0):
        time.sleep(2)  
        print(f" ✅ No se encontraron archivos duplicados entre {argumentos.directorio1} y {argumentos.directorio2}.")
    else:        
        # Mostrar duplicados entre directorios
        mostrar_duplicados_entre_directorios(
            duplicados,
            solo_listar=argumentos.solo_listar,
            dir1=argumentos.directorio1,
            dir2=argumentos.directorio2
        )

    cierre_final(argumentos.solo_listar)    

if __name__ == "__main__":
    main()