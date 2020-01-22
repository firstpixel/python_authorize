#!/usr/bin/env python2
# coding: latin-1
import sys, json, datetime
from datetime import timedelta, date
import time




class Authorize:
    def __init__(self, inputData):
        self.accountCreated = False
        self.defaultAccount = None
        self.availableLimit = 0 
        self.orderedArray = []
        self.totalResultString = ""
        self.originalOrderArray = []
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
                    
                    
                    self.violationArray = []
                    
                    self.orderedArray =  self.orderedArray if self.orderedArray > 0 else []
                    self.resultString = ""
                    self.resultObject = {}
                    self.transaction = None

                    if line == "EOF":
                        sys.stdout.flush()
                        pass 
                        return None

                    if not self.is_json(line):
                        continue
                    
                    
                    data = json.loads(line)
                    
                    transaction = None

                    
                    #for accountData in data:
                        
                    #check accounts
                    if "account" in data:
                        activeCard = data["account"]["active-card"]
                        availableLimit = data["account"]["available-limit"]
                        account = Account(activeCard, availableLimit)
                        self.violationArray = self.checkAccountViolations(self.violationArray, account)
                        account.setViolations(self.violationArray)
                        
                        
                        
                    #check transactions   
                    if "transaction" in data:
                        merchant = data["transaction"]["merchant"]
                        amount = data["transaction"]["amount"]
                        timeTrans = data["transaction"]["time"]
                        
                        self.transaction = Transaction(self.defaultAccount, merchant, amount, timeTrans, self.originalIndex)
                        self.violationArray = self.checkTransactionViolations(self.violationArray, self.defaultAccount, self.transaction)
                        self.transaction.setViolations(self.violationArray)
                        self.orderedArray.append(self.transaction)

                    
                    self.resultObject = self.getResultObject(self.defaultAccount, self.violationArray)
                    self.originalOrderArray.append(self.resultObject)

                            
                    #sort transaction array by time
                    DataToTime.sortByTime(self.orderedArray)
                    
                    #check for double transaction and small interval
                    self.orderedArray = self.getDoubledTransactionAndSmallIntervalViolations(self.orderedArray)
                    
                    self.setOriginalOrder()
                    self.orderedArray = self.clearOrderArrayList(self.orderedArray)
                    
                    if not self.transaction is None:
                        self.setTransactionAccountLimit( self.transaction, self.originalOrderArray[-1])
                    else:
                        self.originalOrderArray[-1]["account"]["available-limit"] = self.availableLimit

                    #transform item in string
                    if len(self.originalOrderArray) > 0:
                        self.resultString = json.dumps(self.originalOrderArray[-1]) + '\n'
                    
                    self.totalResultString += self.resultString

                    self.originalIndex += 1
                    #print list          
                    sys.stdout.write(self.resultString)
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
        while l < len(self.originalOrderArray):
            k = 0
            while k < len(self.orderedArray):
                if self.orderedArray[k].orIndex == l:
                    self.originalOrderArray[l]['violations'] = self.orderedArray[k].violations
                    self.originalOrderArray[l]['account']['available-limit'] = self.orderedArray[k].availableLimit if hasattr(self.orderedArray[k], 'availableLimit') else 0
                k += 1
            l += 1
        
    def getDoubledTransactionAndSmallIntervalViolations(self, transactionArray):
        
        i = 0
        listSize = len(transactionArray)
        intervalCounter = 1
        while i < listSize:
            trans = transactionArray[i]
            timeFormated = DataToTime.convertToTime(trans.time)
            timeDelta =  timeFormated + datetime.timedelta(0,120)
            j = i + 1
            
            first = transactionArray[i]
            
            while j < listSize and timeDelta >= DataToTime.convertToTime(transactionArray[j].time):
                next = transactionArray[j]
                if intervalCounter > 3:
                    if not self.transactionViolations.HIGH_FREQUENCY in transactionArray[j].violations:
                        transactionArray[j].violations.append(self.transactionViolations.HIGH_FREQUENCY)

                if first.merchant == next.merchant and first.amount == next.amount:
                    if not self.transactionViolations.DOUBLED in transactionArray[j].violations:
                        transactionArray[j].violations.append(self.transactionViolations.DOUBLED)
                
                intervalCounter += 1 
                j += 1
            i += 1
            if timeDelta < DataToTime.convertToTime(transactionArray[j-1].time):
                intervalCounter = intervalCounter if intervalCounter > 0 else 0
            
            
        return transactionArray
    def dump(self,obj):
        for attr in dir(obj):
            print("obj.%s = %r" % (attr, getattr(obj, attr)))
    def clearOrderArrayList(self, transactionArray):
        
        i = 0
        listSize = len(transactionArray)
        if listSize > 4:
            trans = transactionArray[-1]
            topItem = transactionArray[0]
            timeFormated = DataToTime.convertToTime(trans.time)
            timeDelta =  timeFormated - datetime.timedelta(0,180)
                
            if DataToTime.convertToTime(topItem.time) > timeDelta:
                transactionArray.pop(0)
        return transactionArray

    def getResultObject(self, account, violationArray):
        if account is None:
            return { "account": { "active-card": False, "available-limit": 0 }, "violations":  violationArray }
        else:
            return { "account": { "active-card":  self.defaultAccount.activeCard , "available-limit":  self.defaultAccount.availableLimit }, "violations":  violationArray }

    def enum(self,**enums):
            return type('Enum', (), enums)

    def checkAccountViolations(self, violationArray, account):    
        return self.checkAccountCreatedViolation(violationArray, account)

    def checkAccountCreatedViolation(self, violationArray, account):
        
        if self.accountCreated:
            account.availableLimit = self.availableLimit
            violationArray.append(self.accountViolations.INITIALIZED)
            return violationArray
        elif not account == None:
            self.defaultAccount = account
            self.availableLimit = account.availableLimit
            self.accountCreated = True
            return violationArray
    
    def checkTransactionViolations(self, violationArray, account, transaction):
        violationArray = self.checkTransactionAccountCreatedViolations( violationArray, account, transaction)
        if not self.transactionViolations.NOT_INITIALIZED in violationArray:
            violationArray = self.checkTransactionAccountActiveCardViolations( violationArray, account, transaction)
            if not self.transactionViolations.NOT_ACTIVE in violationArray:
                violationArray = self.checkTransactionAccountLimitViolations( violationArray, account, transaction)
        return violationArray

    def checkTransactionAccountCreatedViolations(self, violationArray, account, transaction):
        if self.accountCreated:
            account.availableLimit = self.availableLimit
            return violationArray
        else:
            violationArray.append(self.transactionViolations.NOT_INITIALIZED)
            return violationArray

    def checkTransactionAccountActiveCardViolations(self, violationArray, account, transaction):
        if account.activeCard:
            return violationArray
        else:
            violationArray.append(self.transactionViolations.NOT_ACTIVE)
            return violationArray

    def checkTransactionAccountLimitViolations(self, violationArray, account, transaction):
        if self.availableLimit - transaction.amount >= 0:
            return violationArray
        else:
            violationArray.append(self.transactionViolations.INSUFFICIENT)
            return violationArray

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
    def setViolations(self, violationsArray):
        self.violations = violationsArray
    

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
        self.transactionSortedArray.append(currentTransaction)
    
    def increaseTransactions():
        self.countTransactionsIn2Minutes += 1

    def setViolations(self, violationsArray):
        self.violations = violationsArray
    
    def addViolation(self, violation):
        self.violations.append(violation)

    def sortArray(unsortedArray): 
        return sorted(
        unsortedArray,
        key=lambda x: datetime.strptime(x['Created'], '%m/%d/%y %H:%M'), reverse=True
)


