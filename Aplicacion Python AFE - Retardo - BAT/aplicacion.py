import sys

from Tkinter import *
import tkMessageBox
import time
import sys
import serial
import time
import pylab as pl
import scipy.io
import scipy
import scipy.signal
import numpy as np
from peakutils.plot import plot as pplot
from scipy.io import loadmat


#####################################################################################
# Metodo grabartxt
# Recibe:
#   - Datos a guardar en un txt
#   - Nombre del fichero txt
#####################################################################################
def grabartxt(filas, name):
 archi=open(name,'a')
 for j in range(0,len(filas),1):
  for h in range (0, len(filas[j]),1):
   archi.write(filas[j][h])
   archi.write(' ')
  archi.write('\n')
 archi.close()


#####################################################################################
# Metodo grabartxt
# Recibe:
#   - Datos a guardar en un txt
#   - Nombre del fichero txt
# Salida
#   - Guarda en ficheros txt los valores de la senhal PPG y del giroscopio 
#####################################################################################
def grabartxt_senhales(datos, nombreFichero):
 archi=open(nombreFichero,'w')
 for j in range(0,len(datos),1):
  archi.write(str(datos[j]))
  archi.write(' ')
  archi.write('\n')
 archi.close()



#####################################################################################
# Metodo data:download
# Recibe:
#   - Nombre del fichero txt
#
#####################################################################################
def data_download(puerto, nombreFichero): 
 time.sleep(15)
 try:
  s = serial.Serial('%s' %puerto, 4000000)#windows
  #s = serial.Serial('/dev/ttyACM0', 9600)#ubuntu
 except:
  return 0
 s.timeout=1
 s.write('start')
 s.flush()
 list=[]
 a_escribir=[]
 i=0
 contador=0
 while(s.inWaiting()==0):
  contador+=1
 while(1):
  try:
   contador=0
   while(s.inWaiting()==0): 
    contador+=1
    if (contador>1000000):
     break
   if(s.inWaiting()>0):
    for i in range (0,16,1):
     # if i<=3:
     #  data = s.read()
     # if i>3 and i<8: 
      data = s.read()
      list.append(data.encode('hex'))
     # if i>=8: 
     #  data = s.read()
    a_escribir.append(list)
    list=[]
   else: 
    break;
  except:
   return 0
   break;
 grabartxt(a_escribir,nombreFichero)
 s.close()
 return 1




#####################################################################
#
# Metodo aviso finalizacion descarga o error durante la descarga
#
####################################################################
def Aceptar_descarga(puerto, nombreFichero):
 if (data_download(puerto, nombreFichero)):
  tkMessageBox.showinfo("FA WATCH", "Fichero descargado correctamente!")
 else:
  tkMessageBox.showinfo("FA WATCH", "Ha ocurrido un error :(. Desconecta el Reloj e intentalo de nuevo! asegurese antes de que el puerto COM es el correcto")








######################################################################
#
# Metodo para leer datos del fichero
#
######################################################################
def Procesado(fichero_reloj):
 filtro_fir='fir_gaussian_4'     #nombre del archivo que contiene los coeficientes del filtro fir
 filtro_iir='iir_0-3'            #nombre del fichero que contiene los coeficientes del filtro iir
 print (fichero_reloj)
 try:
  fichero=open(fichero_reloj)
  contenido=fichero.read()
  fichero.close()
 except:
  tkMessageBox.showinfo("FA WATCH", "El fichero que has seleccionado no existe o no esta en el directorio raiz, intentalo de nuevo!")
  return 0
 datos=contenido.split()
 
 #obtencion de datos
 led1=[]
 accelX=[]
 accelY=[]
 accelZ=[]
 giroX=[]
 giroY=[]
 giroZ=[]
 byteExtra=[]
 for z in range(0,len(datos),16):
  led1.append((int(datos[z],16) << 16) + (int(datos[z+1],16) << 8) + int(datos[z+2],16))
  accelX.append((int(datos[z+3],16) << 8) + (int(datos[z+4],16)))
  accelY.append((int(datos[z+5],16) << 8) + (int(datos[z+6],16)))
  accelZ.append((int(datos[z+7],16) << 8) + (int(datos[z+8],16))) 
  giroX.append((int(datos[z+9],16) << 8) + (int(datos[z+10],16)))
  giroY.append((int(datos[z+11],16) << 8) + (int(datos[z+12],16)))
  giroZ.append((int(datos[z+13],16) << 8) + (int(datos[z+14],16)))
  #byteExtra.append(int(datos[z+15],16)) 
  byteExtra.append(int(datos[z+15],16) << 5) 

  #accel.append((int(datos[z+3],16))/float(0xFF))        # Para Reescalar dividiendo por 255
