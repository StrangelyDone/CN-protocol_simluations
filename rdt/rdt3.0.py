import random
from threading import Timer
import time

class Packet:
    #so basically the packet would be made of the sequence num, payload data and checksum..!
    #the sequence_num => binary integer(1-bit) and the data, checksum are binary strings..!
    def __init__(self, seq_num, data, checksum):
        self.seq_num = seq_num
        self.data = data
        self.checksum = checksum

class ACK_packet(Packet):
    def __init__(self, seq_num, checksum):
        super().__init__(seq_num, "", checksum)
        self.ACK = 1

class channel:
    prob = 0.4
    loss_prob = 0.3 
    delay_range = (0.1, 1.3)  

    #returns the corrupted binary string..!
    @staticmethod
    def flip_random_bit(binary_str):
        if len(binary_str) == 0:
            return binary_str
        
        #randomly choose an index..!
        index = random.randint(0, len(binary_str) - 1)

        #flip the bit at that index
        if binary_str[index] == '0':
            flipped = '1'  
        else:
            flipped = '0'

        return binary_str[:index] + flipped + binary_str[index+1:]

    @staticmethod
    def corrupt_packet(packet, error_prob = prob):
        #corrupt the packet, prob% of the time lol
        if random.random() < error_prob:
            field_to_corrupt = random.choice(["seq_num", "checksum", "data"])
            
            if field_to_corrupt == "seq_num":
                #flip 0 to 1 or 1 to 0
                packet.seq_num = 1 - packet.seq_num
            else:
                #flip one random bit in that binary string (data or checksum)
                if(field_to_corrupt == "checksum"):
                    packet.checksum = channel.flip_random_bit(packet.checksum)
                else:
                    packet.data = channel.flip_random_bit(packet.data)
        
        return packet
    
    @staticmethod
    def flip_bit(b):
        return '1' if b == '0' else '0'
    
    @staticmethod
    def corrupt_ack_packet(packet, probability = prob):
        if random.random() >= probability:
            return packet

        #choose a random field to corrupt..!
        field = random.choice(["seq_num", "checksum"])

        if field == "seq_num":
            packet.seq_num = 1 - packet.seq_num
        else:
            packet.checksum = channel.flip_random_bit(packet.checksum)

        return packet

    
    @staticmethod
    def udt_send(packet, type = "packet"):
        if random.random() < channel.loss_prob:
            print(f"[channel]  {type} lost!")
            #lost packet => none..!
            return None
        
        #introduce the random delay.. * -> unpack the touple..!
        delay = random.uniform(*channel.delay_range)
        print(f"[channel]  {type} delayed by {round(delay, 2)}s")

        #introduce the corruption in packet..!
        try:
            if hasattr(packet, "ACK"):
                packet =  channel.corrupt_ack_packet(packet)
        except Exception:
            packet = channel.corrupt_packet(packet)

        #the delay..!
        time.sleep(delay)

        #return the packet..!
        return packet
    
class endsystem:
    def __init__(self, type):
        self.type = type

    def log(self):
        if(self.type == "sender"):
            print(f"[sender]   {self.state}")
        else:
            print(f"[receiver] {self.state}")

