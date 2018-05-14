import csv, math, random
from matplotlib import pyplot as plt

# Pedir nombre de documento con coordenadas
nombre = raw_input("Ingrese el nombre del documento con las coordenadas: ")

# Abrir y leer documento
with open(nombre, "r") as doc:
	reader = csv.reader(doc)
	datos = list(reader)

# Limpiar datos
coordenadas = map(lambda x: [float(i) for i in x[:-1]], datos[1:])
vdatos = zip(*coordenadas)

# Sacar minimos, maximos y diferencias de coordenadas en X y Y
lon_min, lon_max = min(vdatos[0]), max(vdatos[0])
lat_min, lat_max = min(vdatos[1]), max(vdatos[1])
lon_delta = lon_max - lon_min
lat_delta = lat_max - lat_min

# Normalizar los datos
datos = map(lambda x: [(x[0] - lon_min)/lon_delta, (x[1] - lat_min)/lat_delta], coordenadas)

# Construir matriz de distancias PLANAS
ciudades = len(datos)
distancias = [[0.0] * ciudades for i in range(ciudades)]
for j in range(ciudades):
	for k in range(ciudades):
		distancias[j][k] = ( (datos[j][0] - datos[k][0])**2 + (datos[j][1] - datos[k][1])**2 )**0.5

# Construir matriz de distancias ESFERICAS
arcos = [[0.0] * ciudades for i in range(ciudades)]
for j in range(ciudades):
	for k in range(ciudades):
		y = abs(coordenadas[j][0] - coordenadas[k][0]) * 110547
		x = abs(coordenadas[j][1] - coordenadas[k][1]) * 111320 * math.cos( math.radians( coordenadas[j][0] - coordenadas[k][0] ) )
		arcos[j][k] = ( x**2 + y**2 )**0.5

# Calcular la distancia del recorrido
def recorrido(secuencia, dist_mat):
	total = dist_mat[ secuencia[0] ][ secuencia[-1] ]	
	for i in range(len(secuencia) - 1):
		total += dist_mat[ secuencia[i] ][ secuencia[i+1] ]	
	return total	

# Invertir un segmento de la ruta
def invertir(secuencia):
	nueva_secuencia = secuencia[:]
	llaves = random.sample(nueva_secuencia, 2)
	llaves.sort()
	segmento = nueva_secuencia[ llaves[0] : llaves[1] ]
	nueva_secuencia[ llaves[0] : llaves[1] ] = segmento[::-1]
	return nueva_secuencia

# Enfriamiento simulado
def enfriamiento_simulado(coords, tempi, steps, optfunc, temp_prog=0):
	temp_funt = []
	const1 = steps / math.log(tempi + 1.0)
	const2 = float(tempi) / steps ** 2
	const3 = - tempi / float(steps)
	temp_funt.append( lambda t: math.e ** (- (t - steps) / const1) - 1 )
	temp_funt.append( lambda t: const2 * (t - steps) ** 2 )
	temp_funt.append( lambda t: const3 * t + tempi )
	f = open("rutas.txt", "w")
	f.writelines("Rutas evaluadas\nDimensiones: " + str(len(coords)) + "\n")
	f.close()
	try:
		cooling = temp_funt[temp_prog]
	except IndexError as err:
		print err
		return None
	ruta = range(len(coords))
	random.shuffle(ruta)
	dist = optfunc(ruta, distancias)
	for j in range(steps):
		f = open("rutas.txt", "a")
		f.writelines(str(ruta) + ", " + str(dist))
		n_ruta = invertir(ruta)
		n_dist = optfunc(n_ruta, distancias)
		if n_dist < dist:
			ruta = n_ruta[:]
			dist = n_dist
		elif n_dist >= dist:
			cte = math.e ** (- (n_dist - dist) / cooling(j) )
			if cte >= random.random() and cte < 1:
				ruta = n_ruta[:]
				dist = n_dist
		f.writelines("\n")
		f.close()
	return ruta, dist

# Ver mapa de la ruta propuesta
def ver_ruta(ruta, datos, distancia, imagen="ruta_"):
	mapa = [datos[i] for i in ruta]
	mapa.append(mapa[0])
	tabla = zip(*mapa)
	plt.clf()
	plt.plot(tabla[1], tabla[0], "bo-")
	plt.savefig(imagen + str(distancia) + ".png")

rta, dis = enfriamiento_simulado(datos, 200, 500000, recorrido)
caminar = recorrido(rta, arcos)
print("Distancia minima hallada: " + str(caminar) + " metros")
ver_ruta(rta, datos, dis)
