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
import numpy as np


@directive_enabled_class
class VCMAgent(Agent):
    """
    Buyer or Seller agent in bargaining game
    """ 
    
    def prepare(self):
        self.log_message(f"<A-{self.short_name}> prepare")      
        #same endowment for each agent
        self.endowment = self.get_property("endowment")
        # list of lists of buyer values, one list per buyer
        self.group_rate = self.get_property("group_rate") 
        # get num_participants
        self.start_cc = self.get_property("start_cc") 
        self.num_participants = self.get_property("num_participants") 
        self.num_agents = self.address_book.num_agents()
        msg_out = f"endow: {self.endowment}, group_rate: {self.group_rate}, "
        msg_out += f"num_participants: {self.num_participants}, "
        msg_out += f"num_agents: {self.num_agents}"
        self.log_message(f'<A-{self.short_name}>: {msg_out}')


    def make_contribution(self, round):
        mu,sigma = 0, 4
        nn=np.random.normal(mu, sigma)
        self.log_message(f"numpy_random_normal-{nn}")
        #contribution= random.normal(self.endowment, sigma, 1)[0]
        noise=abs(random.gauss(0, 4))
        self.log_message(f"noise--{noise}")
        contribution = 0
        if self.my_type == 'C':
            contribution= self.endowment-noise
        elif self.my_type == 'D':
            contribution= noise
        elif self.my_type == 'CC':
            if round<=1:
                contribution= self.start_cc-noise
            else: 
                contribution = self.last_group_contribution/self.num_agents + noise
        contribution = int(contribution)
        # maintain boundary conditions after added noise
        if contribution > self.endowment:
            contribution = self.endowment
        if contribution < 0:
            contribution = 0
        log_it = f"{round}, {self.short_name}, {self.my_type},"
        if round > 1:
            log_it += f"{self.last_group_contribution},"
            log_it += f" {self.last_group_contribution/self.num_agents},"        
        log_it += f" {contribution}"
        self.log_message(log_it, target='agent_data')
        return contribution


    @directive_decorator("init_agent")
    def init_agent(self, message: Message):
        self.agent_data = message.get_payload()
        self.my_type = self.agent_data['type']
        # type can be 'C', 'D', 'CC'
        self.send_message('agent_started','vcm_environment.VCMEnvironment')
        log_it = f"<A> init agent {self.agent_data}"
        self.log_message(log_it, target='agent_data')


    @directive_decorator("contribute")
    def contribute(self, message: Message):
        self.log_message(f"<A {self.short_name}> contribute")
        round = message.get_payload()
        contribution = self.make_contribution(round)
        payload = (self.short_name, contribution)
        self.send_message('contribution', 'vcm_institution.VCMInstitution', payload)


    @directive_decorator("results")
    def results(self, message: Message):
        data = message.get_payload()
        self.log_message(data, target = 'agent_data')
        self.last_group_contribution = data['group_contribution']
 
