# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 23:18:09 2018

@author: Christian Jung

Schnittstelle über COM4, Änderung in Zeile 237
ID=32 eingeben
dann set U/I mode drücken 
power eingeben in Watt

"""

import serial, time
import tkinter as tk


class aeconversion(object):

    def ser_open(self,ser):
        ser.close()
        try:
            ser.open()   
        except Exception:
            print ('Der serielle Port konnte nicht geoeffnet werden')
            exit()
        ser.flushInput() 								# Eingangspuffer leeren
        ser.flushOutput()								# Ausgangspuffer leeren    
        return()
        
        
    def query(self, value):    
        self.ser.write(value)
        value = ""
        val=self.ser.readline()   
        if val.decode() !='\n':
            self.error=True
        val=self.ser.readline()          
#       starttime=time.time()
#        while not chr(13) in val.decode():
#           value = "%s%s"%(value, val.decode())
#           val = self.ser.read()
#           if (time.time()-starttime)>self.timeout: 
#               print('no response AEConversion after {}s-> timeout and exit'.format(self.timeout))
#               raise ValueError("%s%s"%(value,val))                     
#               break
#        value = "%s%s"%(value, val.decode())
        if len(val)>0 and val[-1]==13:
           value=val[:-2].decode()
        else:
           self.error = True
        return value        
        
    
    def wr_read(_wr_message_hex):								# Abfrage des Wechselrichters
    	_wr_error = ""
    	try:
    		ser.open()
    	except Exception:
    		_wr_error = "Der serielle Port konnte nicht geoeffnet werden:"    #+ str(e)
    		exit()
    	if ser.isOpen():
    		try:
    			ser.flushInput() 								# Eingangspuffer leeren
    			ser.flushOutput()								# Ausgangspuffer leeren
    			ser.write(_wr_message_hex)
    			time.sleep(0.5)  								# Pause vor Datenempfang
    			_wr_response_hex = ser.readline().encode("hex")	# Antwort des Wechselrichters
    			ser.close()
    		except Exception:
    			_wr_error = "Kommunikationsfehler: "      # + str(e1)
    			
    	else:
    		_wr_error = "Der com-Port konnte nicht geoeffnet werden"
    	
    	if _wr_error == "":
    		return _wr_response_hex
    	else:
    		return _wr_error
                
    def BquitClick(self):
        self.Bui['bg']='red'  
        self.ser.close()
        return()
        
        
    def BmodeClick(self):  
       value =self.query(self.mode)             #disable MPP Tracking  #<ID>B_m_uu.u<CR>        
       if value== self.mode_result:                      
            self.Bui['bg']='green' 
       else:                      
            self.Bui['bg']='red'                   
       return()
        
       
    def update(self):
        if self.Bui['bg']=='green' :
            value =self.query(self.ask)
            self.Vbat=value[9:14]
            self.Ibat=value[15:20]
            self.Pbat=value[21:26]
            Vnetz=value[27:32]
            Inetz=value[33:38]
            self.Pnetz=value[39:44]
            Temp=value[45:48]
            Energie=value[49:]
            if float(self.Pbat)>0.0:
                self.Eta='{:.2f}'.format(float(self.Pnetz)/float(self.Pbat))
            else: self.Eta=1.0   
            self.sVbat.set(self.Vbat)  
            self.sIbat.set(self.Ibat)           
            self.sPbat.set(self.Pbat)  
            self.sVnetz.set(Vnetz)  
            self.sInetz.set(Inetz)           
            self.sPnetz.set(self.Pnetz)   
            self.sT.set(Temp) 
            self.sWh.set(Energie)   
            self.sEta.set(self.Eta)   
            print(value)
        self.frame.after(500,self.update)    
        return()
        
        
    def Newid(self,einput):
        newid=int(self.Lid.get())    
        self._id=newid  
        self.typ=('#'+str(self._id)+'9\r').encode()            #abfrage Wechselrichtertyp, Antwort: *329 500-90 3\r'
        self.mode=('#'+str(self._id)+'B_2_50.0\r').encode()    #<ID>B_m_uu.u<CR> Antwort: <LF>*<ID>B_m_uu.u_z<CR> 
        self.mode_result='*'+str(self._id)+'B 2 50.0 '           
        
        self.askcurrent=('#'+str(self._id)+'S\r').encode()
        self.ask=('#'+str(self._id)+'0\r').encode()       #Messwerte abfragen
                                    #b'*320   0  51.3  0.00   493   0.0  0.02     1  50    237 \xf4\r'
                                    #        status V   I-in  P-in V-out  I-out  P-out T   WH   
                                    #  *320   0  51.2  1.49    75 232.1  0.33    71  50    243 -\r
                                    #'b'*320   0  51.2  2.77   138 232.1  0.59   133  50    246 Y\r'        
        result=self.query(self.typ)  
        if not self.error:
            self.styp.set(result[5:]) 
        else:    
            self.styp.set('error')                          
        return()       
    
    def Newcurrent(self,einput):     #<ID>S_ii.i<CR> Antwort: <LF>*<ID>S_ii.i_z ii.i ist die Stromvorgabe 
        try:
            power=float(self.Lpower.get())							# eingebene Leistung abfragen
            current=power/float(self.Vbat)/float(self.Eta)			# und umrechnen in benötigten Strom
            if current<10.0:
                scurrent=('#'+str(self._id)+'S_0{:0.1f}\r'.format(current)).encode()
            elif current<20.0: 
                scurrent=('#'+str(self._id)+'S_{:0.1f}\r'.format(current)).encode()
            result=self.query(scurrent) 
            if result[0:5]=='*32S ':
                result= result[6:-1]
            else:
                result='ackn error'
                self.error = True                
        except:
            result='wrong input' 
        self.scurrent.set(result)  									# Strom setzen
        return()
    
    
    
    def __init__(self,frame,_id=32):
                          #=AESGI-Adresse: 32, ist die zweistellige WR-Nummer, _ ist ein Leerzeichen, z die Prüfsumme
                          
        self._id=_id   
        self.frame=frame
        self.frame.grid()
        self.timeout=20000
        self.error=False
               
        fontsize = ("Helvitica",11)  

        self.Vbat=0.0
        self.Ibat=0.0
        self.Pbat=0.0   
        self.eta=1.0

        tk.Label(self.frame,font=fontsize,text='ID:').grid(row=1,column=1)  
        tk.Label(self.frame,font=fontsize,width=10,text='              ').grid(row=1,column=3)  
        tk.Label(self.frame,font=fontsize,text='Typ:').grid(row=2,column=1)          
        tk.Label(self.frame,font=fontsize,text='set Current:').grid(row=3,column=1) 
        tk.Label(self.frame,font=fontsize,text='Vbat:').grid(row=4,column=1) 
        tk.Label(self.frame,font=fontsize,text='Ibat:').grid(row=5,column=1) 
        tk.Label(self.frame,font=fontsize,text='Pbat:').grid(row=6,column=1) 
        tk.Label(self.frame,font=fontsize,text='Vnetz:').grid(row=7,column=1) 
        tk.Label(self.frame,font=fontsize,text='Inetz:').grid(row=8,column=1) 
        tk.Label(self.frame,font=fontsize,text='Pnetz:').grid(row=9,column=1)       
        tk.Label(self.frame,font=fontsize,text='T:').grid(row=10,column=1) 
        tk.Label(self.frame,font=fontsize,text='Wh:').grid(row=11,column=1) 
        
        self.scurrent=tk.StringVar()
        self.styp=tk.StringVar()
        self.sVbat=tk.StringVar()
        self.sIbat=tk.StringVar()
        self.sPbat=tk.StringVar()
        self.sVnetz=tk.StringVar()
        self.sInetz=tk.StringVar()
        self.sPnetz=tk.StringVar()
        self.sT=tk.StringVar()
        self.sWh=tk.StringVar()       
        self.sEta=tk.StringVar()               
        tk.Label(self.frame,font=fontsize,textvariable=self.scurrent).grid(row=3,column=3) 
        tk.Label(self.frame,font=fontsize,textvariable=self.styp).grid(row=2,column=2)     
        tk.Label(self.frame,font=fontsize,textvariable=self.sVbat).grid(row=4,column=2) 
        tk.Label(self.frame,font=fontsize,textvariable=self.sIbat).grid(row=5,column=2) 
        tk.Label(self.frame,font=fontsize,textvariable=self.sPbat).grid(row=6,column=2) 
        tk.Label(self.frame,font=fontsize,textvariable=self.sVnetz).grid(row=7,column=2) 
        tk.Label(self.frame,font=fontsize,textvariable=self.sInetz).grid(row=8,column=2) 
        tk.Label(self.frame,font=fontsize,textvariable=self.sPnetz).grid(row=9,column=2)         
        tk.Label(self.frame,font=fontsize,textvariable=self.sT).grid(row=10,column=2) 
        tk.Label(self.frame,font=fontsize,textvariable=self.sWh).grid(row=11,column=2)         
        tk.Label(self.frame,font=fontsize,textvariable=self.sEta).grid(row=9,column=3)  
          
        self.Lid = tk.Entry(self.frame,font=fontsize,width=5)       
        self.Lid.insert(5,'')
        self.Lid.bind('<Return>',self.Newid)   
        self.Lid.grid(row=1,column=2)   
        self.Lpower = tk.Entry(self.frame,font=fontsize,width=5)       
        self.Lpower.insert(5,'')
        self.Lpower.bind('<Return>',self.Newcurrent)   
        self.Lpower.grid(row=3,column=2)   
        
        self.styp=tk.StringVar()
        self.ltyp=tk.Label(self.frame,font=fontsize,textvariable=self.styp)
        self.ltyp.grid(row=2,column=2,columnspan=10,in_=self.frame)               


        self.Bui=tk.Button(self.frame,text="Set U/I mode",font=fontsize,command=self.BmodeClick)
        self.Bui.grid(row=3,column=1)       
        tk.Button(self.frame,text="Quit",font=fontsize,command=self.BquitClick).grid(row=15,column=1)       

        self.ser = serial.Serial(										# Initialieren der RS485 Schnittstelle
        	#port = "/dev/ttyUSB0",
        	port = "COM4",    
        	baudrate = 9600,
        	bytesize = serial.EIGHTBITS,
        	parity = serial.PARITY_NONE,
        	stopbits = serial.STOPBITS_ONE,
        	timeout = 1,
        	xonxoff = False,
        	rtscts = False,
        	dsrdtr = False,
        	writeTimeout = 2
        )
        self.ser.close()  
        self.ser.open()        
        self.styp.set('unknown')  
        self.scurrent.set('unknown')   

    
        self.frame.after(1000,self.update)
        self.frame.mainloop()    



if __name__ == '__main__':
     root = tk.Tk()     
     display=aeconversion(root,tk)   