#  if (int(datos[z+7],16)>0x7F):              #suma_simple
#   accel.append((-((int(datos[z+7],16))^0xFF )-1)/float(0x7F))     #suma_simple
#  else:                    #suma_simple
#   accel.append((int(datos[z+7],16))/float(0x7F))        #suma_simple

 giroX_plot=[]
 giroY_plot=[]
 giroZ_plot=[]
 giroXNorm=[]
 giroYNorm=[] 
 giroZNorm=[]
 accelX_plot=[]
 accelY_plot=[]
 accelZ_plot=[]
 accelXNorm=[]
 accelYNorm=[] 
 accelZNorm=[]

  #representacion de la senhal del giroscopio
 pl.figure()
 pl.plot(giroX,label="Giro eje X")
 pl.plot(giroY,label="Giro eje Y")
 pl.plot(giroZ,label="Giro eje Z")
 pl.title("Giro Signal Sin tratar")
 pl.xlabel("Samples")
 pl.ylabel("Degrees/s ")
 pl.legend(loc="best") 
 
 #------------------------------------------------
 #representacion de la senhal mV de bateria (3,7v)
 pl.figure()
 pl.plot(byteExtra,label="Nivel mV bateria")
 pl.title("BATERIA (milivoltios)")
 pl.xlabel("Samples")
 pl.ylabel("mV")
 pl.legend(loc="best") 
 #------------------------------------------------


 # ----------------------------------------------------------
 # tratamiento datos del giroscopio (normalizacion)
 for i in range(len(giroX)):
  # Si mayor es negativo si no positivo
  if(giroX[i]>=32768):
   giroX[i] = (giroX[i]-65536)
   giroX_plot.append(giroX[i]/float(32.768))
   # if giroX[i]/float(-32768) <= 0.0001:
   #  giroX[i] = 0
   # else:
   giroX[i] = giroX[i]/float(-32768)
   giroXNorm.append(giroX[i])
  else:
   giroX_plot.append(giroX[i]/float(32.768))
   # if giroX[i]/float(32768) <= 0.0001:
   #  giroX[i] = 0
   # else:
   giroX[i] = giroX[i]/float(32768)
   giroXNorm.append(giroX[i])    


#  print dato
  if(giroY[i]>=32768):
#   print 'Antes: ', dato
   giroY[i] = (giroY[i]-65536)
#   print 'Despues: ', dato
   giroY_plot.append(giroY[i]/float(32.768))

   giroY[i] = giroY[i]/float(-32768)
   giroYNorm.append(giroY[i])
  else:
   giroY_plot.append(giroY[i]/float(32.768))

   giroY[i] = giroY[i]/float(32768)
   giroYNorm.append(giroY[i]) 



#  print dato
  if(giroZ[i]>=32768):
#   print 'Antes: ', dato
   giroZ[i] = (giroZ[i]-65536)
#   print 'Despues: ', dato
   giroZ_plot.append(giroZ[i]/float(32.768))

   giroZ[i] = giroZ[i]/float(-32768)
   giroZNorm.append(giroZ[i]) 
  else:
   giroZ_plot.append(giroZ[i]/float(32.768))

   giroZ[i] = giroZ[i]/float(32768)
   giroZNorm.append(giroZ[i]) 

 

 ##----------------------------------------------------------------
 # Tratamiento datos senal ejes acelerometro
 # ----------------------------------------------------------------
 for i in range(len(accelX)):
  if(accelX[i]>=32768):
   accelX[i] = (accelX[i]-65536)
   accelX_plot.append(accelX[i]/float(4096))
   # if giroX[i]/float(-32768) <= 0.0001:
   #  giroX[i] = 0
   # else:
   accelXNorm.append(accelX[i]/float(-8*4096))
  else:
   accelX_plot.append(accelX[i]/float(4096))
   # if giroX[i]/float(32768) <= 0.0001:
   #  giroX[i] = 0
   # else:
   accelXNorm.append(accelX[i]/float(8*4096))



#  print dato
  if(accelY[i]>=32768):
#   print 'Antes: ', dato
   accelY[i] = (accelY[i]-65536)
#   print 'Despues: ', dato
   accelY_plot.append(accelY[i]/float(4096))

   accelYNorm.append(accelY[i]/float(-8*4096))
  else:
   accelY_plot.append(accelY[i]/float(4096))

   accelYNorm.append(accelY[i]/float(8*4096))




