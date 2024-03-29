#!/usr/bin/env python
import rospy
from PCANBasic import *
import time                    ## Time-related library
import threading               ## Threading-based Timer library
from pcan.msg import Twist1
import numpy as np
m_CanRead = True
m_IsFD = False
m_PcanHandle = PCAN_USBBUS1
Acceleration_fin =[]
e2OCAN_RNDB = TPCANMsg()
e2OCAN_LAMP = TPCANMsg()
e2OCAN_STEER = TPCANMsg()
e2OCAN_BRAKE = TPCANMsg()
e2OCAN_ACCEL = TPCANMsg()
e2OCAN_WIPHORN = TPCANMsg()
b=0
s=0
Acceleration_fin=[]
for i in range(8):
	e2OCAN_RNDB.DATA[i] = 0x00
	e2OCAN_LAMP.DATA[i] = 0x00
	e2OCAN_STEER.DATA[i] = 0x00
	e2OCAN_BRAKE.DATA[i] = 0x00
	e2OCAN_ACCEL.DATA[i] = 0x00
	e2OCAN_WIPHORN.DATA[i] = 0x00

e2OCAN_RNDB.ID = 0x778
e2OCAN_RNDB.MSGTYPE = PCAN_MESSAGE_STANDARD
e2OCAN_RNDB.LEN = 8

e2OCAN_LAMP.ID = 0x776
e2OCAN_LAMP.MSGTYPE = PCAN_MESSAGE_STANDARD
e2OCAN_LAMP.LEN = 8

e2OCAN_STEER.ID = 0x774
e2OCAN_STEER.MSGTYPE = PCAN_MESSAGE_STANDARD
e2OCAN_STEER.LEN = 8

e2OCAN_BRAKE.ID = 0x772
e2OCAN_BRAKE.MSGTYPE = PCAN_MESSAGE_STANDARD
e2OCAN_BRAKE.LEN = 8

e2OCAN_ACCEL.ID = 0x770
e2OCAN_ACCEL.MSGTYPE = PCAN_MESSAGE_STANDARD
e2OCAN_ACCEL.LEN = 8

e2OCAN_WIPHORN.ID = 0x76D
e2OCAN_WIPHORN.MSGTYPE = PCAN_MESSAGE_STANDARD
e2OCAN_WIPHORN.LEN = 8

RNDB_NEUTRAL = 0x14
RNDB_REVERSE = 0x0C
RNDB_DRIVE = 0x24
RNDB_BOOST = 0x84

LAMP_OFF = 0x09
LAMP_RIND = 0x19
LAMP_LIND = 0x89
LAMP_HAZARD = 0x99
LAMP_LBEAM = 0x0B
LAMP_HBEAM = 0x0D
LAMP_BKLIGHT_B7 = 0x09
LAMP_BKLIGHT_B6_ON = 0xE0
LAMP_BKLIGHT_B6_OFF = 0x20

STEER_ZERO = 0x01
STEER_LEFT = 0xA2
STEER_RIGHT = 0xA1

BRAKE_ZERO = 0x01
BRAKE_FULL = 0xC9

ACCEL_ZERO = 0x01
ACCEL_FULL = 0xC9

WIPER_OFF = 0x20
WIPER_INT = 0x60
WIPER_HIGH = 0xA0
HORN_ON = 0x18
HORN_OFF = 0x08

