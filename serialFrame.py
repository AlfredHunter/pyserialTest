#!/usr/bin/env python
# encoding: utf-8

import serialposix
import hashlib
import os,sys
from time import sleep

filename = 'PowerBoard.bin'

def HexShow(argv):
        result = ''
        hLen = len(argv)
        for i in xrange(hLen):
            hvol = ord(argv[i])
            hhex = '%02x'%hvol
            result += hhex + ' '
        print 'Hex:',result
        return result[0:-1]

def md5hex(word):
    """ MD5加密算法，返回32位小写16进制符号
    """
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()

def md5sum(fname):
    """ 计算文件的MD5值
    """
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else: #最后要将游标放回文件开头
            fh.seek(0)
    m = hashlib.md5()
    if isinstance(fname, basestring) \
            and os.path.exists(fname):
        with open(fname, "rb") as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    #上传的文件缓存 或 已打开的文件流
    elif fname.__class__.__name__ in ["StringIO", "StringO"] \
            or isinstance(fname, file):
        for chunk in read_chunks(fname):
            m.update(chunk)
    else:
        return ""
    return m.hexdigest()

def checkAck(ackBytes):
	if not len(ackBytes):
		print 'mcu not ack'
		return False
	showstr = HexShow(ackBytes)
	splitStr = showstr.split(' ')
	print splitStr
	if splitStr[0] == '5a' and splitStr[-1] == 'a5':
		if len(splitStr) != int(splitStr[1],16):
			print 'ack length check error'
			return False
	else:
		print 'ack header or footer error'
		return False
	checksum = 0
	for num in splitStr[0:-2]:
		checksum = checksum + int(num, 16)
	checksumStr = '' + hex(checksum)
	#print 'checksunStr:' + checksumStr[-2:]
	if checksumStr[-2:] != splitStr[-2]:
		print 'ack checksum Error'
		return False		
	return True
		

def prepareUpgrade(serialInstance):
    firmwareSize = '%08x'%os.path.getsize(filename)
    firmwareMd5 = md5sum(filename)
    print 'firmwareMd5:'+ firmwareMd5
    print 'firmSize:' + firmwareSize

    writeStr = '\x5a\x1a\x0F\x00'+firmwareMd5.decode('hex')+firmwareSize.decode('hex')    
    showstr = HexShow(writeStr)
    #print showstr.split(' ')
    checksum = 0
    for num in showstr.split(' '):
    	#print num
    	#print int(num,16)
    	checksum = checksum + int(num,16)
    checksumStr = ''+ hex(checksum)
    #print hex(checksum)
    print 'checksunStr:' + checksumStr[-2:]
    writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
    #print hex(checksum).decode('hex')
    #showstr = HexShow(writeStr)
    #print 'write str:'+ writeStr
    n = serialInstance.write(writeStr) 
    ack = 0
    timeout_count = 0
    while not ack and timeout_count < 10:
    	ack = serialInstance.read(7)
    	sleep(0.5)
	timeout_count = timeout_count + 1
    if checkAck(ack):
    	if ack[3] == '\x00':
    		if ack[4] == '\x00':
    			print 'mcu prepared to upgrade'
    			return True
    		elif ack[4] == '\x01':
    			print 'mcu storage not enough'
    			return False
    		elif ack[4] == '\x02':
    			print 'mcu is busy, please retry later'
    			return False
    		else:
    			print 'not known ack cmd'
    			return False
    	else:
    		print 'not ack prepare cmd'
    		return False
    else:
    	print 'ack bytes check error'
    	return False