#  print dato
  if(accelZ[i]>=32768):
#   print 'Antes: ', dato
   accelZ[i] = (accelZ[i]-65536)
#   print 'Despues: ', dato
   accelZ_plot.append(accelZ[i]/float(4096))

   accelZNorm.append(accelZ[i]/float(-8*4096))
  else:
   accelZ_plot.append(accelZ[i]/float(4096))
   accelZNorm.append(accelZ[i]/float(8*4096))



 #representacion de la senhal original PPG
 pl.figure()
 pl.plot(led1, label="Original Signal")
 pl.title("PPG Signal")
 pl.xlabel("Samples")
 pl.ylabel("Amplitude")
 pl.legend(loc="best")



 
 #representacion de la senhal del Acelerometro
 pl.figure()
 pl.plot(accelX,label="Accel eje X")
 pl.plot(accelY,label="Accel eje Y")
 pl.plot(accelZ,label="Accel eje Z")
 pl.title("Acelerometer Signal")
 pl.xlabel("Samples")
 pl.ylabel("Aceleracion")
 pl.legend(loc="best") 




 #representacion de la senhal del giroscopio
 pl.figure()
 pl.plot(giroX_plot,label="Giro eje X")
 pl.plot(giroY_plot,label="Giro eje Y")
 pl.plot(giroZ_plot,label="Giro eje Z")
 pl.title("Giro Signal")
 pl.xlabel("Samples")
 pl.ylabel("Degrees/s ")
 pl.legend(loc="best") 




 #representacion de la senhal del giroscopio
 pl.figure()
 pl.plot(accelX_plot,label="Accel eje X")
 pl.plot(accelY_plot,label="Accel eje Y")
 pl.plot(accelZ_plot,label="Accel eje Z")
 pl.title("Accel Signal")
 pl.xlabel("Samples")
 pl.ylabel("Degrees/s ")
 pl.legend(loc="best") 



 #representacion de la senhal del giroscopio
 pl.figure()
 pl.plot(giroXNorm,label="Giro eje X Normalizado")
 pl.title("Giro X Normalizado")
 pl.xlabel("Samples")
 pl.ylabel("Degrees/s ")
 pl.legend(loc="best") 



 #representacion de la senhal del giroscopio
 pl.figure()
 pl.plot(giroYNorm,label="Giro eje Y Normalizado")
 pl.title("Giro Y Normalizado")
 pl.xlabel("Samples")
 pl.ylabel("Degrees/s ")
 pl.legend(loc="best") 



 #representacion de la senhal del giroscopio
 pl.figure()
 pl.plot(giroZNorm,label="Giro eje Z Normalizado")
 pl.title("Giro Z Normalizado")
 pl.xlabel("Samples")
 pl.ylabel("Degrees/s ")
 pl.legend(loc="best") 


 
# #obtencion de movimiento
#  dummy=[] #variable en la que se guarda informacion de cada muestra si se considera o no artefactada, 1 y 0 respectivamente.
#  umbral=0.9 #variable en la que se mantiene el valor umbral del acelerometro para evitar artefactos
#  #deteccion movimiento
#  accel_array=np.array(accel)  #paso de lista a array
#  led1_mov=np.array(led1)    #paso de lista a array
#  desfase=50     #tramo de comprovacion de datos con umbral superior al establecido 
#  for k in range(desfase,len(accel_array)-desfase,1):
#   movl=np.where(abs(accel_array[k-desfase:k])>umbral)
#   movh=np.where(abs(accel_array[k:k+desfase])>umbral)
#   if ((len(movl[0])>0) and (len(movh[0])>0)):# supera el umbral?
#    led1_mov[k]=led1_mov[k-1]
#    dummy.append(1)
#   else:
#    dummy.append(0)
 
