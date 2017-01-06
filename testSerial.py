#!/usr/bin/env python
# encoding: utf-8

import serialposix
import os,sys
from time import sleep

def serialTest(serialInstance):
	while(True):
		writeStr = raw_input('input string:')
		n = serialInstance.write(writeStr)
		sleep(1)
		ack = serialInstance.read(10)
		print 'ack is:%s'%ack


if __name__ == "__main__":

	t = serialposix.Serial('/dev/ttyUSB0',115200,timeout=0.5)

	if( t.is_open ):
		t.close()

	t.open()

	print t.portstr

	#serialTest(t)
	t.close()


