import multiprocessing
import os

from cminmax_main_odd import Odd
from cminmax_main_even_select_side import Even

p = "./instances/"
cores = 60
timelimit = 3600*4
memLimit = 110

# Crear una lista para almacenar los archivos y sus valores NV
files_with_nv = []

# Leer los archivos y extraer los valores NV
for file in os.listdir(p):
    file_path = os.path.join(p, file)
    with open(file_path, 'r') as f:
        line = f.readline()
        while "#" in line:
            line = f.readline()

        # Primera línea podría tener dos formatos:
        # 10 6
        if len(line.split()) == 2:
            NV, NE = map(int, line.split())
        # NV:10 NE:6
        else:
            NV, NE = map(int, line.split()[1::2])
        files_with_nv.append((NV, file_path))

# Ordenar la lista por NV de menor a mayor
files_with_nv.sort()

# Procesar los archivos en orden
for NV, file_path in files_with_nv:
    try:
        if NV % 2 == 0:
            model = Even(file_path, cores, timelimit,memLimit)
        else:
            model = Odd(file_path, cores, timelimit,memLimit)

        model.run()
    except Exception as e:
        print(f"Error code: {e}")
        print(f"Error message: {str(e)}")
