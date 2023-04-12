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
from dataclasses import dataclass



@directive_enabled_class
class VCMHumanAgent(Agent):
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

        self.contribution_history = []

        self.period_length = self.get_property("period_length")
        
        self.beginning_cash = 0
        self.register_outlet("beginning_cash", "beginning_cash")


        self.message = ""
        self.register_outlet("message", "message")

        self.total_earnings = 0
        self.register_outlet("total_earnings", "total_earnings")

        self.period = 0
        self.register_outlet("period", "period")

        self.group_rate = self.get_property("group_rate")
        self.register_outlet("group_rate", "group_rate")

        self.savings_rate = self.get_property("savings_rate")
        self.register_outlet("savings_rate", "savings_rate")

        self.time_left = 10
        self.register_outlet("time_left", "time_left")

        self.num_participants = 0
        self.register_outlet("num_participants", "num_participants")

        self.total_contribution = 0
        self.register_outlet("total_contribution", "total_contribution")

        self.savings = 0
        self.register_outlet("savings", "savings")


        self.return_on_group = 0
        self.register_outlet("return_on_group", "return_on_group")
        self.return_on_savings = 0
        self.register_outlet("return_on_savings", "return_on_savings")
        self.period_earnings = 0
        self.register_outlet("period_earnings", "period_earnings")


        self.prev_group_return = None
        self.register_outlet("prev_group_return", "prev_group_return")

        self.prev_savings_return = None
        self.register_outlet("prev_savings_return", "prev_savings_return")

        self.previous_period = None
        self.register_outlet("previous_period", "previous_period")

        self.previous_period_earnings = None
        self.register_outlet("previous_period_earnings", "previous_period_earnings")


        self.register_outlet("endowment", "endowment")
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
        # self.log_message(f"{round}, {self.short_name}, {self.my_type}, {contribution}", target='agent_data')
        return contribution


    @directive_decorator("time_update")
    def time_update(self, message: Message):
        self.time_left = self.time_left - 1
        if self.time_left > 0:
            logging.info("Should be updating time left...")
            reminder_msg = Message()
            reminder_msg.set_sender(self.myAddress)
            reminder_msg.set_directive("time_update")
            self.reminder(seconds_to_reminder = 1,
                            message = reminder_msg)
        else:
            self.send_message('end_period', [self.myAddress])


    @directive_decorator("end_period")
    def end_period(self, message: Message):
        self.send_to_subject("execute_method", {"method": "disable_contribution_buttons"})
        

    @directive_decorator("final_values")
    def final_values(self, message: Message):
        contribution_history_item = message.get_payload()
        #### Previous period information prep
        self.prev_group_return = contribution_history_item["earnings"]
        self.prev_savings_return = (self.savings * self.savings_rate)
        self.previous_period = contribution_history_item["period"]
        self.previous_period_earnings = self.prev_group_return + self.prev_savings_return
        ####

        earnings = contribution_history_item["earnings"] + self.prev_savings_return
        self.total_earnings += earnings
        contribution_history_item["earnings"] = earnings
        self.contribution_history.append(contribution_history_item)
        
        self.send_to_subject("execute_method", {"method": "display_contribution_history", 
            "parameters": {"data": [contribution_history_item] } })

    @directive_decorator("display_message")
    def display_message(self, message: Message):
        self.message = message.get_payload()["message"]
        

    @directive_decorator("init_agent")
    def init_agent(self, message: Message):
        self.my_type = message.get_payload()
        # type can be 'C', 'D', 'CC'
        self.send_message('agent_started','vcm_environment.VCMEnvironment')
        self.send_to_subject("display_ui", {"ui_file": "agent.html"})
        reminder_msg = Message()
        reminder_msg.set_sender(self.myAddress)
        reminder_msg.set_directive("time_update")
        # self.reminder(seconds_to_reminder = 1,
        #                 message = reminder_msg)


    @directive_decorator("pool_update") #, human_subject_post="", computation_response="")
    def pool_update(self, message: Message):
        temp = message.get_payload()
        self.total_contribution = temp["total_contributions"]
        self.num_participants = temp["participants_count"]

    @directive_decorator("submit_contribution") #, human_subject_post="", computation_response="")
    def submit_contribution(self, message: Message):
        contribution = int(message.get_payload()["contribution"])
        self.log_message(f"<A {self.short_name}> contribute")
        round = message.get_payload()
        self.savings = self.beginning_cash - contribution
        payload = (self.short_name, contribution)
        self.send_message('contribution', 'vcm_institution.VCMInstitution', payload)


    @directive_decorator("contribute")
    def contribute(self, message: Message):
        self.group_rate = self.get_property("group_rate")
        self.savings_rate = self.get_property("savings_rate")
        self.time_left = self.get_property("period_length")
        self.log_message(f"<A {self.short_name}> contribute")
        round_data = message.get_payload()
        self.period = round_data["round"]
        self.message = round_data["message"]
        self.beginning_cash = round_data["beginning_cash"]
        self.savings = self.beginning_cash
        #contribution = self.make_contribution(self.period)
        #payload = (self.short_name, contribution)
        # self.send_message('contribution', 'vcm_institution.VCMInstitution', payload)
        self.send_to_subject("execute_method", {"method": "enable_contribution_buttons"})
        reminder_msg = Message()
        reminder_msg.set_sender(self.myAddress)
        reminder_msg.set_directive("time_update")
        self.reminder(seconds_to_reminder = 1,
                        message = reminder_msg)



    @directive_decorator("results")
    def results(self, message: Message):
        cont, pe, ge, gc, te = message.get_payload()
        self.log_message(f"<A {self.short_name}> last contribution is {cont}, private earning is {pe}, group earning is {ge}, total earning is {te}")
        self.last_group_contribution = gc
 
