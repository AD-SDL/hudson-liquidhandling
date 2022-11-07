from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import *

softLinx = SoftLinx("TorreyPinesRIC20 Test", "C:\\Users\\svcaibio\\Desktop\\Debug\\torreyPinesTest.slvp")

softLinx.torreyPinesSetTemperature(temperature=37)

softLinx.saveProtocol()