import select

if select.select([sys.stdin,],[],[],0.0)[0]:
    authorize = Authorize(sys.stdin)
else:
    print "No data"







#{"account": {"active-card": true, "available-limit": 100}}
#    {"transaction": {"merchant": "Burger King", "amount": 20, "time": "2019-02-13T10:00:00.000Z"}}


'''


Code Challenge: Authorizer
==========================

You are tasked with implementing an application that authorizes a
transaction for a specific account following a set of predefined rules.

Please read the instructions below, and feel free to ask for
clarifications if needed.

Packaging
---------

Your README file should contain a description on relevant code design
choices, along with instructions on how to build and run your
application.

Building and running the application must be possible under Unix or Mac
operating systems. [Dockerized
builds](https://docs.docker.com/engine/reference/commandline/build/) are
welcome.

You may use open source libraries you find suitable, but please refrain
as much as possible from adding frameworks and unnecessary boilerplate
code.

Sample usage
------------

Your program is going to be provided 'json' lines as input in the 'stdin', and should provide a 'json' line output for each one — imagine
this as a stream of events arriving at the authorizer.


    $ cat operations
    {"account": {"active-card": true, "available-limit": 100}}
    {"transaction": {"merchant": "Burger King", "amount": 20, "time": "2019-02-13T10:00:00.000Z"}}
    {"transaction": {"merchant": "Habbib's", "amount": 90, "time": "2019-02-13T11:00:00.000Z"}}

    $ authorize < operations

    {"account": {"active-card": true, "available-limit": 100}, "violations": []}
    {"account": {"active-card": true, "available-limit": 80}, "violations": []}
    {"account": {"active-card": true, "available-limit": 80}, "violations": ["insufficient-limit"]}

State
-----

The program **should not** rely on any external database. Internal state
should be handled by an explicit in-memory structure. State is to be
reset at application start.

Operations
----------

The program handles two kinds of operations, deciding on which one
according to the line that is being processed:

1.  Account creation
2.  Transaction authorization

For the sake of simplicity, you can assume all monetary values are
positive integers using a currency without cents.

* * * * *

### 1. Account creation

#### Input

Creates the account with 'available-limit' and 'active-card' set. For
simplicity sake, we will assume the application will deal with just one
account.

#### Output

The created account's current state + any business logic violations.

#### Business rules

-   Once created, the account should not be updated or recreated:
    'account-already-initialized'.

#### Examples

    input
        {"account": {"active-card": true, "available-limit": 100}}
        ...
        {"account": {"active-card": true, "available-limit": 350}}


    output
        {"account": {"active-card": true, "available-limit": 100}, "violations": []}
        ...
        {"account": {"active-card": true, "available-limit": 100}, "violations": ["account-already-initialized" ]}

* * * * *

### 2. Transaction authorization

#### Input

Tries to authorize a transaction for a particular 'merchant', 'amount'
and 'time' given the account's state and last **authorized**
transactions.

#### Output

The account's current state + any business logic violations.

#### Business rules

You should implement the following rules, keeping in mind **new rules
will appear** in the future:

-   No transaction should be accepted without a properly initialized
    account: 'account-not-initialized'

-   No transaction should be accepted when the card is not active:
    'card-not-active'

-   The transaction amount should not exceed available limit:
    'insufficient-limit'

-   There should not be more than 3 transactions on a 2 minute interval:
    'high-frequency-small-interval' (the input order cannot be relied
    upon, since transactions can eventually be out of order respectively
    to their 'time's)

-   There should not be more than 1 similar transactions (same amount
    and merchant) in a 2 minutes interval: 'doubled-transaction'

#### Examples

##### Given there is an account with 'active-card: true' and 'available-limit: 100':

    input
        {"transaction": {"merchant": "Burger King", "amount": 20, "time": "2019-02-13T10:00:00.000Z"}}

    output
        {"account": {"active-card": true, "available-limit": 80}, "violations": []}

##### Given there is an account with 'active-card: true', 'available-limit: 80' and 3 transaction occurred in the last 2 minutes:

    input
        {"transaction": {"merchant": "Habbib's", "amount": 90, "time": "2019-02-13T10:01:00.000Z"}}

    output
        {"account": {"active-card": true, "available-limit": 80}, "violations": ["insufficient-limit" "high-frequency-small-interval"]}

* * * * *

Error handling
--------------

-   Please assume input parsing errors will not happen. We will not
    evaluate your submission against input that breaks the contract.

-   Violations of the business rules are **not** considered to be errors
    as they are expected to happen and should be listed in the outputs's
    'violations' field as described on the 'output' schema in the
    examples. That means the program execution should continue normally
    after any violation.

Our expectations
----------------

We at Nubank value **simple, elegant, and working code**. This exercise
should reflect your understanding of it.

Your solution is expected to be **production quality**, **maintainable**
and **extensible**. Hence, we will look for:

-   Immutability;
-   Quality unit and integration tests;
-   Documentation where needed;
-   Instructions to run the code.

General notes
-------------

-   This challenge may be extended by you and a Nubank engineer on a
    different step of the process;
-   You should submit your solution source code to us as a compressed
    file containing the code and possible documentation. Please make
    sure not to include unnecessary files such as compiled binaries,
    libraries, etc;
-   Do not upload your solution to public repositories in GitHub,
    BitBucket, etc;
-   The project should be implemented as a stream application rather
    than a Rest API.
-   Please keep your test anonymous, paying attention to:
    -   the code itself, including tests and namespaces;
    -   version control author information;
    -   automatic comments your development environment may add.

AuthorizerChallenge.md
Displaying AuthorizerChallenge.md.


'''