#  #trazado de linea recta sobre tramos artefactados
#  led1_mov_2=np.array(led1)  #paso de lista a array
#  dummy_array=np.array(dummy)  #paso de lista a array
#  positions=np.where(dummy_array==0)
#  for z in range (1,len(positions[0]),1):
#   if(positions[0][z]-positions[0][z-1]>10):
#    pendiente=(led1_mov_2[positions[0][z]+desfase]-led1_mov_2[positions[0][z-1]+desfase])/float((positions[0][z]+desfase)-(positions[0][z-1]+desfase)) 
#    init=positions[0][z-1]+desfase
#    val=led1_mov_2[positions[0][z-1]+desfase]
#    for l in range (positions[0][z-1]+desfase,positions[0][z]+desfase,1):
#     pos=l-init
#     led1_mov_2[l]= (pos*pendiente)+val
 
 #filtrado FIR/IIR
 mat=loadmat(filtro_fir)
 low_pass=mat.get('Num')[0,:]
 a=1.0
 low_signal_mov=scipy.signal.lfilter(low_pass,a,led1)
 mat=loadmat(filtro_iir)
 sos=mat.get('SOS')
 band_signal_mov=scipy.signal.sosfilt(sos,low_signal_mov)
 
 #Filtrado Average
 #matriz_sin_average=np.array(led1_mov_2)
 matriz_sin_average=np.array(led1)
 lista_average=[]
 for j in range(0,len(matriz_sin_average)-100,1):
  lista_average.append(matriz_sin_average[j:j+100].mean())
 matriz_average_simple=np.array(lista_average)
 matriz=matriz_sin_average[50:len(matriz_sin_average)-50]-matriz_average_simple


 # Calculo de las variaciones de nivel de continua restando a la muestra i+1 la anterior (i)
 movimientos=[];
 # for i in range(0,len(led1)-1):
 for i in range(0,len(matriz_sin_average)-101):
 	# movimientos.append(abs(led1[i+1]-led1[i]))
 	movimientos.append(abs(matriz_average_simple[i]-matriz_sin_average[i+101]))
 movimientos_rep = np.array(movimientos)


 #representacion cambio niveles de continua
 pl.figure()
 pl.plot(movimientos_rep, label="Valor medio senal")
 pl.title("Valor medio 100 muestras")
 pl.xlabel("Samples")
 pl.ylabel("Amplitude")
 pl.legend(loc="best")

 #representacion de la senhal Average
 pl.figure()
 pl.plot(matriz, label="Average Signal")
 pl.title("Average Signal")
 pl.xlabel("Samples")
 pl.ylabel("Amplitude")
 pl.legend(loc="best")

  #representacion de la senhal FIR/IR
 pl.figure()
 pl.plot(band_signal_mov, label="FIR//IR Signal")
 pl.title("FIR/IR Signal")
 pl.xlabel("Samples")
 pl.ylabel("Amplitude")
 pl.legend(loc="best")


 #filtrado wavelet de ppg
 # 
 
 #Filtrado Wavelet
 # timestamp=np.linspace(200, len(band_signal_mov)+ 100,len(band_signal_mov)-100)
 # coefs=pywt.wavedec(led1_mov_2,wavelet='db4',level=8,mode='smooth')
 # cA8,cD8,cD7,cD6,cD5,cD4,cD3,cD2,cD1=coefs
 # cA8_2=np.zeros(len(cA8))
 # cD8_2=np.zeros(len(cD8))
 # cD6_2=np.zeros(len(cD6))
 # cD5_2=np.zeros(len(cD5))
 # cD4_2=np.zeros(len(cD4))
 # cD3_2=np.zeros(len(cD3))
 # cD2_2=np.zeros(len(cD2))
 # cD1_2=np.zeros(len(cD1))
 # line=np.linspace(50,len(matriz)+50,len(matriz))
 # coef_2=[cA8_2,cD8_2,cD7,cD6,cD5,cD4_2,cD3_2,cD2_2,cD1_2]
 # wavelet_signal=pywt.waverec(coef_2,'db4',mode='smooth')
 # timestamp=np.linspace(200, len(band_signal_mov)+ 100,len(matriz))
 # timestamp2=np.linspace(150, len(band_signal_mov)+ 150,len( wavelet_signal))
 # # representacion senhales filtradas
 # pl.figure()
 # pl.subplot(2,1,1)
 # pl.plot(band_signal_mov, label="FIR-IIR Filter")
 # pl.plot(timestamp,matriz, label="Smooth Filter")
 # pl.plot(timestamp2,wavelet_signal, label="Wavelet Filter")
 # pl.title("PPG Signal without DC component")
 # pl.xlabel("Samples")
 # pl.ylabel("Amplitude")
 # pl.legend(loc="best")
 # pl.subplot(2,1,2)
 # pl.plot(led1, label="Original Signal")
 # pl.plot(led1_mov_2, label="Original Signal with motion removed")
 # pl.title("PPG Signal")
 # pl.xlabel("Samples")
 # pl.ylabel("Amplitude")
 # pl.legend(loc="best")
 

 # Se graban las senhales de interes en un fichero txt
 nombreFichero = 'vector_PPG_original'
 grabartxt_senhales(led1, nombreFichero)

 # Ficheros giroscopio
 nombreFichero = 'vector_giroscopioXNorm'
 grabartxt_senhales(giroXNorm, nombreFichero)
 nombreFichero = 'vector_giroscopioYNorm'
 grabartxt_senhales(giroYNorm, nombreFichero)
 nombreFichero = 'vector_giroscopioZNorm'
 grabartxt_senhales(giroZNorm, nombreFichero)



 # Ficheros acelerometro SIN TRATAR
 nombreFichero = 'vector_accelX'
 grabartxt_senhales(accelX, nombreFichero)
 nombreFichero = 'vector_accelY'
 grabartxt_senhales(accelY, nombreFichero)
 nombreFichero = 'vector_accelZ'
 grabartxt_senhales(accelZ, nombreFichero)



 # Ficheros acelerometro NORMALIZADO
 nombreFichero = 'vector_accelXNorm'
 grabartxt_senhales(accelXNorm, nombreFichero)
 nombreFichero = 'vector_accelYNorm'
 grabartxt_senhales(accelYNorm, nombreFichero)
 nombreFichero = 'vector_accelZNorm'
 grabartxt_senhales(accelZNorm, nombreFichero)

 

 # # Se guarda la senhal PPG con diferentes filtros en fichero txt
 nombreFichero = 'vector_PPG_FIR'
 grabartxt_senhales(band_signal_mov, nombreFichero)
 # # # nombreFichero = 'vector_Wavelet'
 # # # grabartxt_senhales(accel, nombreFichero)
 nombreFichero = 'vector_PPG_Average'
 grabartxt_senhales(matriz, nombreFichero)
   
 # tkMessageBox.showinfo("Info", "Se ha generado correctamente los archivos")

 pl.show()





