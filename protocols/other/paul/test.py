from liquidhandling import SoftLinx

plate_id = 1
shaker_speed  = 30 
incubation_time = [0,1,0,0]
hidex_protocol = "TEST"


softLinx = SoftLinx("Paul Part 1", "C:\\Users\\svcaibio\\Desktop\\PAUL\\RepeatedODReadings\\part1.slvp")
# initialize plates 
softLinx.setPlates({
    "SoftLinx.Liconic.Nest": "Plate.96.Corning-3635.ClearUVAssay",
}) 
# take first 5 readings
for i in range(5):  
    # Incubate the plate
    softLinx.liconicLoadIncubator(loadID=plate_id)
    softLinx.liconicShake(shaker1Speed=shaker_speed, shakeTime=incubation_time)
    softLinx.liconicUnloadIncubator(loadID=plate_id)

    # move plate to hidex and take reading
    softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"], ["Softinx.Hidex.Nest"])
    softLinx.plateCraneMoveCrane(["SoftLinx.PlateCrane.Safe"])
    softLinx.hidexRun(hidex_protocol)

    # move plate back to Liconic Nest 
    softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
    softLinx.plateCraneMoveCrane(["SoftLinx.PlateCrane.Safe"])
softLinx.saveProtocol()

softLinx = SoftLinx("Paul Part 2", "C:\\Users\\svcaibio\\Desktop\\PAUL\\RepeatedODReadings\\part2.slvp")
softLinx.saveProtocol()