import os
import hashlib
import argparse

def calcular_hash(filepath, chunk_size=8192):
    """Calcula el hash SHA-256 de un archivo en bloques."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"[ERROR] No se pudo leer {filepath}: {e}")
        return None

def obtener_archivos_con_hashes(directorio):
    """Obtiene un diccionario de {ruta: hash} para todos los archivos en el directorio dado."""
    archivos_hash = {}
    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            hash_archivo = calcular_hash(ruta)
            if hash_archivo:
                archivos_hash[ruta] = hash_archivo
    return archivos_hash

def buscar_duplicados(dir1, dir2):
    """Busca archivos duplicados entre dos directorios comparando sus hashes."""
    archivos1 = obtener_archivos_con_hashes(dir1)
    archivos2 = obtener_archivos_con_hashes(dir2)

    hash_to_rutas2 = {}
    for ruta2, hash_val in archivos2.items():
        hash_to_rutas2.setdefault(hash_val, []).append(ruta2)

    duplicados = []
    for ruta1, hash1 in archivos1.items():
        rutas2 = hash_to_rutas2.get(hash1, [])
        for ruta2 in rutas2:
            duplicados.append((ruta1, ruta2))
    
    nombre_carpeta = (dir1, dir2)

    return duplicados, *nombre_carpeta

def mostrar_menu_y_eliminar(duplicados, solo_listar=False, dir1=None, dir2=None):
    """Muestra los duplicados y permite al usuario decidir cuál eliminar (si no está en modo solo lectura)."""
    print("\n🔍 Archivos duplicados encontrados:\n")

    if dir1 and dir2:
        print(f"  [1]{dir1}  ⇆  [2]{dir2}")

    for i, (f1, f2) in enumerate(duplicados, 1):
        print(f"{i}. {os.path.basename(f1)}  ⟷  {os.path.basename(f2)}", end="")

        if solo_listar:
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

def main():
    parser = argparse.ArgumentParser(
        description="Busca archivos duplicados en dos directorios comparando su contenido."
    )
    parser.add_argument("directorio1", help="Primer directorio a analizar")
    parser.add_argument("directorio2", help="Segundo directorio a analizar")
    parser.add_argument("--solo-listar", action="store_true",
                        help="Solo mostrar duplicados sin ofrecer opción de eliminar")

    args = parser.parse_args()
    print(f"{args.directorio1}")
    nombre_carpeta = (args.directorio1, args.directorio2)
    if not os.path.isdir(args.directorio1) or not os.path.isdir(args.directorio2):
        print("❌ Ambos caminos deben ser directorios válidos.")
        return

    print("🔎 Buscando duplicados...")
    
    duplicados, dir1, dir2 = buscar_duplicados(args.directorio1, args.directorio2)

    if not duplicados:
        print("✅ No se encontraron archivos duplicados.")
    else:
        mostrar_menu_y_eliminar(duplicados, solo_listar=args.solo_listar,
            dir1=dir1,
            dir2=dir2)
        
        print("""────────────────────░███░
───────────────────░█░░░█░
──────────────────░█░░░░░█░
─────────────────░█░░░░░█░
──────────░░░───░█░░░░░░█░
─────────░███░──░█░░░░░█░
───────░██░░░██░█░░░░░█░
──────░█░░█░░░░██░░░░░█░
────░██░░█░░░░░░█░░░░█░
───░█░░░█░░░░░░░██░░░█░
──░█░░░░█░░░░░░░░█░░░█░
──░█░░░░░█░░░░░░░░█░░░█░
──░█░░█░░░█░░░░░░░░█░░█░
─░█░░░█░░░░██░░░░░░█░░█░
─░█░░░░█░░░░░██░░░█░░░█░
─░█░█░░░█░░░░░░███░░░░█░
░█░░░█░░░██░░░░░█░░░░░█░
░█░░░░█░░░░█████░░░░░█░
░█░░░░░█░░░░░░░█░░░░░█░
░█░█░░░░██░░░░█░░░░░█░
─░█░█░░░░░████░░░░██░
─░█░░█░░░░░░░█░░██░█░
──░█░░██░░░██░░█░░░█░
───░██░░███░░██░█░░█░
────░██░░░███░░░█░░░█░
──────░███░░░░░░█░░░█░
──────░█░░░░░░░░█░░░█░
──────░█░░░░░░░░░░░░█░
──────░█░░░░░░░░░░░░░█░
──────░█░░░░░░░░░░░░░█░
████──░█░████░░░░░░░░█░
█──█──████──████░░░░░█░
█──█──█──█──█──████████
█──█──████──█──█──────█
█──█──█──█────██──██──█
█──████──█──█──█──────█
█─────█──█──█──█──█████
███████──████──█──────█
──────████──██████████
""")
        print("Sustainable software practices")

if __name__ == "__main__":
    main()

