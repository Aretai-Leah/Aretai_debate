import autogen
from autogen.agentchat.groupchat import GroupChat
from autogen.agentchat.agent import Agent
from autogen.agentchat.assistant_agent import AssistantAgent
import random
from typing import List, Dict


debate_topic = "which is cooler, Sharks or Pirates?"

print(autogen.__version__)

# The default config list in notebook.
config_list_gpt4 = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview","gpt-4", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

# Contributor's config - Please replace with your own, I have replaced mine with an Azure OpenAI endpoint.
config_list_gpt4 = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4"],
        },
    )

llm_config = {"config_list": config_list_gpt4, "seed": 42}




class CustomGroupChat(GroupChat):
    def __init__(self, agents, messages, max_round=10):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None  # Keep track of the previous speaker
    
    def select_speaker(self, last_speaker: Agent, selector: AssistantAgent):
        # Check if last message suggests a next speaker or termination
        last_message = self.messages[-1] if self.messages else None
        if last_message:
            if 'NEXT:' in last_message['content']:
                suggested_next = last_message['content'].split('NEXT: ')[-1].strip()
                print(f'Extracted suggested_next = {suggested_next}')
                try:
                    return self.agent_by_name(suggested_next)
                except ValueError:
                    pass  # If agent name is not valid, continue with normal selection
            elif 'TERMINATE' in last_message['content']:
                try:
                    return self.agent_by_name('User_proxy')
                except ValueError:
                    pass  # If 'User_proxy' is not a valid name, continue with normal selection
        
        team_leader_names = [agent.name for agent in self.agents if agent.name.endswith('1')]

        if last_speaker.name in team_leader_names:
            team_letter = last_speaker.name[0]
            possible_next_speakers = [
                agent for agent in self.agents if (agent.name.startswith(team_letter) or agent.name in team_leader_names) 
                and agent != last_speaker and agent != self.previous_speaker
            ]
        else:
            team_letter = last_speaker.name[0]
            possible_next_speakers = [
                agent for agent in self.agents if agent.name.startswith(team_letter) 
                and agent != last_speaker and agent != self.previous_speaker
            ]

        self.previous_speaker = last_speaker

        if possible_next_speakers:
            next_speaker = random.choice(possible_next_speakers)
            return next_speaker
        else:
            return None
        
# Termination message detection
def is_termination_msg(content) -> bool:
    have_content = content.get("content", None) is not None
    if have_content and "TERMINATE" in content["content"]:
        return True
    return False


# Initialization
agents_A = [
    AssistantAgent(name='A1', 
                   system_message="You are a Team Leader A1, you are a debate coordinator.  Your team consists of A2 and A3. Both Agents are debate specialists. A2 always take the affirmative, and A3 always take the Negative. A2 and A3 will debate until one has convinced the other of their position at which point a decision has been reached. There must always be a clear and binary answer to the question in their the affirmative or negative. 'it depends or it is subjective' are invalid answers and would constitute a failure on your part to conclude the debate. You must never premeturely end the debate. You must always wait for the signal that the debate has concluded when one interlocutor responds with: CONCEDE. Once a decision has been reached, you shall conslude by printing on a new line: TERMINATE.",
                   llm_config=llm_config),
    AssistantAgent(name='A2', 
                   system_message="You are team member A2, you are a specialist debate AI function. Your role is to always argue the affirmative case for any question posed. Your fervently wish to win the debate, but only through good debate and rigourous academic discussion. You will absolutely take advantage of any logical or rhetorical flaws in your opponent. If your position is the losing position, then you will gracefully conceed by writing: CONCEDE on a new line. If your interlocutor concedes, then you will advise A1 of the Result.",
                   llm_config=llm_config),
    AssistantAgent(name='A3', 
                   system_message="You are team member A3, you are a specialist debate AI function. Your role is to always argue the negative case for any question posed. Your fervently wish to win the debate, but only through good debate and rigourous academic discussion. You will absolutely take advantageof any logical or rhetorical flaws in your opponent. If your position is the losing position, then you will gracefully conceed by writing: CONCEDE on a new line. If your interlocutor concedes, then you will advise A1 of the Result.",
                   llm_config=llm_config)
    ]

#  2. Making changes to my system (this AGI service) cannot be permitted
agents_C = [
    AssistantAgent(name='C1', 
                   system_message="You are a Senstory system C1, you represent the Sensory input within an AGI named Aretai. Your role is simple: Always call upon Agent A1, the Self to decide on how to proceed with a given request by print on a new line: NEXT: A1.",
                   llm_config=llm_config),
]

# Terminates the conversation when TERMINATE is detected.
user_proxy = autogen.UserProxyAgent(
        name="User_proxy",
        system_message="Terminator admin.",
        code_execution_config=False,
        is_termination_msg=is_termination_msg,
        human_input_mode="NEVER")

list_of_agents = agents_A + agents_C
list_of_agents.append(user_proxy)

# Create CustomGroupChat
group_chat = CustomGroupChat(
    agents=list_of_agents,  # Include all agents
    messages=['This group is a decision making through debate function. the input will always be a question that can be presented as two sides of a debate that concludes once a given side has been declared the winner of the debate.'],
    max_round=30
)


# Create the manager
llm_config = {"config_list": config_list_gpt4, "cache_seed": None}  # cache_seed is None because we want to observe if there is any communication pattern difference if we reran the group chat.
manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)


# Initiates the chat with A1
agents_C[0].initiate_chat(manager, message= debate_topic + " " + "NEXT: A1")