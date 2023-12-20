# Aretai_debate
This is a debate function using ms autogen

This is a relatively simple Autogen project, consisting of a single file. Fair warning, I'm not a great developer :/

This uses heirarchical agent flow to pass to specific agents and separate out the groups into a cognition team and executive function team. 
https://github.com/microsoft/autogen/blob/main/notebook/agentchat_hierarchy_flow_using_select_speaker.ipynb

passing in a debate_topic The two debate agents will argue for and against the premise until they decide one is the winner. The debate topic must be able to be rendered into a binary for/against topic, or else the debate coordinator will reject it (or maybe go off on a tangent). 

