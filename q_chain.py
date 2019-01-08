import sublime
import sublime_plugin
import threading
import re

#chain command and parse output to next command inputs
#example
#view.run_command("q_chain", {"chain": ["q_select_text", "q_send", "q_out_panel"]})
#view.run_command("q_chain", {"input": "til 10", "chain": ["q_send", "q_out_panel"]})
#view.run_command("q_chain", {"input": "test output", "chain": ["q_out_panel"]})
class QChainCommand(sublime_plugin.TextCommand):

    def do(self, edit, input=None):
        if input is not None:
            return input
        else:
            return "start"  #to start chain

    def run(self, edit, input=None, chain=None):
        if (len(chain) > 0 and re.search("QSend.*", self.__class__.__name__)):
            print("Spawning thread for q send action "+self.__class__.__name__)
            t = QChainCommandThread(self, edit, input, chain)
            t.start()
        else:
            self.exec_chain(edit, input, chain)

    def exec_chain(self, edit, input, chain):
        output = self.do(edit, input)
        if output is None:
            print('break chain because output is none')
            return

        if chain is not None:
            if len(chain) > 0:
                print('\tchain ' + str(len(chain)) + ' command ' + chain[0] + '...')
                self.view.run_command(chain[0], {"input": output, "chain": chain[1:]})
            else:
                print('finished chain')
        else:
            #no chain - just print output to console
            print(output)

class QChainCommandThread(threading.Thread):
    def __init__(self, cmd, edit, input, chain):
        print("thread init")
        self.cmd = cmd
        self.edit = edit
        self.input = input
        self.chain = chain
        threading.Thread.__init__(self)
        
    def run(self):
        self.cmd.exec_chain(self.edit, self.input, self.chain)