import random
import matplotlib.pyplot as plt

cong_win_size = 1
rtt_count = 1

#for plotting the graph..
y_axis = []
x_axis = []

total_rtt = int(input("enter the total number of rtt: "))

threshold = None
threshold = int(input("enter the threshold value: "))

choice = int(input("how do you want your loss events to be..? (choose a number)\n" \
            "1. Random \n" \
            "2. Manually configured\n"))

if(choice == 2):
    num = int(input("enter no of loss events: "))
    loss_events = []

    for i in range(1, num + 1):
        foo = int(input(f"enter rtt of loss event {i}: "))
        loss_events.append(foo)


#make a fucntion that simulates a packet loss when cong_win_size is between the threshold and the actual tipping point..!
#how to calculate the tipping point..??? some f(threshold..?)..???
#randonmly choose a value between threhsold and tipping point..! (and also choose the loss event..! needed for tahoe..?)
#provide this value to the congestion avoidance phase..!
def random_between_1_and_tipping_point(threshold):
    return random.randint(2, threshold + 10)



#main simulation logic..!
def main():
    global rtt_count
    global threshold
    global cong_win_size

    print(f"RTT = {rtt_count}, congestion_win_size = {cong_win_size}, ssthresh = {threshold}")
    print('*' * 48)

    while(rtt_count < total_rtt):
        #append this rtt number to the x-axis and cong_win_size to the y-axis..!
        x_axis.append(rtt_count)
        y_axis.append(cong_win_size)

        if cong_win_size < threshold:
            #simulate slow start..!
            rtt_count += 1
            cong_win_size *= 2

            # y_axis.append(cong_win_size)
        else:
            #simulate congestion avoidace..!
            rtt_count += 1
            cong_win_size += 1

            # y_axis.append(cong_win_size)

        if(choice == 1):
            #if their choice was for random loss events..!
            if random.randint(0, 100) < 10:
                print("Packet Loss Detected!")
                print("resetting congestion window to 1..!")
                threshold = (cong_win_size // 2)
                cong_win_size = 1

                # #remove the last appended value.. and add the correct value..!
                # y_axis.pop()
                # y_axis.append(cong_win_size)

            else:
                print("No Packet Loss Detected")

        elif(choice == 2):
            #predefined loss events..!
            if(rtt_count in loss_events):
                print("Packet Loss Detected!")

                print("resetting congestion window to one..!")
                threshold = (cong_win_size // 2)
                cong_win_size = 1   

                # #remove the last appended value.. and add the correct value..!
                # y_axis.pop()
                # y_axis.append(cong_win_size)

        print(f"RTT = {rtt_count}, congestion_win_size = {cong_win_size}, ssthresh = {threshold}")

        print('*' * 48)

    #plot the graph..!
    plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b')
    plt.title("TCP Tahoe Congestion Window Evolution")
    plt.xlabel("RTT")
    plt.ylabel("Congestion Window Size")
    plt.grid(True)

    plt.savefig("tahoe_plot.png")
    plt.show()



main()