m_objPCANBasic = PCANBasic()
print("PCAN_CHANNEL_CONDITION (Before) = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_CHANNEL_CONDITION)))

Status = m_objPCANBasic.Initialize(m_PcanHandle, PCAN_BAUD_500K, 0, 0, 0)
print(Status)
i=0
print "i :", i
print("PCAN_DEVICE_NUMBER = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_DEVICE_NUMBER)))
print("PCAN_API_VERSION= " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_API_VERSION)))
print("PCAN_HARDWARE_NAME = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_HARDWARE_NAME)))
print("PCAN_CHANNEL_CONDITION = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_CHANNEL_CONDITION)))
print("PCAN_CHANNEL_VERSION = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_CHANNEL_VERSION)))
print("PCAN_BITRATE_INFO = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_BITRATE_INFO)))
print("PCAN_BUSSPEED_NOMINAL = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_BUSSPEED_NOMINAL)))
print("PCAN_RECEIVE_STATUS = " + str(m_objPCANBasic.GetValue(m_PcanHandle, PCAN_RECEIVE_STATUS)))

with open("/sys/class/pcan/version") as f:
	version = f.readline()
	print(version)

e2OCAN_LAMP.DATA[6] = 0x20
e2OCAN_STEER.DATA[6] = 0xC0

e2OCAN_RNDB.DATA[6] = RNDB_NEUTRAL
e2OCAN_LAMP.DATA[7] = LAMP_HAZARD
e2OCAN_STEER.DATA[7] = STEER_ZERO
e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
e2OCAN_WIPHORN.DATA[7] = WIPER_OFF | HORN_OFF

def ChangeHex(n):
	x = (n % 16)
	c = ""
	if (x < 10):
		c = x
	if (x == 10):
		c = "A"
	if (x == 11):
		c = "B"
	if (x == 12):
		c = "C"
	if (x == 13):
		c = "D"
	if (x == 14):
		c = "E"
	if (x == 15):
		c = "F"

	if (n - x != 0):
		return ChangeHex(n / 16) + str(c)
	else:
		return str(c)

def ReadMessages():
	try:
		stsResult = PCAN_ERROR_OK
		while (not (stsResult & PCAN_ERROR_QRCVEMPTY)):
			result = m_objPCANBasic.Read(m_PcanHandle)
			stsResult = result[0]
			if result[0] == PCAN_ERROR_OK:
				newMsg = result[1]
				msgTimeStamp = result[2]
				#msgTimeStamp.value = (msgTimeStamp.micros + 1000 * msgTimeStamp.millis + 0x100000000 * 1000 * msgTimeStamp.millis_overflow)

				#print(format(newMsg.ID,'04x'))
				MsgID = format(newMsg.ID,'04x')
				DATA7 = format(newMsg.DATA[7],'02x')
				DATA6 = format(newMsg.DATA[6],'02x')
				if (MsgID == '076c'):
					print "Vehicle speed status"
					print "\nSpeed of Car : ", int(DATA7,16)
				elif (MsgID == '076e'):
					print "\n\nWiper & Horn Status"
					if(DATA7 == 'a0'):
						print "\nWiper : ON \nHorn : ON"
					elif(DATA7 == '20'):
						print "\nWiper : OFF \nHorn : ON"
					elif(DATA7 == '80'):
						print "\nWiper : ON \nHorn : OFF"
					elif(DATA7 == '00'):
						print "\nWiper : OFF \nHorn : OFF"
				elif (MsgID == '0771'):
					print "\n\nThrottle Status"
					Throttle = DATA7
					print "\nThrottel Percentage of Car : ", int(Throttle,16)/2
				elif (MsgID == '0773'):
					print "Braking Status"
					Brake = DATA7
					print "\nBraking Percentage of Car : ", int(Brake,16)/2
				elif (MsgID == '0775'):
					print "\n\nSteering angle & Steering Direction Status"
					Steer = DATA7
					Steer_bin = bin(int(Steer,16))
					#if(Steer_bin[8] == '0' and Steer_bin[9] == '1'):
					#	print "\nSteering Direction : Clockwise"
					#elif(Steer_bin[8] == '1' and Steer_bin[9] == '0'):
					#	print "\nSteering Direction : AntiClockwise"

					#Steer_angle = 32*int(Steer_bin[2]) + 16*int(Steer_bin[3]) + 8*int(Steer_bin[4]) + 4*int(Steer_bin[5]) + 2*int(Steer_bin[6]) + int(Steer_bin[7])
					#print "\n Steering Angle : ",Steer_angle
					#Steering Angle yet to be done

				elif (MsgID == '0777'):
					print "\n\nTurn Indicators & HL Beam"
					if(DATA7[0] == '8'):
						print "\nIndicator Status : Left Indicator"
					elif(DATA7[0] == '1'):
						print "\nIndicator Status : Right Indicator"
					elif(DATA7[0] == '9'):
						print "\nIndicator Status : Hazard Indicator"
					elif(DATA7[0] == '0'):
						print "\nIndicator Status : OFF"

					if(DATA7[1] == '4'):
						print "\nHead Lights : ON"
					elif(DATA7[1] == '0'):
						print "\nHead Lights : OFF"
				elif (MsgID == '0779'):
					print "\n\nDriving Mode & PRNDL Status"
					
					if(DATA7 == '40'):
						print "\nDriving Mode : Manual"
					elif(DATA7 == '80'):
						print "\nDriving Mode : Autonomous"
					elif(DATA7 == 'c0'):
						print "\nDriving Mode : Homing in Progress"
					else:
						print "\nDriving Mode : Invalid"

					if(DATA6 == '08'):
						print "\nGear Status : Reverse"
					elif(DATA6 == '10'):
						print "\nGear Status : Neutral"
					elif(DATA6 == '20'):
						print "\nGear Status : Drive"
					elif(DATA6 == '80'):
						print "\nGear Status : Boost"
					else:
						print "\nGear Status : Invalid"


				#print(msgTimeStamp.value)

				#for i in range(newMsg.LEN):
				#    print(format(newMsg.DATA[i],'02x'))
	except KeyboardInterrupt:
		tmrRead.stop()
		m_objPCANBasic.Uninitialize(m_PcanHandle)
		raise SystemExit, 1

def WriteMessages():
	try:
		m_objPCANBasic.Write(m_PcanHandle, e2OCAN_RNDB)
		m_objPCANBasic.Write(m_PcanHandle, e2OCAN_LAMP)
		m_objPCANBasic.Write(m_PcanHandle, e2OCAN_STEER)
		m_objPCANBasic.Write(m_PcanHandle, e2OCAN_BRAKE)
		m_objPCANBasic.Write(m_PcanHandle, e2OCAN_ACCEL)
		m_objPCANBasic.Write(m_PcanHandle, e2OCAN_WIPHORN)
	except KeyboardInterrupt:
		tmrWrite.stop()
		m_objPCANBasic.Uninitialize(m_PcanHandle)
		raise SystemExit, 1

###*****************************************************************
### Timer class
###*****************************************************************
class TimerRepeater(object):
	"""
	A simple timer implementation that repeats itself
	"""
	# Constructor
	def __init__(self, name, interval, target, isUi, args=[], kwargs={}):
		"""
		Creates a timer.
		Parameters:
			name        name of the thread
			interval    interval in second between execution of target
			target      function that is called every 'interval' seconds
			args        non keyword-argument list for target function
			kwargs      keyword-argument list for target function
		"""
		# define thread and stopping thread event
		self._name = name
		self._thread = None
		self._event = None
		self._isUi = isUi
		# initialize target and its arguments
		self._target = target
		self._args = args
		self._kwargs = kwargs
		# initialize timer
		self._interval = interval
		self._bStarted = False

	# Runs the thread that emulates the timer
	def _run(self):
		"""
		Runs the thread that emulates the timer.
		Returns:
			None
		"""
		while not self._event.wait(self._interval):
			if self._isUi:
				# launch target in the context of the main loop
				root.after(1, self._target,*self._args, **self._kwargs)
			else:
				self._target(*self._args, **self._kwargs)

	# Starts the timer
	def start(self):
		# avoid multiple start calls
		if (self._thread == None):
			self._event = threading.Event()
			self._thread = threading.Thread(None, self._run, self._name)
			self._thread.start()

	# Stops the timer
	def stop(self):
		if (self._thread != None):
			self._event.set()
			self._thread = None


def callback(msg):
	global n,b,r,l,s
	#global Acceleration_fin
	#Acceleration_fin='0x00'
	#Acceleration_final = ChangeHex(n*2+1) # n is the acceleartion 0-100 a is what we get from controller
	#Brake_final = ChangeHex(b*2+1) #b is the brake 0-100 , b is what we get from controller
	#Steering_angle_left = ChangeHex(s*8 + 2) # s is the angle to be turned
	#Steer_angle_right = ChangeHex(s*8 + 1) # s is the angle to be turned
	if msg.linear.x > 0:
		if flag_x == 1:
			n=0
		else:
			n=n+1
			if n>100:
				n=100
			e2OCAN_RNDB.DATA[6] = RNDB_DRIVE
			e2OCAN_ACCEL.DATA[7] = n*2+1
			
			#e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
			#e2OCAN_STEER.DATA[7] = abs(s)*4+2
			print 'wooo'
	elif (msg.linear.x < 0):
		if flag_x == 1:
			b=0
		else:
			b=b+1
			if b>100:
				b=100
		
		e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
		e2OCAN_BRAKE.DATA[7] = b*2+1
		#e2OCAN_STEER.DATA[7] = abs(s)*4+2
		#e2OCAN_ACCEL.DATA[7] = b*2+1
		#e2OCAN_RNDB.DATA[6] = RNDB_DRIVE
		#e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
		#e2OCAN_STEER.DATA[7] = abs(s)*4+2
		e2OCAN_RNDB.DATA[7] = RNDB_NEUTRAL

	if msg.linear.y < 0:
		s=s-1
		if s < -40 :
			s = -40

		if s<0:
			e2OCAN_RNDB.DATA[6] = RNDB_DRIVE
			e2OCAN_STEER.DATA[7] = s*8+2
			e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
			
			e2OCAN_LAMP.DATA[7] = LAMP_LIND
			e2OCAN_LAMP.DATA[6] = LAMP_BKLIGHT_B6_OFF
			e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
		else:
			e2OCAN_RNDB.DATA[6] = RNDB_DRIVE
			e2OCAN_STEER.DATA[7] = abs(s)*4+1
			e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
			
			e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
		

	elif msg.linear.y > 0:
		s=s+1
		if s > 40:
			s=40

		if s>0:
			e2OCAN_RNDB.DATA[6] = RNDB_DRIVE
			e2OCAN_STEER.DATA[7] = s*8+1
			e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
			
			e2OCAN_LAMP.DATA[7] = LAMP_RIND
			e2OCAN_LAMP.DATA[6] = LAMP_BKLIGHT_B6_OFF
			e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
		else:
			e2OCAN_STEER.DATA[7] = s*4+2
			e2OCAN_RNDB.DATA[6] = RNDB_DRIVE
			e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
			
			e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO



	if msg.linear.z > 0:
		e2OCAN_LAMP.DATA[7] = LAMP_HBEAM
		e2OCAN_LAMP.DATA[6] = LAMP_BKLIGHT_B6_OFF
	elif msg.linear.z < 0:
		e2OCAN_LAMP.DATA[7] = LAMP_LBEAM
		e2OCAN_LAMP.DATA[6] = LAMP_BKLIGHT_B6_OFF

	if msg.linear.x == 0 and msg.linear.y == 0 and msg.linear.z == 0 :
		e2OCAN_ACCEL.DATA[7] = ACCEL_ZERO
		e2OCAN_BRAKE.DATA[7] = BRAKE_ZERO
		e2OCAN_LAMP.DATA[7] = LAMP_BKLIGHT_B7
		e2OCAN_LAMP.DATA[6] = LAMP_BKLIGHT_B6_ON
		e2OCAN_RNDB.DATA[7] = RNDB_NEUTRAL
		e2OCAN_STEER.DATA[7] = s*4+2

	if msg.wiper > 0 :
		e2OCAN_WIPHORN.DATA[7] = WIPER_HIGH
	elif msg.wiper == 0 :
		e2OCAN_WIPHORN.DATA[7] = WIPER_INT
	elif msg.wiper < 0 :
		e2OCAN_WIPHORN.DATA[7] = WIPER_OFF
	global flag_x,flag_y
	prev_x= msg.linear.x
	prev_y= msg.linear.y
	prev_z= msg.linear.z
	if prev_x == 0:
		flag_x=1
	else:
		flag_x=0

	if prev_y == 0:
		flag_y=1
	else:
		flag_y=0



rospy.init_node('e2oMove')
sub = rospy.Subscriber('cmd_vel', Twist1, callback)
tmrRead = TimerRepeater("tmrRead", 0.010, ReadMessages, False)
tmrWrite = TimerRepeater("tmrWrite", 0.010, WriteMessages, False)
tmrWrite.start()
tmrRead.start()
rospy.spin()
#o1yPjTaQ