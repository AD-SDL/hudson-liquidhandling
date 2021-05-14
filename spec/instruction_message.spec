Instuction Message Specs
    
    - General Notes: 

        - instruction messages are sent from compute cell (lambda6) to work cell (hudson01) over port 5556
        - contains all files and data necessary to excecute the protocol on the work cell
        - Json format 
        - Files included in message: 
            - one .ahk file (AutoHotKey)
            - one .slvp file (SoftLinx)
            - one .txt file (Manifest file)
            - one or more .hso files (SoloSoft)

    - Structure: 

        <address>***<message_block> 

            address = name of instructions directory 
            message_block: 
                - all instruction details added to dictionary then sent in json.dumps(dictionary) format
                
                Basic structure: 
                {filename1 : 
                    {category1: [datails], 
                     category2: [details], 
                     ect..
                    }, 
                 filename2 : 
                    {category1: [datails], 
                     category2: [details], 
                     ect..
                    },
                } 

                Detailed Structure: 
                {<<instruction_filename>> : 
                    {"path": [<<full_instruction_file_path>>], 
                     "purpose": ["instructions"], 
                     "type": [<<file_extension>>], 
                     "ctime": [<<creation_timestamp>>, <<human_readable_creation_timestamp>>], 
                     "mtime": [<<modification_timestamp>>, <<human_readable_modification_timestamp>>], 
                     "data": [<<contents_of_instruction_file>>], 
                    }, 
                ...ect... 
                }

    
    - Example Instruction Message:  (shortened version of real message)

        Campaign1-col5-v1-1621004652***{
            "steps_1_2_3.hso": {
                "path": ["/lambda_stor/data/hudson/instructions/Campaign1-col5-v1-1621004652/steps_1_2_3.hso"], 
                "purpose": ["instructions"], 
                "type": ["hso"], 
                "ctime": ["1621004652.9254575", "2021-05-14 10:04:12.925457"], 
                "mtime": ["1621004652.9254575", "2021-05-14 10:04:12.925457"], 
                "data": [
                    "TipBox.180uL.Axygen-EVF-180-R-S.bluebox\n", 
                    "Empty\n", 
                    "DeepBlock.96.VWR-75870-792.sterile\n", 
                    "Plate.96.Corning-3635.ClearUVAssay\n", 
                    "DeepBlock.96.VWR-75870-792.sterile\n", 
                    "Plate.96.Corning-3635.ClearUVAssay\n", 
                    "Plate.96.Corning-3635.ClearUVAssay\n", 
                    "Empty\n", 
                    "GetTip\n", 
                    "Position1\n", 
                    "TipDisposal\n", 
                    "8\n", 
                    "1\n", 
                    "0\n", 
                    "False\n", 
                    "!@#$\n", 
                    "Aspirate\n", 
                    "Position3\n", 
                    "0\n", 
                    "2\n", 
                    "100\n", 
                    "1\n", 
                    "True\n", 
                    "False\n", 
                    "True\n", 
                    "False\n", 
                    "Position1\n", 
                    "0\n", 
                    "0\n", 
                    "0.5\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "\n", 
                    "1\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "a\n", "
                    0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "0\n", 
                    "0\n", 
                    "5\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "!@#$\n", 
                    "Dispense\n", 
                    "Position4\n", 
                    "0\n", 
                    "2\n", 
                    "100\n", 
                    "0\n", 
                    "True\n", 
                    "False\n", 
                    "True\n", 
                    "False\n", 
                    "Position1\n", 
                    "0\n", 
                    "0\n", 
                    "2\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "\n", 
                    "1\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "a\n", 
                    "0\n", 
                    "0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "60,0,0,0,0,0,0,0,0,0,0,0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "0\n", 
                    "!@#$\n", 
                    "ShuckTip\n", 
                    "TipDisposal\n", 
                    "!@#$\n"
                ]
            },
            "steps_1_2_3.slvp": {
                "path": ["/lambda_stor/data/hudson/instructions/Campaign1-col5-v1-1621004652/steps_1_2_3.slvp"], 
                "purpose": ["instructions"], 
                "type": ["slvp"], 
                "ctime": ["1621004652.9374576", "2021-05-14 10:04:12.937458"], 
                "mtime": ["1621004652.9374576", "2021-05-14 10:04:12.937458"], 
                "data": [
                    ... contents of file ... 
                ]
            }, 
            "steps_1_2_3.ahk": {
                "path": ["/lambda_stor/data/hudson/instructions/Campaign1-col5-v1-1621004652/steps_1_2_3.ahk"], 
                "purpose": ["instructions"], 
                "type": ["ahk"], 
                "ctime": ["1621004652.9374576", "2021-05-14 10:04:12.937458"], 
                "mtime": ["1621004652.9374576", "2021-05-14 10:04:12.937458"], 
                "data": [
                    "#SingleInstance, Force\n", 
                    "SendMode Input\n", 
                    "SetWorkingDir, 
                    %A_ScriptDir%\n", 
                    "\n", 
                    "Run, \"C:\\Program Files (x86)\\Hudson Robotics\\SoftLinx V\\SoftLinxVProtocolEditor.exe\" %A_ScriptDir%\\steps_1_2_3.slvp\n", 
                    "WinActivate, SoftLinx V\n", 
                    "Sleep, 5000\n", 
                    "MouseClick, Left, 300, 45\n", 
                    "Sleep, 1000\n", 
                    "if WinActive(\"Not Saved\") {\n",
                    "\tSend, {Tab}{Enter}\n", 
                    "\tSleep, 5000\n", "}\n", 
                    "if WinActive(\"Start Now?\") {\n", 
                    "\tSend, {Enter}\n", "\tSleep, 5000\n", 
                    "}\n"
                ]
            }, 
            "steps_1_2_3.txt": {
                "path": ["/lambda_stor/data/hudson/instructions/Campaign1-col5-v1-1621004652/steps_1_2_3.txt"], 
                "purpose": ["instructions"], 
                "type": ["txt"], 
                "ctime": ["1621004652.9414575", "2021-05-14 10:04:12.941458"], 
                "mtime": ["1621004652.9414575", "2021-05-14 10:04:12.941458"], 
                "data": ["1621004652.9438274\n", "2021-05-14 10:04:12.943842\n", 
                "steps_1_2_3.hso\n", 
                "steps_1_2_3.slvp\n", 
                "steps_1_2_3.ahk"
            ]
        }
    }
                    
                    
                     
                    
                    
                    
                
    



                







    

