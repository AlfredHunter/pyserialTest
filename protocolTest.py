#!/usr/bin/env python
# encoding: utf-8

import serialposix
from serialFrame import checkAck
from serialFrame import HexShow
import os,sys
from time import sleep
import struct
import multiprocessing
import getopt

global isStartCurrentsTest

colorRed = "\x1B[1;31;40m"
colorGreen = "\x1B[1;36;42m"
colorBlue = "\x1B[7;36;47m"
colorEnd = "\x1B[0m"

def sendLedsControlFrame(serialInstance, arg):
	writeStr = '\x5a\x08\x01\x09'
        if arg == '1':
		writeStr = writeStr + '\x00\x01'
        elif arg == '2':
		writeStr = writeStr + '\x00\x02'
        elif arg == '3':
		writeStr = writeStr + '\x00\x03'
        elif arg == '4':
		writeStr = writeStr + '\x00\x04'
        elif arg == '5':
		writeStr = writeStr + '\x00\x05'
        elif arg == '6':
		writeStr = writeStr + '\x00\x06'
        elif arg == '7':
		writeStr = writeStr + '\x00\x07'
        elif arg == '8':
		writeStr = writeStr + '\x00\x08'
        elif arg == '9':
		writeStr = writeStr + '\x00\x09'
        elif arg == '10':
		writeStr = writeStr + '\x00\x0A'
        elif arg == '11':
		writeStr = writeStr + '\x00\x0B'
        elif arg == '12':
		writeStr = writeStr + '\x00\x0C'
        elif arg == '13':
		writeStr = writeStr + '\x00\x0D'
        elif arg == '14':
		writeStr = writeStr + '\x00\x0E'
        elif arg == '15':
		writeStr = writeStr + '\x00\x0F'
	else:
		writeStr = writeStr + '\x00\x00'
		
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)
	#ack = serialInstance.read(13)
	#if checkAck(ack):
	#	print 'have sent leds control frame'
	#	return True
	#else:
	#	print 'read leds control frame error'

def rebootTarget(serialInstance, arg):
	if arg == '0':
		writeStr = '\x5a\x07\x05\x00\x00'
	elif arg == '1':
		writeStr = '\x5a\x07\x05\x00\x01'
	else:
		writeStr = '\x5a\x07\x05\x01\x01'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)

def resetMCU(serialInstance):
	writeStr = '\x5a\x05\xff'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)
	
def readBatSystemState(serialInstance, arg):
	writeStr = '\x5a\x06\x02'
	if arg == '0':
		writeStr = writeStr + '\x00'
	elif arg == '1':
		writeStr = writeStr + '\x01'
	elif arg == '2':
		writeStr = writeStr + '\x02'
	else:
		writeStr = writeStr + '\x00'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)

def readModulePowerState(serialInstance):
	writeStr = '\x5a\x06\x03\x01'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)

def readFaultBitState(serialInstance):
	writeStr = '\x5a\x06\x04\x01'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)

def readNewestFaultState(serialInstance):
	writeStr = '\x5a\x06\x0B\x00'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)

def readVersion(serialInstance, arg):
	if arg == '0':
		writeStr = '\x5a\x06\x0E\x00'
	elif arg == '1':
		writeStr = '\x5a\x06\x0E\x01'
	else:
		return
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)
	#ack = serialInstance.read(18)
	#if checkAck(ack):
	#	#print ack[5:-2]
	#	print 'firmware version: ' + ack[5:-2]
	#	return True
	#else:
	#	print 'read version frame error'

def startCurrentsTest(serialInstance, arg):
	writeStr = '\x5a\x08\x0A\x01\x01'
	if arg == '0':
		writeStr = writeStr + '\x00'
	if arg == '1':
		writeStr = writeStr + '\x01'
	if arg == '2':
		writeStr = writeStr + '\x02'
	if arg == '3':
		writeStr = writeStr + '\x03'
	if arg == '5':
		writeStr = writeStr + '\x05'
	else:
		print 'arg err'#writeStr = '\x5a\x08\x0A\x01\x01\x01'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	isStartCurrentsTest = 1 
	sleep(0.05)
	#ack = serialInstance.read(7)
	#if checkAck(ack):
	#	print 'started currents test'
	#	return True
	#else:
	#	print 'read currents test prepare frame error'

def readCurrentsData(serialInstance):
	curData = serialInstance.read(41)
	if checkAck(curData):
		if curData[1] == '\x29' and curData[2] == '\x0A':
			print 'currents data uploaded'
	else:
		print 'read currents data error'

def stopCurrentsTest(serialInstance):
	writeStr = '\x5a\x08\x0A\x01\x00\x02'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	isStartCurrentsTest = 0
	sleep(0.05)
	#ack = serialInstance.read(7)
	#if checkAck(ack):
	#	print 'currents test have stopped'
	#	return True
	#else:
	#	print 'read stop currents test frame error'
	
