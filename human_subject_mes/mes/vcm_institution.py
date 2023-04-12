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
from dataclasses import dataclass, asdict


class VCMPool:
    def __init__(self, group_return=5) -> None:
        self.group_return = group_return
        self.contributor_map = {}
        self.contributor_earnings = {}
        self.total_contributions = 0
        self.total_returns = 0
    
    def contribute(self, contributor, contribution):
        """_summary_

        Args:
            contributor (_type_): _description_
            contribution (_type_): _description_
        """
        if contributor not in self.contributor_map.keys():
            self.contributor_map[contributor] = 0
        self.contributor_map[contributor] = contribution
        self.total_contributions = sum(self.contributor_map.values())

    def participant_count(self):
        return len(self.contributor_map.keys())

    def determine_earnings(self):
        self.total_returns = self.total_contributions * self.group_return
        for contributor in self.contributor_map.keys():
            returns_temp = {}
            returns_temp["return"] = self.total_returns/self.participant_count()
            returns_temp["contribution"] = self.contributor_map[contributor]
            self.contributor_earnings[contributor] = returns_temp

    def retrieve_earnings(self, contributor):
        if contributor in self.contributor_earnings.keys():
            return self.contributor_earnings[contributor]
        else:
            return None    

    def reset(self):
        self.contributor_map = {}
        self.total_contributions = 0
    

@dataclass
class ContributionHistory:
    subject_id: str
    period: int
    investment: int
    total: int
    num_investors: int
    earnings: int = None



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
        self.period_length = self.get_property("period_length") + self.get_property("agent_period_adjustment")
        
        msg_out = f"endow: {self.endowment}, group_rate: {self.group_rate}, "
        msg_out += f"num_agents: {self.num_agents}"
        # self.log_message(f'<I>: {msg_out}, target = self.short_name')

        self.pool = VCMPool(group_return=self.group_rate)
        self.total_contributions = 0
        self.participants_count = 0
        self.participants_map = {}


        self.round = 0

    @directive_decorator("end_period")
    def end_period(self, message: Message):
        self.pool.determine_earnings()
        # Update with period end information
        agents = self.address_book.get_agents()
        for agent in agents:
            return_information = self.pool.retrieve_earnings(agent)
            if return_information is not None:
                temp_info = ContributionHistory(subject_id=None,
                        period=self.round,
                        investment=return_information["contribution"],
                        num_investors=self.pool.participant_count(),
                        total=self.pool.total_contributions,
                        earnings=return_information["return"]
                        )
            else:
                temp_info = ContributionHistory(subject_id=None,
                        period=self.round,
                        investment=0,
                        num_investors=self.pool.participant_count(),
                        total=self.pool.total_contributions,
                        earnings=0
                        )
            self.send_message('final_values', agent, asdict(temp_info))
        
        if self.round < 5:
            for agent in agents:
                temp = {"message": "Next round starts in 5 seconds"}
                self.send_message('display_message', agent, temp)

            reminder_msg = Message()
            reminder_msg.set_sender(self.myAddress)
            reminder_msg.set_directive("start_period")
            self.reminder(seconds_to_reminder = 5,
                        message = reminder_msg)
        else:
            for agent in agents:
                temp = {"message": "Experiment has concluded"}
                self.send_message('display_message', agent, temp)



        # self.send_message('start_period', self.myAddress, {})

    @directive_decorator("start_period")
    def start_period(self, message: Message):
        self.round += 1
        log_it = f"<I> start-period :: round = {self.round}"
        # self.log_message(log_it, target = self.short_name)
        # initialize period data
        self.num_contributions_received = 0
        self.contributions = []
        self.group_contribution = 0
        # send messages to agents to make contribution
        agents = self.address_book.get_agents()
        agent_round_start_data = {}
        agent_round_start_data["message"] = "Round has begun!"
        agent_round_start_data["beginning_cash"] = 100
        agent_round_start_data["round"] = self.round
        
        for agent in agents:
            self.send_message('contribute', agent, agent_round_start_data)
        
        reminder_msg = Message()
        reminder_msg.set_sender(self.myAddress)
        reminder_msg.set_directive("end_period")
        self.reminder(seconds_to_reminder = self.period_length,
                        message = reminder_msg)


    def update_agents_on_pool(self):
        update= {}
        update["total_contributions"] = self.pool.total_contributions
        update["participants_count"] = self.pool.participant_count()
        agents = self.address_book.get_agents()
        for agent in agents:
            self.send_message('pool_update', agent, update)


    @directive_decorator("contribution")
    def contribution(self, message: Message):
        payload = message.get_payload()
        contributor = payload[0]
        contribution = payload[1]
        
        self.pool.contribute(contributor, contribution)

        self.update_agents_on_pool()



        # payload = (self.short_name, contribution)
        # self.log_message(f"<I> contribution :: payloads = {payload} {self.num_contributions_received}", target=self.short_name)
        

    @directive_decorator("old_contribution")
    def old_contribution(self, message: Message):
        self.num_contributions_received += 1
        payload = message.get_payload()
        # payload = (self.short_name, contribution)
        # self.log_message(f"<I> contribution :: payloads = {payload} {self.num_contributions_received}", target=self.short_name)
        self.contributions.append(payload)
        if self.num_contributions_received == self.num_agents:
            self.process_contributions()


    def process_contributions(self):
        contribution = dict((c[0],c[1]) for c in self.contributions)
        for i in contribution.items():
            self.log_message(f"<I> the contribution of {i[0]} is {i[1]}")
        group_contribution = sum([c[1] for c in self.contributions])
        group_earning = group_contribution * self.group_rate
        log_it =  f"<I> p_c :: group_c = {group_contribution}"
        log_it += f" group_e = {group_earning}"
        # self.log_message(log_it, target = self.short_name)
        private_earning=dict((c[0],self.endowment-c[1]) for c in self.contributions)
        # self.log_message(f"pe = {private_earning}", target = self.short_name)
        for a_name, p_earn in private_earning.items():
            self.log_message(f"the private_earning of {a_name} is {p_earn}")
        total_earning = dict((c[0],self.endowment-c[1]+group_earning/self.num_agents) for c in self.contributions)
        # for a_name, t_earn in total_earning.items():
        #     self.log_message(f"<I> the total_earning of {a_name} is {t_earn}", target = self.short_name)
        agents = self.address_book.get_agents()
        self.log_message(f"<I> process_contributions :: agents = {agents}")
        for agent in agents:
            information=[contribution[agent], private_earning[agent], group_contribution, group_earning, total_earning[agent]]
            self.send_message('results', agent, information)
            self.log_data((agent, contribution[agent], private_earning[agent], group_earning, total_earning[agent]))
        self.send_message('next_round',"vcm_environment.VCMEnvironment")