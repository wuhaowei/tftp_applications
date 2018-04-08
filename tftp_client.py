import os
import socket
import struct

class TftpClient():
    def __init__(self, server_ip):
        # set up socket
        self.setup_socket()
        self.server_ip = server_ip
    
    def menu(self):
        print("*"*30)
        print("TFTP Server: " + self.server_ip)
        print(">>>1. download")
        print(">>>2. upload")
        print(">>>3. exit")
        print("*"*30)
        menu_selection = input(">>>")
        if menu_selection == "1":
            file_name = input("[Download] Please enter file name: ")
            self.request(1, file_name)
        elif menu_selection == "2":
            file_name = input("[Upload] Please enter file name: ")
            self.request(2, file_name)
        elif menu_selection == "3":
            print("exit...")
        else:
            print("\n", "Please enter a valid option!")
            self.menu()
            
    def setup_socket(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(("", 69))
    
    def request(self, op_num, file_name):
        if op_num == 1:
            request_msg = struct.pack("!H{}sb5sb".format(len(file_name)), 
                                    1, file_name.encode("utf-8"), 0, b"octet", 0)
            self.udpSocket.sendto(request_msg, (self.server_ip, 69))
            self.downloader(file_name)
        elif op_num == 2:
            pass
        else:
            pass

    def ack(self, block, server_addr):
        ack_msg = struct.pack("!HH", 4, block)
        self.udpSocket.sendto(ack_msg, server_addr)

    def downloader(self, file_name):
        f = open(file_name, "wb")
        finished = False
        block_num = 0
        while not finished:
            # receive and parse data
            recv_content, server_addr = self.udpSocket.recvfrom(1024)
            content_op_num = struct.unpack("!H", recv_content[:2])[0]
            # receive data
            if content_op_num == 3:
                content_block = struct.unpack("!H", recv_content[2:4])[0]
                content_data = recv_content[4:]
                # verify data and return acknowledgement
                if content_block == block_num:
                    # next expected block_num
                    block_num += 1
                    # reset block_num if count index exceeds 65535 (2 Bytes)
                    if block_num == 65536:
                        block_num = 0
                    # write data only if receive the data block 
                    f.write(content_data)
                    # determine if downloading is finished
                    if len(content_data) < 512:
                        finished = True
                else:
                    pass
                # send acknowledgement anyway
                self.ack(content_block, server_addr)
                print("block:{:6} -- {}".format(content_block, content_op_num), end="\r")
            # receive error
            elif content_op_num == 5:
                # close and delete created empty file
                f.close()
                os.unlink(file_name)
                # show message and quit the loop
                print("*"*30)
                print("The file <{}> does not exist...".format(file_name), "\n")
                break
        if finished:
            f.close()
            print("*"*30)
            print("The file <{}> was downloaded successfully...".format(file_name), "\n")

def main():
    server_ip = input("Please enter server IP: ")
    client = TftpClient(server_ip)
    client.menu()

if __name__ == "__main__":
    main()

