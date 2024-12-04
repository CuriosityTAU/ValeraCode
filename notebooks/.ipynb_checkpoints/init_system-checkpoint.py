import os
import time

def get_sink():
    cmd = 'pactl list short sinks'
    process = os.popen(cmd)
    output = process.read()
    process.close()
    
    # print(output)
    result = output.split('\n')
    print("list of audio:")
    for r in result:
        print(r)
    
    for i in range(len(result)):
        sink_info = result[-(i+1)].split('\t')
        try:
            if 'usb' in sink_info[1]:
                sink_name = sink_info[1]
                break
        except:
            pass
    print('Selected sink:')
    print(sink_name)
    return sink_name

def initialize():
    sink_name = get_sink()
    
    cmd_list = [
        ('pactl set-default-sink ' + sink_name, -1),
        ('pactl set-sink-volume ' + sink_name + ' 20%', 2), 
        ('play -n synth 0.2 sine 440', 5)
    ]
    
    for cmd in cmd_list:
        print(cmd[0])
        process = os.popen(cmd[0])
        output = process.read()
        process.close()

print("Initializing system ...")
initialize()