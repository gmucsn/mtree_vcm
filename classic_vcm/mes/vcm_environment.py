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


@directive_enabled_class
class VCMEnvironment(Environment):
    """
    Tells Institution to start and waits for end
    """

    def prepare(self):
        self.log_message("<E> prepare")      
        #same endowment for each agent
        self.endowment = self.get_property("endowment")
        # list of lists of buyer values, one list per buyer
        self.group_rate = self.get_property("group_rate") 
        # get num_participants
        self.num_participants = self.get_property("num_participants") 
        self.num_cooperators = self.get_property("num_cooperators")
        self.num_defectors = self.get_property("num_defectors")
        self.num_conditional_cooperators = self.get_property("num_conditional_cooperators")
        self.total_rounds = self.get_property("total_rounds")
        self.num_agents = self.address_book.num_agents()
        self.round = 1
        msg_out = f"endowment: {self.endowment}, group_rate: {self.group_rate}, "
        msg_out += f"num_participants: {self.num_participants}, "
        msg_out += f"num_agents: {self.num_agents}, total_rounds: {self.total_rounds}"
        self.log_message(f'<E> prepare: {msg_out}')


    def set_reminder(self, directive, seconds_to_reminder):
        """Sets a reminder to send a message"""
        reminder_msg = Message()
        reminder_msg.set_sender(self.myAddress)
        reminder_msg.set_directive(directive)
        self.reminder(seconds_to_reminder = seconds_to_reminder,
                      message = reminder_msg)


    def make_agent_types(self):
        """Prepare agent types for agents"""
        agent_types = []
        for k in range(self.num_cooperators):
            agent_types.append("C")
        for k in range(self.num_defectors):
            agent_types.append("D")
        for k in range(self.num_conditional_cooperators):
            agent_types.append("CC")
        random.shuffle(agent_types)
        return agent_types
    
    def make_agent_data(self, agent_types):
        self.agent_data = {}
        for k in range(self.num_agents):
            agent = {}
            name = f"vcm_agent.VCMAgent {k+1}"
            agent['name'] = name
            agent['type']= agent_types[k]
            agent['endowment'] = self.endowment
            agent['contribution'] = 0
            agent['group_earn'] = 0.0
            agent['private_earn'] = 0.0
            agent['total_earn'] = 0.0
            self.log_message(f"<E> make agent data {agent}")
            self.agent_data[name] = agent


    @directive_decorator("start_environment")
    def start_environment(self, message: Message):
        """
        Message handler for first message in simulation.
        """
        #self.set_reminder('end', 10)
        agent_types = self.make_agent_types()
        self.make_agent_data(agent_types)
        self.agents_reported = 0
        for agent_name, agent in self.agent_data.items():
            self.send_message('init_agent', agent_name, agent)


    @directive_decorator("agent_started")
    def agents_started(self, message: Message):
        self.agents_reported += 1
        if self.agents_reported == self.num_agents:
            self.send_message('start_period', 'vcm_institution.VCMInstitution', self.agent_data)


    @directive_decorator("next_round")
    def next_round(self, message: Message):
        self.round += 1
        self.log_message("<E>-received request for next round")
        self.log_message(self.round)
        if self.round <= self.total_rounds:
             self.send_message('start_period', 'vcm_institution.VCMInstitution', self.agent_data)
        else:
            self.log_message(f'<E> Ending in 3',target='summary_data')
            self.set_reminder('end', 3)

  
    @directive_decorator("end")
    def end(self, message: Message):
        self.log_message(f'<E> Shutdown', target='summary_data')
        self.shutdown_mes()