def serialDump(serialInstance, globalIsStartCurrentsTest):
	header = serialInstance.read(1)
	if header == '\x5A':
		length = serialInstance.read(1)
		contentLen = struct.unpack("B", length)[0] - 4
		#print 'contentLen is:%d' %contentLen
		content = serialInstance.read(contentLen)
		check = serialInstance.read(1)
		footer = serialInstance.read(1)
		if footer == '\xA5':	
			if checkAck(header + length + content + check + footer):
				if content[0] == '\x01':
					print colorRed + 'cmd 01 frame'+ colorEnd
				elif content[0] == '\x02':
					print 'cmd 02 frame'
					if content[1] == '\x00':
						print colorRed + 'battery voltage' + ': %d'%(struct.unpack('<H', bytes(content[4:6]))[0]) + colorEnd
					elif content[1] == '\x02':
						print colorRed + 'battery percentage' + ': %d'%(struct.unpack('<H', bytes(content[4:6]))[0]) + colorEnd
				elif content[0] == '\x03':
					print 'cmd 03 frame'
				elif content[0] == '\x04':
					print 'cmd 04 frame'
				elif content[0] == '\x05':
					print 'cmd 05 frame'
				elif content[0] == '\x0A':
					if content[1] == '\x01':
						if globalIsStartCurrentsTest == 1:
							print colorRed+'have started currents test'+colorEnd
						elif globalIsStartCurrentsTest == 0:
							print colorRed+'have stopped currents test'+colorEnd
						else:
						    print 'start or stop currents test'
						globalIsStartCurrentsTest = 3
					elif content[1] == '\x00':
						print 'currents data have uploaded'
					else:
						print 'not known cmd 0A frame'
				elif content[0] == '\x0B':
					print 'cmd 0B frame'
				elif content[0] == '\x0E':
					print colorBlue + 'firmware version: ' + content[4:] + colorEnd
				elif content[0] == '\x06':
					print 'cmd 06 frame'
				elif content[0] == '\x0F':
					print 'cmd 0F frame'
				elif content[0] == '\xFF':
					print 'cmd FF frame:reset MCU'
				else:
					print 'not known cmd'
			else:
				print 'rec check sum err'
		else:
			print 'frame footer err'
			#raise BadFrame
	#else:
	#	print 'not recieve anydata'
		
def serialDumpProcess(serialInstance, globalIsStartCurrentsTest):
	print 'have enter serial dump process'
	try:
		while True:
			serialDump(serialInstance, globalIsStartCurrentsTest)
		pass
	except KeyboardInterrupt, e:
		print 'exit serial dump process'	

if __name__ == "__main__":
	normal = 0
	leds_effect = 0
	read_type = 0
	print "footer name: ", sys.argv[0]

	t = serialposix.Serial('/dev/ttyUSB1',115200,timeout=0.5)

	if( t.is_open ):
		t.close()
	t.open()
	print t.portstr

	isStartCurrentsTest = 3
	process = multiprocessing.Process( target = serialDumpProcess, args = (t, isStartCurrentsTest))
	process.start()

	opts, args = getopt.getopt(sys.argv[1:],"v:r:n:hms:ft:epo")
	for op, value in opts:
		if op == "-v":
			readVersion(t, value)
		elif op == "-r":
			rebootTarget(t, value)
		elif op == "-n":
			normal = 2 
			leds_effect = value
			sendLedsControlFrame(t, leds_effect)
		elif op == "-h":
			print "help, exit"
		elif op == '-m':
			normal = 3
			readModulePowerState(t)
		elif op == "-s":
			normal = 1
			readBatSystemState(t, value)
			read_type = value
		elif op == "-f":
			normal = 4
			readFaultBitState(t)
		elif op == "-t":
			normal = 2
			startCurrentsTest(t, value)
		elif op == "-e":
			readNewestFaultState(t)
		elif op == "-p":
			normal = 1
			readBatSystemState(t, 2)
		elif op == "-o":
			resetMCU(t)
			
	#readVersion(t)
	#sendLedsControlFrame(t)
	#rebootTarget(t)
	#sleep(1000)	
	try:
		while normal:#True:			
			#readVersion(t)
			#sleep(0.5)
			if normal == 1:
				readBatSystemState(t, read_type)
				sleep(0.5)
			elif normal == 2:
				sendLedsControlFrame(t, '0')
				sleep(0.5)
			elif normal == 3:
				readModulePowerState(t)
				sleep(0.5)
			elif normal == 4:
				readFaultBitState(t)
				sleep(0.5)
		raise KeyboardInterrupt
	except KeyboardInterrupt, e:
		if normal == 2:
			stopCurrentsTest(t)
		print 'exit'

	process.join()
	t.close()
	print 'test stopped'
	sys.exit()	
