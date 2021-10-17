# echo_client.py
import socket, time, sys

class Decapper():

    state = "capped"
    s = None

    def __init__(self):

        # initial window setup
        # super().__init__()
        host = "169.254.44.133"#"192.168.1.2"#'169.254.140.234'
        port = 10005
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        print("hello")

        while(True):
            self.cycle()
            self.wait()
    


    def cycle(self):
        print("incycle")
        if self.state == "capped":
            print("going to decap")
            self.s.sendall(b"startdecapping\r\n")
            print(self.s.recv(1024).decode("utf-8"))
            self.state = "decapped"
            time.sleep(5)
        elif self.state == "decapped":
            print("going to cap")
            self.s.sendall(b"startcapping\r\n")
            print(self.s.recv(1024).decode("utf-8"))
            self.state = "capped"
            time.sleep(5)

    def wait(self):
        wait_data = ""
        while str(wait_data) != str(1) or str(wait_data) != str(4):
                self.s.sendall(b"getstate\r\n")
                data = self.s.recv(1024)
                wait_data = data.decode("ascii")[:1]
                print(wait_data)
                time.sleep(5)
                if str(wait_data) == str(4):
                    print("ready")
                    break
                else:
                    print("not ready")
                if str(wait_data) == str(1):
                    print("ready")
                    break
                else:
                    print("not ready")
        time.sleep(5)
        

if __name__ == '__main__':
    app = Decapper()
    sys.exit(app.exec_())
    

