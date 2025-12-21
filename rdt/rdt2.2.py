import random
import string

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
    prob = 0.17

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
    def udt_send(packet):
        try:
            if hasattr(packet, "ACK"):
                return channel.corrupt_ack_packet(packet)
        except Exception:
            return channel.corrupt_packet(packet)        
    
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

class Receiver(endsystem):
    last_received_ack = 1

    def __init__(self, state = "waiting for call 0 from below"):
        super().__init__("receiver")
        self.state = state
        self.packet = None

    def verify_packet_and_give_ACK_packet(self):
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
            return self.make_pkt(self.last_received_ack)
        
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

        #sender state is updated and receiver gets it..!
        receiver.packet, sender.state = rdt_send(sender, data)
        print(f"[receiver] called from below, received packet")

        #generating ACK packet for the received packet..!
        ack_packet = receiver.verify_packet_and_give_ACK_packet()
        corrupted_ack = channel.udt_send(ack_packet)
        print("[receiver] ACK sent")

        sender.log()
        receiver.log()

        #sender gets the ACK and processes it
        print("[sender]   ACK received")
        result = sender.verify_ACK_packet(corrupted_ack)

        if result != "retransmit..!":
            #only move to next packet if ACK is valid
            print("[sender]   no error in transmission")
            i += 1
        else:
            print("[sender]   incorrect/corrupt ACK, Retransmitting...")

        sender.log()
        receiver.log()
        transmission_count += 1

        print("----------")

    print("Total # of transmissions =", transmission_count)

# def random_message(length=20):
#     return ''.join(random.choice(string.ascii_letters + string.digits + ' ') for _ in range(length))

# data_list = [
#     random_message(20),
#     random_message(30),
#     random_message(25),
#     random_message(40),
#     random_message(15)
# ]

data_list = [
            "Hi hello",
            "how are you doing?",
            "bye bye!"
            ]

main(data_list)