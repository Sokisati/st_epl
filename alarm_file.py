class AlarmSystem:
    
    def __init__(self):
       self.errorCodeList = [0,0,0,0,0];

    
    def shellNotResponding(self):
           self.errorCodeList[2]=1;
       
    def seperationFailed(self):
           self.errorCodeList[4]=1;
        
    def seperationSuccesful(self):
           self.errorCodeList[4]=1;

        
        