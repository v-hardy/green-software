# Aqui importamos los modulos estandar de python necesarios
import os
import hashlib
import argparse     # Crear interfaces de línea de comandos

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

def buscar_duplicados(dir1, dir2):
    """Busca archivos duplicados entre dos directorios comparando sus hashes."""
    dic_archivos1 = obtener_archivos_con_hashes(dir1)
    dic_archivos2 = obtener_archivos_con_hashes(dir2)

    hash_lista_de_rutas2 = {}
    for ruta_en_2, valor_hash in dic_archivos2.items():
        # Genero diccionario de CLAVE valor_hash y VALOR lista de rutas de archivos con ese valor_hash (Diccionario invertido de hashes a rutas)
        hash_lista_de_rutas2.setdefault(valor_hash, []).append(ruta_en_2)

    duplicados = []
    for ruta_en_1, valor_hash_de_1 in dic_archivos1.items():
        # Obtengo lista de rutas en 2 segun valor de hash de 1
        rutas2 = hash_lista_de_rutas2.get(valor_hash_de_1, [])
        for ruta2 in rutas2:
            duplicados.append((ruta_en_1, ruta2))

    return duplicados

def mostrar_menu_y_eliminar(duplicados, solo_listar=False, dir1_print=None, dir2_print=None):
    """Muestra los duplicados y permite al usuario decidir cuál eliminar (si no está en modo solo listar)."""
    print("\n 📄 Archivos duplicados encontrados:\n")

    if dir1_print and dir2_print:
        print(f" 📂  [1]{dir1_print}  ⇆  [2]{dir2_print}")

    for i, (f1, f2) in enumerate(duplicados, 1):
        print(f" {i}. {os.path.basename(f1)}  ⟷  {os.path.basename(f2)}", end="")

        if solo_listar:
            print("")
            continue

        bandera=True
        while bandera:
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
                print("   ❌  Opción inválida..." , end="")

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
        print("\n\n📣 NOTA: Ganate un like eliminando tus archivos duplicados.\n")

def main():
    argumentos = procesar_argumentos()
    print(" 🔎 Buscando duplicados...") 
    duplicados = buscar_duplicados(argumentos.directorio1, argumentos.directorio2)

    if not duplicados:
        print(" ✅ No se encontraron archivos duplicados.")
    else:
        mostrar_menu_y_eliminar(duplicados, solo_listar=argumentos.solo_listar, dir1_print=argumentos.directorio1, dir2_print=argumentos.directorio2)
        cierre_final(argumentos.solo_listar)     

if __name__ == "__main__":
    main()