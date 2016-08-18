#! /usr/bin/env python
# encoding: utf-8

import serialposix
import hashlib
import os
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

    writeStr = '\x5a\x1b\x0F\x00'+firmwareMd5.decode('hex')+firmwareSize.decode('hex')+'\x00'    
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
    sleep(2)
    ack = serialInstance.read(8)
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
		sleep(0.01)
		ack = serialInstance.read(8)
		if checkAck(ack):
				return True
		else:
			sendPackage(writeBytes)
			#retryCount = retryCount + 1
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
			print 'send no.%d'%count
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
			#sleep(0.5)
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
	ack = serialInstance.read(8)
	if checkAck(ack):
		if ack[4] == '\x00':
			print 'upgrade succuss'
		else:
			print 'upgrade faild: check not ok'
	else:
		print 'check ack error'

if __name__ == "__main__":

	t = serialposix.Serial('/dev/ttyUSB0',115200,timeout=0.5)

	if( t.is_open ):
		t.close()

	t.open()

	print t.portstr

	if prepareUpgrade(t):
		confirmCODE = raw_input('confirm to update?Y/N:')
		if confirmCODE == 'Y' or confirmCODE == 'y':
			SendFirmware(t)
			upgradeFinishCheck(t)
		elif confirmCODE == 'N' or confirmCODE == 'n':
			print 'not to update'
		
	t.close()
	print 'program over'

	
