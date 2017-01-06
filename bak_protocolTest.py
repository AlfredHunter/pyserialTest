#!/usr/bin/env python
# encoding: utf-8

import serialposix
from serialFrame import checkAck
from serialFrame import HexShow
import os,sys
from time import sleep
import struct
import multiprocessing

global isStartCurrentsTest

colorRed = "\x1B[1;31;40m"
colorGreen = "\x1B[1;36;42m"
colorBlue = "\x1B[7;36;47m"
colorEnd = "\x1B[0m"

def sendLedsControlFrame(serialInstance):
	writeStr = '\x5a\x08\x01\x09\x00\x03'
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

def rebootTarget(serialInstance):
	writeStr = '\x5a\x06\x03\x01'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.05)
	
def readVersion(serialInstance):
	writeStr = '\x5a\x06\x0E\x00'
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

def startCurrentsTest(serialInstance):
	writeStr = '\x5a\x08\x0A\x01\x01\x06'
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
				elif content[0] == '\x03':
					print 'cmd 03 frame'
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
				elif content[0] == '\x0E':
					print colorBlue + 'firmware version: ' + content[3:] + colorEnd
				elif content[0] == '\x06':
					print 'cmd 06 frame'
				elif contetn[0] == '\x0F':
					print 'cmd 0F frame'
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

	t = serialposix.Serial('/dev/ttyUSB0',115200,timeout=0.5)

	if( t.is_open ):
		t.close()
	t.open()
	print t.portstr

	isStartCurrentsTest = 3
	process = multiprocessing.Process( target = serialDumpProcess, args = (t, isStartCurrentsTest))
	process.start()

	readVersion(t)
	#sendLedsControlFrame(t)
	#startCurrentsTest(t)
	#rebootTarget(t)
	#sleep(1000)	
	try:
		while True:			
			#readVersion(t)
			#sleep(0.05)
			sendLedsControlFrame(t)
			sleep(0.1)
	except KeyboardInterrupt, e:
		stopCurrentsTest(t)
		print 'exit'

	t.close()
	print 'test stopped'
	
