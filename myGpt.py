from openai import OpenAI
client = OpenAI()
from typing_extensions import override
from openai import AssistantEventHandler
import json

# Async event handling
class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)
 
# Assistant Functions
# Initialize Assistant
def initialize_assistant(agent):
    try:
        if agent.tools is not None:
            agent.assistant = client.beta.assistants.create(
                name=agent.name,
                instructions=agent.system_prompt,
                tools=agent.tools,
                model=agent.model,
                )
        else:
            agent.assistant = client.beta.assistants.create(
                name=agent.name,
                instructions=agent.system_prompt,
                model=agent.model,
            )
        print("Checkpoint: assistant initialized")
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize agent: Caught {e.__class__.__name__}: {e}")

# Initialize Thread
def initialize_thread(agent):
    try:
        agent.thread = client.beta.threads.create()
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize thread: Caught {e.__class__.__name__}: {e}")

# Go through messages and print content
def print_agent_messages(messages):
    for full_msg in reversed(json.loads(messages.json())['data']):
        role = full_msg['role']
        for message in full_msg['content']:
            if message['type']=='text':
                print(role+': '+message['text']['value'])

# Agent class
class Agent:
    def __init__(self,system_prompt="You are a helpful chat based assistant",
                 name = 'AgentGpt',
                 model = 'gpt-4o',
                 tools = None):
        self.system_prompt = system_prompt
        self.name = name
        self.model = model
        self.tools = tools
        initialize_assistant(self)
        self.thread = None
        self.messages=[]
    # chat method
    def chat(self,msg,additiona_prompt = "remember to double check your work",images=None,files=None,stream=False):
        if self.thread is None:
            initialize_thread(self)
        
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=msg
            )
        
        self.messages.append(message)

        if stream==False:
            self.run = client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=additiona_prompt)
            if self.run.status == 'completed': 
                self.messages = client.beta.threads.messages.list(
                    thread_id=self.thread.id
                )
                print_agent_messages(self.messages)
            else:
                print(self.run.status)
        else:
            # Then, we use the `stream` SDK helper 
            # with the `EventHandler` class to create the Run 
            # and stream the response.
            
            with client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=additiona_prompt,
                event_handler=EventHandler(),
                ) as stream:
                stream.until_done()
        