class Sender(endsystem):
    def __init__(self, state = "waiting for call 0 from above"):
        super().__init__("sender")
        self.state = state
        self.data = ""
        self.timer = None
        self.time_out_interval = 2.0
        self.packet = None

        #needed..?
        self.waiting_for_ACK = False

    #data in binary form..!
    def make_pkt(self):
        #calculate the check sum for the data..! 
        checksum = calc_checksum(self.data)
        if("0" in self.state):
            #create the packet
            packet = Packet(0, self.data, checksum)
        else:
            #create the packet lol
            packet = Packet(1, self.data, checksum)

        return packet
    
    #send the ack packet here..!
    def verify_ACK_packet(self, packet):
        #stop the timer once you get the ACK packet..!
        self.stop_timer()

        #handle the case where the ACK is lost..!
        if(packet is None):
            return "retransmit..!"

        #check if the ack is corrupt..!
        data = format(1, '08b') + format(packet.seq_num, '08b')
        checksum = calc_checksum(data)

        #if corrupt.. retransmit..!
        if(checksum != packet.checksum):
            return "retransmit..!"

        #check if its the correct seq_num ..!
        if("0" in self.state and packet.seq_num == 0):
            self.state = "waiting for call 1 from above"
            return ""
        
        if("1" in self.state and packet.seq_num == 1):
            self.state = "waiting for call 0 from above"
            return ""
        
        return "retransmit..!"
    
    def start_timer(self):
        #check if theres a timer already active.. (for safety)
        if self.timer:
            self.timer.cancel()

        #initialize the timer and set the trigger function to the handler..!
        self.timer = Timer(self.time_out_interval, self.timeout_handler)
        self.timer.start()
        self.time_out = False

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
            self.time_out = False

    def timeout_handler(self):
        print("[sender]   Timeout, Retransmitting...!")
        self.time_out = True

        #anything else needed..??

    def send_packet(self, packet):
        self.packet = packet
        #send the packet through channel
        print(f"[sender]   Sending packet with seq {packet.seq_num}")
        ############################################################################################################3
        #make a loss channel and send the packet here and return the sent packet
        #might be packet or none...! something like this..!

        #start the timer before hand cuz the function returns stuff after delay
        #and we can't have our timer starting after that delay..!
        self.start_timer()

        #change state accordingly...!
        if('0' in self.state):
            self.state = "waiting for ACK 0"
        else:
            self.state = "waiting for ACK 1"

        #send the packet through the channel..!!
        packet = channel.udt_send(self.packet)

        self.waiting_for_ack = True

        #might be none or an actual packet..!
        return packet

class Receiver(endsystem):
    last_received_ack = 1

    def __init__(self, state = "waiting for call 0 from below"):
        super().__init__("receiver")
        self.state = state
        self.packet = None

    #just receive the packet..!
    def rcv_pkt(self, packet):
        self.packet = packet


    def verify_packet_and_give_ACK_packet(self):
        #check if the self.packet is an actual packet..!
        if(self.packet is None):
            #packet loss so send ACK for previous state..!(last_received_ACK..!)
            #also no state change here.. cuz its not a trigger..!
            return self.make_pkt(self.last_received_ack)

        #waiting for packet with seq num 0 
        if("0" in self.state and self.packet.seq_num != 0):
                #no state change
                return self.make_pkt(1)
        #waiting for packet with seq num 1
        if("1" in self.state and self.packet.seq_num != 1):
                #no state change
                return self.make_pkt(0)
        
        #now verify if the packet is corrupt..!
        ck_sum = calc_checksum(self.packet.data)
        if(ck_sum == self.packet.checksum):
            #change state accordingly
            if("0" in self.state):
                self.state = "waiting for call 1 from below"
            else:
                self.state = "waiting for call 0 from below"

            self.last_received_ack = self.packet.seq_num
            return self.make_pkt(self.packet.seq_num)
        else:
            #no state change (send ack for previous packet..!)
            return self.make_pkt(1 - self.last_received_ack)
        
    def make_pkt(self, seq_num):
        #ACK, here would just be an integer(and always equals to 1)..!
        #calculate checksum with that in mind..!
        data = format(1, '08b') + format(seq_num, '08b')
        checksum = calc_checksum(data)

        packet = ACK_packet(seq_num, checksum)

        return packet

#function to calculate check sum for the data..!
def calc_checksum(binary_data):
    #the data we have is a binary string already, so just check if we need to do any additional padding...!
    if len(binary_data) % 16 != 0:
        binary_data += '0' * (16 - (len(binary_data) % 16))

    #just like the internet checksum.. add the 16-bit chunks..!
    checksum = 0
    for i in range(0, len(binary_data), 16):
        chunk = binary_data[i:i+16]
        chunk_value = int(chunk, 2)
        checksum += chunk_value

        #handle carry(the wrap-around thingy..!)
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    #final wraparound (in case another carry was added)
    checksum = (checksum & 0xFFFF) + (checksum >> 16)

    #the ones complement
    checksum = ~checksum & 0xFFFF

    return format(checksum, '016b')


#function to convert english-text to binary string..! (where data is just a string..!)
#the resulting binary string has 8 time the initial length.. also theres no space between words..!
#example: the string "hi hello" would become.. "0110100001101001001000000110100001100101011011000110110001101111"..1
def eng_to_bin(data):
    return ''.join(format(ord(c), '08b') for c in data)


