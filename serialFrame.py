#! /usr/bin/env python
# encoding: utf-8

import serialposix

t = serialposix.Serial('/dev/tty.wchusbserial1410',115200)

if( t.is_open ):
	t.close()

t.open()

print t.portstr

def hexShow(argv):
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x'%hvol
        result += hhex + ' '
    print 'write Hex:',result

firmware = open('hello.bin','rb')

try:
	while True:

		strRead = firmware.read(5)

		if not strRead:
			break;
		#hexShow(strInput)

		n = t.write('\x5A'+strRead+'\xA5')

		str = t.read(n)

		print str

finally:
	firmware.close()

t.close()
#platformSetting = serialposix.PlatformSpecific()

#platformSetting._set_special_baudrate(115200)