import time
import socket

class Driver():
    def __init__(self):
        self.robot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.initialized = False

    # Open Connection establishes a connection using a specific IP address and port.
    def open_connection(self, IPAddress):
        if self.connected == True:
            return 'MockRobot is already connected...'
        else:
            print('Connecting to MockRobot on port 1000...')  
        try:
            server_address = (IPAddress, 1000)
            # Connecting to remote socket at specific address.
            self.robot.connect(server_address)
            self.connected = True
            return ''
        except:
            return 'Failed to connect to MockRobot...'

    # Initialize places MockRobot into an automation-ready (homed) state.
    def initialize(self):
        if self.connected != True:
            return 'MockRobot is not connected...'
            
        if self.initialized == True:
            return 'MockRobot is already initialized...'

        processID = self.robot.sendall('home%')
        status = 'In Progress'

        # Check status every few seconds to see if the status has changed.
        while status == 'In Progress':
            time.sleep(5)
            status = self.robot.sendall('status%' + processID)

        # Status has changed, if successful, return empty string.
        if status == 'Finished Successfully':
            self.initialized == True
            return ''
        
        # If initialization fails, return error status.
        else:
            return status

    # Validate input checks the user's input to ensure it's a valid operation.
    def validateInput(self, operation, parameterNames, parameterValues):
        validOperations = {'pick', 'place', 'transfer'}
        validParameterNames = {'destination location', 'source location'}

        status = ''
        if operation.lower() not in validOperations:
            status += f'{operation} is an invalid operation.\n'
            
        for name in parameterNames:
            if name.lower() not in validParameterNames:
                status += f'{name} is an invalid parameter name.\n'
        
        for value in parameterValues:
            if not value.isnumeric(): 
                status += f'{operation} is an invalid parameter value.\n'

        return status   

    # The UI calls this function and expects that the device driver will perform an operation determined by the
    # parameter operation
    def ExecuteOperation(self, operation, parameterNames, parameterValues):
        # Prevent user from executing operation if driver isn't connected and initialized
        if self.connected == False or self.initialized == False:
            return 'Unable to execute operation. MockRobot is either not connected or not initialized...'

        # Checking user's input using validInput function
        inputIsValid = self.validateInput(self, operation, parameterNames, parameterValues)
        if self.validateInput(operation, parameterNames, parameterValues) != '':
            return inputIsValid

        # MockRobot doesn't have a 'Transfer' API call. Transfer is a 'pick' followed by a 'place'.
        if operation == 'Transfer':
            operation = 'Pick'
        
        # Loop through parameterNames referencing the index and send commands to MockRobot.
        for i in len(parameterNames):
            self.processID = self.robot.sendall(operation + '%' + parameterNames[i] + parameterValues[i])

            # Process can take up to five minutes, check status every five seconds, exit while loop when status changes
            status = 'In Progress'
            while status == 'In Progress':
                time.sleep(5)
                status = self.robot.sendall('status%' + self.processID)
            
            # If process fails, return error and don't continue
            if status == 'Terminated With Error':
                return status

            # The transfer operation needs to change from 'Pick' to 'Place' to continue looping
            if operation == 'Pick':
                operation == 'Place'
            else:
                operation = 'Pick'
            
        # If the operation completed successfully, return empty string
        return ''

    def abort(self):
        if self.connected == True:
            print('Closing connection with MockRobot.')
            self.robot.close()
            return ''
        else:
            return 'No connection with MockRobot to close.'