def SendFirmware(serialInstance):
	#retryCount = 0
	def sendPackage(writeBytes):
		n = serialInstance.write(writeBytes)
		sleep(0.1)
		ack = serialInstance.read(7)
		if checkAck(ack):
			return True
		else:
			#code = raw_input('ack err,go on?(Y/N)')
			#if code == 'N' or code == 'n':
			#	sys.exit()
			sendPackage(writeBytes)
			print 'check ack error,and retry '#%d'%retryCount
			#if retryCount >= 5:
				#print 'retry too much time'
				#return False

	firmware = open(filename,'rb')
	count = 0
	try:
		while True:
			
			strRead = firmware.read(240)
			writeLen = len(strRead) + 6
			if not strRead:
				break
			count = count + 1
			print 'send no.%d,write data length = %d(Bytes)'%(count,writeLen-6)
			writeStr = '\x5a' + ('%02x'%writeLen).decode('hex')+'\x0F\x01'+strRead
			showstr = HexShow(writeStr)
			checksum = 0
			for num in showstr.split(' '):
				checksum = checksum + int(num,16)
			checksumStr = ''+ hex(checksum)
			#print 'checksum = %d'%checksum
			print 'checksum = ' + checksumStr[-2:]
			writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
			
			#retryCount = 0
			if not sendPackage(writeStr):
				print 'mcu not response'
			#n = serialInstance.write(writeStr)
			#sleep(0.01)
			#ack = serialInstance.read(255)
			#if checkAck(ack):
			#	print 'check ack ok'
			#else:
			#	while True:
			#		n = serialInstance.write(writeStr)
			#		sleep(0.5)
			#		ack = serialInstance.read(255)
			#		pass
			#	print 'check ack error'
			#	break
			
	finally:
		firmware.close()

def upgradeFinishCheck(serialInstance):
	writeStr = '\x5a\x07\x0F\x02\x00'
	showstr = HexShow(writeStr)
	#print showstr.split(' ')
	checksum = 0
	for num in showstr.split(' '):
		#print num
		#print int(num,16)
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
    #print hex(checksum)
    #print 'checksunStr:' + checksumStr[-2:]
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(2)
	ack = serialInstance.read(7)
	if checkAck(ack):
		if ack[4] == '\x00':
			print 'upgrade succuss'
			return True
		else:
			print 'upgrade faild: check not ok'
			return False
	else:
		print 'check ack error'
		return False

def readVersion(serialInstance):
	writeStr = '\x5a\x06\x0E\x00'
	showstr = HexShow(writeStr)
	checksum = 0
	for num in showstr.split(' '):
		checksum = checksum + int(num,16)
	checksumStr = ''+ hex(checksum)
	writeStr = writeStr + checksumStr[-2:].decode('hex') + '\xa5'
	n = serialInstance.write(writeStr)
	sleep(0.5)
	ack = serialInstance.read(19)
	if checkAck(ack):
			print 'firmware version: ' + ack[6:-2]
			return True
	else:
		print 'read version frame error'
		return False

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
	ack = serialInstance.read(5)
	if checkAck(ack):
			print 'have reset MCU'
			return True
	else:
		return False
	 
if __name__ == "__main__":
	testUpdateTime = 100
	t = serialposix.Serial('/dev/ttyUSB1',115200,timeout=0.5)

	if( t.is_open ):
		t.close()

	t.open()
	print t.portstr

	readVersion(t)
	sleep(0.5)
	readVersion(t)
#	sleep(0.5)
#	if readVersion(t):
#		if prepareUpgrade(t):
#			SendFirmware(t)
#			print 'firmware have sent finished, start to check md5'
#			upgradeFinishCheck(t)
#	else:
#		print 'may disconnect'
	haveTestTimes = 0
	while testUpdateTime:
		if readVersion(t):
			if prepareUpgrade(t):
				SendFirmware(t)
				print 'firmware have sent finished, start to check md5'
				if upgradeFinishCheck(t):
					if resetMCU(t):
						testUpdateTime = testUpdateTime - 1 
						haveTestTimes = haveTestTimes + 1 
						print 'have update %d times'%haveTestTimes
		else:
			print 'may disconnect'
		sleep(3)

	t.close()
	print 'program over'

	
