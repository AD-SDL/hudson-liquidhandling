from liquidhandling import SoftLinx

plate_num = 5
exp_name = "DATA_FORMAT_EXP_NAME"
data_format = "dna_assembly"

softLinx = SoftLinx("TestStackMulti", "C:\\Users\\svcaibio\\Desktop\\Debug\\DATA_FORMAT_TEST.slvp")

# transfer data to lambda6
softLinx.runProgram("C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{plate_num} {exp_name} {data_format}")

softLinx.saveProtocol()

