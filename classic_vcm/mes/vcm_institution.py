from mTree.microeconomic_system.environment import Environment
from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.agent import Agent
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
from collections import Counter
import math
import random
import logging
import time
import datetime


@directive_enabled_class
class VCMInstitution(Institution):
    """
    Plays guessing game with agent: Closest guess without going over.
    """
    
    def prepare(self):
        self.log_message(f"<I> prepare")      
        #same endowment for each agent
        self.endowment = self.get_property("endowment")
        self.group_rate = self.get_property("group_rate") 
        self.num_agents = self.address_book.num_agents()
        msg_out = f"endow: {self.endowment}, group_rate: {self.group_rate}, "
        msg_out += f"num_agents: {self.num_agents}"
        self.log_message(f'<I>: {msg_out}', target = self.short_name)
        self.round = 0


    @directive_decorator("start_period")
    def start_period(self, message: Message):
        self.round += 1
        log_it = f"<I> start-period :: round = {self.round}"
        self.log_message(log_it, target = self.short_name)
        self.agent_data = message.get_payload()
        self.num_contributions_received = 0
        for agent_name in self.agent_data:
            self.send_message('contribute', agent_name, self.round)


    @directive_decorator("contribution")
    def contribution(self, message: Message):
        self.num_contributions_received += 1
        agent_name, contribution = message.get_payload()
        self.agent_data[agent_name]['contribution'] = contribution
        self.log_message(f"<I> contribution :: payloads = {agent_name, contribution} {self.num_contributions_received}", target=self.short_name)
        if self.num_contributions_received == self.num_agents:
            self.process_contributions()


    def process_contributions(self):   
        group_contribution = 0
        for agent, data in self.agent_data.items():
            group_contribution += data['contribution']
        group_earnings = group_contribution * self.group_rate
        for agent, data in self.agent_data.items():
            data['period'] = self.round
            data['group_earn'] = group_earnings/len(self.agent_data)
            data['private_earn'] = data['endowment'] - data['contribution']
            data['total_earn'] = data['private_earn'] + data['group_earn']
            data['group_contribution'] = group_contribution
            data['group_earnings'] = group_earnings
            self.send_message('results', agent, data)
            self.log_data(data)
        log_it =  f"period = {self.round}, group_contribution = {group_contribution}"
        log_it += f" group_earnings = {group_earnings}"
        self.log_message(log_it, target = 'summary_data')
        self.send_message('next_round',"vcm_environment.VCMEnvironment")