from mTree.microeconomic_system.environment import Environment
from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.agent import Agent
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
import math
import random
import logging
import time
import datetime
import sys
import traceback
import copy

@directive_enabled_class
class AuctionEnvironment(Environment):
    def prepare(self):
        pass

    
    @directive_decorator("start_environment")
    def start_environment(self, message: Message):
        """
        Message handler for first message in simulation.
        """
        pass
        # self.set_reminder('end', 10)
        # agent_types = self.make_agent_types()
        # self.agents_reported = 0
        # agents = self.address_book.get_agents()
        # for k,agent in enumerate(agents):
        #     agent_type = agent_types[k]
        #     self.send_message('init_agent', agent, agent_type)




    def provide_endowment(self):
        endowment = 30
        new_message = Message()  # declare message
        new_message.set_sender(self.myAddress)  # set the sender of message to this actor
        new_message.set_directive("set_endowment")  # Set the directive (refer to 3. Make Messages) - has to match receiver decorator
        new_message.set_payload({"endowment": endowment})
        logging.info("SHOULD BE PROVISDING ENDOWMENT")
        logging.info(new_message)
        
        self.send_message("set_endowment",self.address_book.select_addresses({"address_type": "agent"}) ,{"endowment": endowment})
            
    def start_auction(self):
        
        # new_message = Message()  # declare message
        # new_message.set_sender(self.myAddress)  # set the sender of message to this actor
        # new_message.set_directive("start_auction")
        # self.send(self.institution_address, new_message)  
        new_message = Message()  # declare message
        new_message.set_sender(self.myAddress)  # set the sender of message to this actor
        new_message.set_directive("start_auction")
        new_message.set_payload({"address_book": self.address_book.get_addresses()})
        self.send(self.address_book.select_addresses({"address_type": "institution"}), new_message) 
        
