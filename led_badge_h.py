INPUT = False
OUTPUT = True
HIGH = True
LOW = False

PIN_RED = 3
PIN_GREEN = 1
PIN_BLUE = 0
PIN_ANODE = 2
PIN_NOTHING = 5

current_color = (False, False, False)
counter = 0
counter_max = 1000
just_booted = True
current_best_lq = 127
current_best_node = None
last_best_lq = 127
show_off = False
threshhold_lq = 21
is_friendly = False

@setHook(HOOK_STARTUP)
def init():
    #anode
    setPinDir(PIN_ANODE, OUTPUT)
    writePin(PIN_ANODE, HIGH)

    #r, g, b
    setPinDir(PIN_RED, OUTPUT)
    writePin(PIN_RED, HIGH)
    setPinDir(PIN_GREEN, OUTPUT)
    writePin(PIN_GREEN, HIGH)
    setPinDir(PIN_BLUE, OUTPUT)
    writePin(PIN_BLUE, HIGH)

    write_color(True, False, False)
    
    if loadNvParam(31) != 45:
        saveNvParam(31, 45) #Routes worse than 45 are penalized
    #if loadNvParam(11) != 15:
    #    saveNvParam(11, 15) #Turn off power amp
    if loadNvParam(11) != 31:
        saveNvParam(11, 31) #Turn ON power amp
    #txPwr(1) #out of 17... seriously
    set_friendly(False)

    write_color(False, False, False)

@setHook(HOOK_10MS)
def strobe():
    global counter

    if counter > counter_max:
        counter = 0 #trip!
    else:
        counter += 1

    if counter <= 8: #Tweak this to increase/decrease length of pulse
        set_state(True)
    else:
        set_state(False)

@setHook(HOOK_100MS)
def do_show_off():
    global show_off, counter_max
    if show_off:
        #Just do a visual effect - blink reallyfast, and slow down.
        counter_max += 2
        if counter_max > 150:
            show_off = False

@setHook(HOOK_1S)
def scan():
    global just_booted, current_best_lq, last_best_lq, counter_max, current_best_node, show_off, is_friendly

    if just_booted:
        set_random_color()
        show_off = True
        just_booted = False

    if not is_friendly:
        return

    if show_off:
        #We are showing off, just clear out our link quality.
        current_best_lq = 127
    else:
        #We're not showing off, so just set the blink rate based on link quality.
        if current_best_lq < 45:
            counter_max = ( current_best_lq - 19 ) * 10 #Minimum of 10ms between blinks.
        else:
            counter_max = 300 #This *10 is how many ms between blinks when there is no one nearby.
    
        #Send my color to the other guy, if we've been consistently close for two cycles.
        if current_best_lq < threshhold_lq and last_best_lq < threshhold_lq: #We have to beat this LQ to transmit
            rpc(current_best_node, "receive_color", current_red, current_green, current_blue)
            receive_color(current_red, current_green, current_blue)

    last_best_lq = current_best_lq
    current_best_lq = 127

    mcastRpc(1, 1, "receive")

def receive():
    global current_best_lq, current_best_node
    lq = getLq()
    if lq < current_best_lq:
        current_best_lq = lq
        current_best_node = rpcSourceAddr()

def receive_color(r, g, b):
    global counter_max, show_off
    set_color(r, g, b)
    counter_max = 5 #Increase this to decrease the amount of time it's solid after a transmit
    show_off = True
    
def set_threshhold_lq(x):
    global threshhold_lq
    threshhold_lq = x

def set_friendly(x):
    global is_friendly, counter_max, counter
    is_friendly = not not x
    if is_friendly:
        txPwr(1)
    else:
        txPwr(17)
    counter_max = 200 #reset this to some sane value
    counter = 0 #change it right now


#LED Cube support
def report(color):
    global current_red, current_green, current_blue, counter

    new_r, new_g, new_b = False, False, False

    if is_friendly:
        return #Don't take cube shit if we are being friendly.

    if color == "orange":
        new_r, new_g, new_b = True, True, False
    elif color == "yellow":
        new_r, new_g, new_b = True, True, True
    elif color == "red":
        new_r, new_g, new_b = True, False, False
    elif color == "purple":
        new_r, new_g, new_b = True, False, True
    elif color == "blue":
        new_r, new_g, new_b = False, False, True
    elif color == "green":
        new_r, new_g, new_b = False, True, False

    if current_red == new_r and current_green == new_g and current_blue == new_b:
        if show_off == False:
            counter = 0 #just make it blink right now to show that we heard it.
    else:
        receive_color(new_r, new_g, new_b)


def set_color(r, g, b):
    global current_red, current_green, current_blue
    current_red, current_green, current_blue = r, g, b

def write_color(red, green, blue):
    writePin(PIN_RED, not red)
    writePin(PIN_GREEN, not green)
    writePin(PIN_BLUE, not blue)
def write_current_color():
    write_color(current_red, current_green, current_blue)

def set_state(state):
    if state:
        write_current_color()
    else:
        write_color(False, False, False)

def set_random_color():
    thing = getMs() + random()
    red = 1 & thing
    green = 2 & thing
    blue = 4 & thing
    if not red and not green and not blue: #this shouldn't result in an off LED
        return set_random_color()
    if red == current_red and green == current_green and blue == current_blue: #dont pick the same color
        return set_random_color()
    set_color(red, green, blue)
    #set_state(True)
    return thing

