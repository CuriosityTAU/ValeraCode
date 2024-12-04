import os   
import time

def get_sink():
    cmd = 'pactl list short sinks'
    process = os.popen(cmd)
    output = process.read()
    process.close()
    
    # print(output)
    result = output.split('\n')
    list_audio = {}
    the_sink = None
    for r in result:
        audio_info = r.split('\t')
        try:
            list_audio[audio_info[0]] = audio_info[1]
            if 'usb' in audio_info[1]:
                the_sink = audio_info
        except:
            pass
    print(list_audio)
    print(the_sink)
    return the_sink, list_audio

def initialize():
    the_sink, list_audio = get_sink()
    sink_name = the_sink[1]
    cmd_list = ['pactl suspend-sink %s 1' % k for k, v in list_audio.items()]
    cmd_list = ['pactl suspend-sink %s 0' % the_sink[0]]
    cmd_list.append('pactl set-default-sink ' + sink_name)
    cmd_list.append('pactl set-sink-volume ' + sink_name + ' 100%')
    
    for cmd in cmd_list:
        print(cmd)
        process = os.popen(cmd)
        output = process.read()
        process.close()

def beep(freq=440):
    cmd_list = ['play -n synth 0.2 sine %d' % freq]
    
    for cmd in cmd_list:
        print(cmd)
        process = os.popen(cmd)
        output = process.read()
        process.close()


print("Initializing system ...")
initialize()
time.sleep(1)
beep(440)