#triggers the state change in the sender..! (data is already in binary form..!)
def rdt_send(sender, data):
    #let the sender make the packet..!
    sender.data = data
    packet = sender.make_pkt()

    #send it throught the unreliable data channel..!
    packet = channel.corrupt_packet(packet)

    #decide the state of the sender..!
    if("0" in sender.state):
        st = "waiting for ACK 0"
    else:
        st = "waiting for ACK 1"

    #return the packet so that the receiver can have it..!
    return packet, st



def main(data_list):
    sender = Sender()
    receiver = Receiver()
    transmission_count = 0

    i = 0
    while i < len(data_list):
        if(i == 0):
            sender.log()
            receiver.log()

        #sender sends a packet
        data = eng_to_bin(data_list[i])
        print(f"[sender]   called from above, sending packet")

        sender.data = data
        packet = sender.make_pkt()

        #variable to keep track if we need to retransmit..!
        retransmit = False

        ###############################################################
        #replace this part with the sender.send() function..!
        #the send_packet has the required delay and all the channel stuff in it..!
        #but may be we shouldn't let the sender.state depend on
        #the time out delay and all.. change that part in the sender.send_packet() itself..!
        #i think this is bad design.. ig we shouldn't assign the packet manually..
        #have something like receiver.receiver_pkt() or something like that..!
        #so that whenever the sender.send_packet() is triggered (either here
        #or from the timer timeout..)..!
        packet = sender.send_packet(packet)

        #dont need to print this when we actually know that the packet is lost and no packet is delivered..!
        #and basically dont deliver the lost packet..!
        if(packet is not None):
            receiver.rcv_pkt(packet)
            print(f"[receiver] called from below, received packet")

        #since we can't really kill threads in python.. we will repeatedly check if the timer has gone off..!
        #timer check..!
        if(sender.time_out):
            retransmit = True

        #generating ACK packet for the received packet..!
        #check if its an actual packet or none then if its corrupt or not..!
        #and change the state accordingly with this check..!

        #obviously.. we dont need to do this if the timer has run out..!
        #also we dont need to verify anything if the packet is lost..! (from sender to the receiver..!)
        if(not retransmit and (packet is not None)):
            ack_packet = receiver.verify_packet_and_give_ACK_packet()

        #timer check..!
        if(sender.time_out):
            retransmit = True

        #now send the ack_packet into the unreliable channel..!
        #add a send_pkt function to the receiver also to send the ack packets..?

        #obviously.. we dont need to do this if the timer has run out..!
        #and when the actual packet corresponding to the ACK is lost..!
        if(not retransmit and (packet is not None)):
            print("[receiver] ACK sent")
            corrupted_ack = channel.udt_send(ack_packet, type = "ACK")
            
        else:
            #default it to none when the actual packet corresponding to it is lost..!
            corrupted_ack = None

        #timer check..!
        if(sender.time_out):
            retransmit = True

        #oke now the timer might have triggered and if it has triggered..! then
        #i would want to break the next part of execution.. how do i do it..?


        # sender.log()
        # receiver.log()

        # #timer check..!
        # if(sender.time_out):
        #     retransmit = True

        #sender gets the ACK and processes it

        #obviously.. we dont need to do this if the timer has run out..!
        #and dont need to do this if we know that the ACK is lost..!
        if(not retransmit and (corrupted_ack is not None)):
            print("[sender]   ACK received")
            result = sender.verify_ACK_packet(corrupted_ack)
        else:
            result = "retransmit..!"

        #timer check..!
        if(sender.time_out):
            retransmit = True

        if(((packet is None) or (corrupted_ack is None))and (not sender.time_out)):
            while(not sender.time_out):
                time.sleep(0.001)

        #obviously.. we dont need to do this if the timer has run out..!
        if(not retransmit or (corrupted_ack is None)):
            if result == "retransmit..!":
                retransmit = True
            else:
                retransmit = retransmit or False

        #timer check..!
        if(sender.time_out):
            retransmit = True

        if not retransmit:
            #only move to next packet if ACK is valid
            print("[sender]   no error in transmission")
            i += 1
        else:
            if(not sender.time_out):
                print("[sender]   corrupt/incorrect ACK, Retransmitting...")

        sender.log()
        receiver.log()
        transmission_count += 1

        print("----------")

    print("Total # of transmissions =", transmission_count)


data_list = [
            "Hi hello",
            "how are you doing?",
            "bye bye!"
            ]

main(data_list)