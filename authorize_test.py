#!/usr/bin/env python2
# coding: latin-1
#
# author: Gil Beyruth
# developed for nubank interview
#
# run sample:
# python authorize.py < testcases/operations0
#
# to let it run undefinetly remove the EOF from opertions files
#
# run test:
# python authorize_test.py 
# will run all testcases
#
import unittest, sys, json
from colorprint import ColorPrint as _
from authorize import Authorize

class TestAuthorize(unittest.TestCase):

    """
    Authorize class test
    """

    """
    Test Account
    """    
    def test_Account(self):
        _.print_bold("test_Account")
        sys.stdin = open('testcases/operations0', 'r')
        resultValidation = open('testcases/validations0', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)
    
    """
    Test No Account
    """
    def test_noAccount(self):
        _.print_bold("test_noAccount")
        sys.stdin = open('testcases/operations1', 'r')
        resultValidation = open('testcases/validations1', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)
    
    """
    Test Account already created
    """
    def test_accountAlreadyInitialized(self):
        _.print_bold("test_accountAlreadyInitialized")
        sys.stdin = open('testcases/operations2', 'r')
        resultValidation = open('testcases/validations2', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)

    """
    Test Account with card not active
    """
    def test_accountCardNotActive(self):
        _.print_bold("test_accountCardNotActive")
        sys.stdin = open('testcases/operations3', 'r')
        resultValidation = open('testcases/validations3', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)

    """
    Test Transaction insufficient limit
    """
    def test_accountInsuficientLimit(self):
        _.print_bold("test_accountInsuficientLimit")
        sys.stdin = open('testcases/operations4', 'r')
        resultValidation = open('testcases/validations4', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)
    
    """
    Test Transaction Doubled
    """
    def test_transactionDoubled(self):
        _.print_bold("test_transactionDoubled")
        sys.stdin = open('testcases/operations5', 'r')
        resultValidation = open('testcases/validations5', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)

    """
    Test Transaction and Account mixed violations
    """
    def test_transactionMix(self):
        _.print_bold("test_transactionMix")
        sys.stdin = open('testcases/operations6', 'r')
        resultValidation = open('testcases/validations6', 'r').read()
        self.validateAuthorize( sys.stdin, resultValidation)

    def validateAuthorize(self, stdin, resultValidation):
        authorize = Authorize(stdin, True)
        totalResults = []
        totalValidation = []

        for line in authorize.totalResultString.splitlines():
            totalResults.append(json.loads(line))

        for lineValidation in resultValidation.splitlines():
            totalValidation.append(json.loads(lineValidation))
        
        self.assertEqual(self.ordered(totalValidation) , self.ordered(totalResults))
        
    def ordered(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj

if __name__ == '__main__':
    unittest.main()