#################################################################################
#
# Metodo que procesa el fichero del holter para leer los intervalos del ECG
#
#################################################################################
def procesado_ECG(fichero_ECG):
  intervalos_RR_PPG = []
  try:
    fichero=open(fichero_ECG)
    contenido=fichero.read()
    fichero.close()
  except:
    print ('No se pudo abrir el fichero')
    tkMessageBox.showinfo("Error", "No se pudo abrir el fichero. Asegurese de que el nombre es correcto")
    return 0

  datos=contenido.split()

  #Se guardan los datos del fichero en listas
  intervalos_ECG=[]
  for z in range(0, len(datos),7):
    intervalos_ECG.append(datos[z+5])

  nombreFichero = 'vector_IECG'
  grabartxt_senhales(intervalos_ECG, nombreFichero)
  tkMessageBox.showinfo("Info", "Se ha generado correctamente el archivo con los intervalos ECG")




##################################################################################
# Buscar puertos series disposibles. 
# ENTRADAS:
#   -num_ports : Numero de puertos a escanear. Por defecto 20
#   -verbose   : Modo verboso True/False. Si esta activado se va 
#                imprimiendo todo lo que va ocurriendo
# DEVUELVE: 
#    Una lista con todos los puertos encontrados. Cada elemento de la lista
#    es una tupla con el numero del puerto y el del dispositivo 
##################################################################################
def scan(num_ports = 20, verbose=True):
   
    hay_puerto = False
    dispositivos_serie = []
    
    for i in range(num_ports):
    
      try:
        s = serial.Serial("COM%s" %i)    
        
        dispositivos_serie.append( (i, s.portstr))
        hay_puerto = True

        s.close()
             
      except:
        pass
        
    return (dispositivos_serie, hay_puerto)


	
	
#####################################################################################
# Metodo data: Enviar tiempo d retardo por USB
# Recibe: 
#   - Puerto serie y numero de horas.
#
#####################################################################################
def Enviar_minutos_de_retardo(puerto, minutos): 
	
 aux_minutos = int (minutos);	
	
 if (aux_minutos < 1081):

	time.sleep(15)
	
	s = serial.Serial('%s' %puerto, 4000000)#windows
	#s = serial.Serial('/dev/ttyACM0', 9600)#ubuntu
  
	s.timeout=1
	s.write(minutos + 'MINUTOS')
	s.flush()
 
	s.close()
	
	tkMessageBox.showinfo("FA WATCH", "" + minutos + " minutos de retado cargados correctamente!")
	
 else:
  tkMessageBox.showinfo("Error", "Introduzca un valor menor para el tiempo de retardo, el valor selecionado no esta permitido")
  

