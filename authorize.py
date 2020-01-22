#!/usr/bin/env python2
# coding: latin-1
#
# developed for nubank interview
#
# run sample:
# python authorize.py < testcases/operations0
#
# to let it run indefinitely, remove the EOF from opertions files
# to stop the script, just press Ctrl+c
#
# run test:
# python authorize_test.py 
# will run all testcases

import sys, json, datetime, time, select
from datetime import timedelta, date


class Authorize:
    def __init__(self, inputData, testing = False):
        self.accountCreated = False
        self.defaultAccount = None
        self.availableLimit = 0 
        self.orderedList = []
        if testing:
            self.totalResultString = ""
        self.originalOrderList = []
        self.accountViolations = self.enum(  
            INITIALIZED = "account-already-initialized"  
        )
        self.transactionViolations = self.enum(
            NOT_INITIALIZED = "account-not-initialized",
            NOT_ACTIVE = "card-not-active",
            INSUFFICIENT="insufficient-limit",
            HIGH_FREQUENCY = "high-frequency-small-interval",
            DOUBLED="doubled-transaction"
        )
        self.originalIndex = 0
        try:
            while True:
                for line in iter(sys.stdin.readline, b''):
                    self.violationList = []
                    self.orderedList =  self.orderedList if len(self.orderedList) > 0 else []
                    self.resultString = ""
                    self.resultObject = {}
                    self.transaction = None

                    #break for test cases
                    if line == "EOF":
                        sys.stdout.flush()
                        pass 
                        return None

                    #check if line is json
                    if not self.is_json(line):
                        continue
        
                    data = json.loads(line)
                    transaction = None
                        
                    #check accounts
                    if "account" in data:
                        activeCard = data["account"]["active-card"]
                        availableLimit = data["account"]["available-limit"]
                        account = Account(activeCard, availableLimit)
                        #add account violations
                        self.violationList = self.checkAccountViolations(self.violationList, account)
                        account.setViolations(self.violationList)
                    
                    #check transactions   
                    if "transaction" in data:
                        merchant = data["transaction"]["merchant"]
                        amount = data["transaction"]["amount"]
                        timeTrans = data["transaction"]["time"]
                        self.transaction = Transaction(self.defaultAccount, merchant, amount, timeTrans, self.originalIndex)
                        #add transaction violations
                        self.violationList = self.checkTransactionViolations(self.violationList, self.defaultAccount, self.transaction)
                        self.transaction.setViolations(self.violationList)
                        self.orderedList.append(self.transaction)

                    self.resultObject = self.getResultObject(self.defaultAccount, self.violationList)
                    self.originalOrderList.append(self.resultObject)
      
                    #sort transaction List by time
                    DataToTime.sortByTime(self.orderedList)
                    
                    #check for double transaction and small interval
                    self.orderedList = self.getDoubledTransactionAndSmallIntervalViolations(self.orderedList)
                    
                    #put ordered list back into original list
                    self.setOriginalOrder()

                    #clear order list 4 minuts behind
                    self.orderedList = self.clearOrderList(self.orderedList)
                    
                    #calculate account limit 
                    if not self.transaction is None:
                        self.setTransactionAccountLimit( self.transaction, self.originalOrderList[-1])
                    else:
                        self.originalOrderList[-1]["account"]["available-limit"] = self.availableLimit

                    #transform item in string
                    if len(self.originalOrderList) > 0:
                        self.resultString = json.dumps(self.originalOrderList[-1]) + '\n'
                    if testing:
                        self.totalResultString += self.resultString

                    self.originalIndex += 1

                    #print to console
                    sys.stderr.write(self.resultString)
                    #sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.flush()
            pass 

    def is_json(self, myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError as e:
            return False
        return True
    
    def setOriginalOrder(self):
        k=0
        l=0
        while l < len(self.originalOrderList):
            k = 0
            while k < len(self.orderedList):
                if self.orderedList[k].orIndex == l:
                    self.originalOrderList[l]['violations'] = self.orderedList[k].violations
                    self.originalOrderList[l]['account']['available-limit'] = self.orderedList[k].availableLimit if hasattr(self.orderedList[k], 'availableLimit') else 0
                k += 1
            l += 1
        
    def getDoubledTransactionAndSmallIntervalViolations(self, transactionList):
        
        i = 0
        listSize = len(transactionList)
        intervalCounter = 1
        while i < listSize:
            trans = transactionList[i]
            timeFormated = DataToTime.convertToTime(trans.time)
            timeDelta =  timeFormated + datetime.timedelta(0,120)
            j = i + 1
            first = transactionList[i]
            
            while j < listSize and timeDelta >= DataToTime.convertToTime(transactionList[j].time):
                next = transactionList[j]
                if intervalCounter > 3:
                    if not self.transactionViolations.HIGH_FREQUENCY in transactionList[j].violations:
                        transactionList[j].violations.append(self.transactionViolations.HIGH_FREQUENCY)

                if first.merchant == next.merchant and first.amount == next.amount:
                    if not self.transactionViolations.DOUBLED in transactionList[j].violations:
                        transactionList[j].violations.append(self.transactionViolations.DOUBLED)
                
                intervalCounter += 1 
                j += 1
            i += 1
            if timeDelta < DataToTime.convertToTime(transactionList[j-1].time):
                intervalCounter = intervalCounter if intervalCounter > 0 else 0

        return transactionList


    def dump(self,obj):
        for attr in dir(obj):
            print("obj.%s = %r" % (attr, getattr(obj, attr)))

    def clearOrderList(self, transactionList):
        i = 0
        listSize = len(transactionList)
        if listSize > 4:
            trans = transactionList[-1]
            topItem = transactionList[0]
            timeFormated = DataToTime.convertToTime(trans.time)
            timeDelta =  timeFormated - datetime.timedelta(0,240)
                
            if DataToTime.convertToTime(topItem.time) > timeDelta:
                transactionList.pop(0)
        return transactionList


    def getResultObject(self, account, violationList):
        if account is None:
            return { "account": { "active-card": False, "available-limit": 0 }, "violations":  violationList }
        else:
            return { "account": { "active-card":  self.defaultAccount.activeCard , "available-limit":  self.defaultAccount.availableLimit }, "violations":  violationList }


    def enum(self,**enums):
            return type('Enum', (), enums)


    def checkAccountViolations(self, violationList, account):    
        return self.checkAccountCreatedViolation(violationList, account)


    def checkAccountCreatedViolation(self, violationList, account):
        if self.accountCreated:
            account.availableLimit = self.availableLimit
            violationList.append(self.accountViolations.INITIALIZED)
            return violationList
        elif not account == None:
            self.defaultAccount = account
            self.availableLimit = account.availableLimit
            self.accountCreated = True
            return violationList
    

    def checkTransactionViolations(self, violationList, account, transaction):
        violationList = self.checkTransactionAccountCreatedViolations( violationList, account, transaction)
        if not self.transactionViolations.NOT_INITIALIZED in violationList:
            violationList = self.checkTransactionAccountActiveCardViolations( violationList, account, transaction)
            if not self.transactionViolations.NOT_ACTIVE in violationList:
                violationList = self.checkTransactionAccountLimitViolations( violationList, account, transaction)
        return violationList


    def checkTransactionAccountCreatedViolations(self, violationList, account, transaction):
        if self.accountCreated:
            account.availableLimit = self.availableLimit
            return violationList
        else:
            violationList.append(self.transactionViolations.NOT_INITIALIZED)
            return violationList


    def checkTransactionAccountActiveCardViolations(self, violationList, account, transaction):
        if account.activeCard:
            return violationList
        else:
            violationList.append(self.transactionViolations.NOT_ACTIVE)
            return violationList


    def checkTransactionAccountLimitViolations(self, violationList, account, transaction):
        if self.availableLimit - transaction.amount >= 0:
            return violationList
        else:
            violationList.append(self.transactionViolations.INSUFFICIENT)
            return violationList


    def setTransactionAccountLimit(self,  transaction, item):
        if len(transaction.violations) == 0 and (self.availableLimit - transaction.amount) >=0:
            self.availableLimit = self.availableLimit - transaction.amount
            item["account"]["available-limit"] = self.availableLimit
        else:
            item["account"]["available-limit"] = self.availableLimit   



class DataToTime:
    @staticmethod
    def convertToTime(str):
        dateFromStr = datetime.datetime.strptime(str,"%Y-%m-%dT%H:%M:%S.%fZ")
        return dateFromStr
    @staticmethod
    def sortByTime(transactionList):
        transactionList.sort(key=lambda x:DataToTime.takeTime(x))
    @staticmethod
    def takeTime(elem):
        return elem.time



class Account:
    def __init__(self,activeCardStr, availableLimitStr):
        self.activeCard = activeCardStr
        self.availableLimit = availableLimitStr
    def setViolations(self, violationsList):
        self.violations = violationsList
    


class Transaction:
    def __init__(self,accountObj, merchantStr, amountStr, timeStr, origIndex):
        self.merchant = merchantStr
        self.amount = amountStr
        self.currentTransaction = None
        self.time = timeStr
        self.account = accountObj
        self.orIndex = origIndex
        
    def addTransaction(merchantStr, amountStr, timeStr):
        currentTransaction = {merchant:merchantStr, amounth:amount}
        self.transactionList.add()
        self.transactionSortedList.append(currentTransaction)
    

    def increaseTransactions():
        self.countTransactionsIn2Minutes += 1


    def setViolations(self, violationsList):
        self.violations = violationsList
    

    def addViolation(self, violation):
        self.violations.append(violation)


    def sortList(unsortedList): 
        return sorted(
        unsortedList,
        key=lambda x: datetime.strptime(x['Created'], '%m/%d/%y %H:%M'), reverse=True
        )


if select.select([sys.stdin,],[],[],0.0)[0]:
    authorize = Authorize(sys.stdin, False)
else:
    print("No data")