##########################################################################################################
# 
#  INICIO DEL PROGRAMA 
#
#########################################################################################################33
direc = sys.path[0]
print (direc) 
filename =(direc+ "/images/cardio.gif")
ventana=Tk()
ventana.geometry("840x450+200+200")
ventana.title("Descarga de Datos al PC")


######### Imagen de cardio ###########################################
#image1 = PhotoImage(file="cardio.gif")
#panel1 = Label(ventana, image=image1).place(x=200,y=320)

######### Buscamos los puertos que esten siendo usados ##################################3
(puertos_disponibles, hay_puerto)=scan(num_ports=20, verbose=True)

############### Etiqueta y boton para descargar los datos del reloj en un fichero ##########################################
etiqueta= Label(ventana,text="Introduce el nombre del nuevo fichero que quieres crear:",font=("Calibri",12),fg="black").place(x=20,y=10)
file_name=StringVar()
file_name.set("version_holter.%s.%s.%s-%s.%s.%s.txt"%(time.strftime("%Y"),time.strftime("%m"),time.strftime("%d"),time.strftime("%H"),time.strftime("%M"),time.strftime("%S")))
campo=Entry(ventana,textvariable=file_name).place(x=410,y=13)
etiqueta= Label(ventana,text="Introduce el puerto COM (ej: COM3):",font=("Calibri",12),fg="black").place(x=20,y=40)
numero_puerto=StringVar()
if hay_puerto:
  print (puertos_disponibles[0][1])
  numero_puerto.set("%s" %puertos_disponibles[0][1])
  campo=Entry(ventana,textvariable=numero_puerto).place(x=325,y=43)
  boton=Button(ventana,command=lambda: Aceptar_descarga(numero_puerto.get(), file_name.get() ),text="Descarga de datos del reloj").place(x=20,y=70)
#boton=Button(ventana,command=lambda: Aceptar_descarga(file_name.get()),text="Descarga de datos del reloj").place(x=20,y=70)
else:
  numero_puerto.set("")
  campo=Entry(ventana,textvariable=numero_puerto).place(x=325,y=43)
  boton=Button(ventana,command=lambda: Aceptar_descarga(numero_puerto.get(), file_name.get() ),text="Descarga de datos del reloj").place(x=20,y=70)
############### Etiqueta y boton para obtener los fichero con los vectores de informacion #############################
etiqueta= Label(ventana,text="Introduce el nombre del fichero del cual obtener los datos:",font=("Calibri",12),fg="black").place(x=20,y=145)
file_name_read_2=StringVar()
file_name_read_2.set("version_holter.%s.%s.%s-%s.%s.%s.txt"%(time.strftime("%Y"),time.strftime("%m"),time.strftime("%d"),time.strftime("%H"),time.strftime("%M"),time.strftime("%S")))
campo=Entry(ventana,textvariable=file_name_read_2).place(x=420,y=148)
#print file_name_read_2.get()
boton2=Button(ventana,command=lambda: Procesado(file_name_read_2.get()),text="Obtener ficheros con los datos PPG y giroscopio").place(x=20,y=170)


############### Etiqueta y boton para obtener los intervalos ECG #############################
etiqueta= Label(ventana,text="Introduce el nombre del fichero ECG:",font=("Calibri",12),fg="black").place(x=20,y=230)
file_name_read_3=StringVar()
file_name_read_3.set("")
campo=Entry(ventana,textvariable=file_name_read_3).place(x=280,y=233)
boton3=Button(ventana,command=lambda: procesado_ECG(file_name_read_3.get()),text="Obtener fichero con intervalos ECG").place(x=20,y=260)

############### Etiqueta y boton para ENViar tiempo de retardo por USB a la placa #############################
etiqueta= Label(ventana,text="Introduce el tiempo (en minutos) antes de comenzar con la medida:",font=("Calibri",12),fg="black").place(x=20,y=350)
file_name_read_4=StringVar()
#file_name_read_4=IntVar()
file_name_read_4.set("")
#file_name_read_4.set(0)
campo=Entry(ventana,textvariable=file_name_read_4).place(x=470,y=355)
etiqueta= Label(ventana,text=" (Maximo 1080 minutos) ",font=("Calibri",12),fg="black").place(x=600,y=350)
boton4=Button(ventana, command=lambda:  Enviar_minutos_de_retardo(numero_puerto.get(), file_name_read_4.get() ), text="Cargar tiempo de retardo a pulsera").place(x=20,y=380)



ventana.mainloop()

