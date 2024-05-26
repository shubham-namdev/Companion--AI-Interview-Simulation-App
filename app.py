import time
from utils import *
import json
import nltk
from nltk.corpus import words
import os
import keyboard
import ai
import datetime
import random

class Data:

    def __init__(self) -> None:
        self.datafile = "data.json"
    
    def get_topics(self):
        with open(self.datafile, 'r') as f:
            data = json.load(f)
        topics = []
        for k in data["data"]:
            topics.append(k['topic'].lower())
        return topics
    
    def add_topic(self, topic : dict) -> None:
        if topic["topic"].lower() in self.get_topics():
            with open(self.datafile, 'r') as f:
                data = json.load(f)
            for k in data["data"]:
                if k["topic"] == topic["topic"].lower():
                    k["questions"] = topic["questions"]
            with open(self.datafile, 'w') as f:
                json.dump(data, f, indent=4)
        else:    
            with open(self.datafile, 'r') as f:
                data = json.load(f)
            data["data"].append(topic)
            with open(self.datafile, 'w') as f:
                json.dump(data, f, indent=4)
    
    def get_questions(self, topic:str) -> list[str]:
        with open(self.datafile, 'r') as f:
            data = json.load(f)
        for d in data["data"] : 
            if d["topic"] == topic:
                return d["questions"]
             
class App:

    def __init__(self) -> None:
        self.data = Data()
        self.configfile = 'conf.json'
        with open(self.configfile, 'r') as f:
            self.config = json.load(f)

        if self.config["dependencies"] == "False":
            try:
                print_message("Installing Dependencies (python-libraries) :", color='green')
                os.system("pip install -r requirements.txt")
                self.change_config("dependencies", "True")
            except Exception as e:
                print_message(f"Error : {e} \nDependencies were unable to install!", color='red')
                print_message(f"Exiting...", color='red')
                time.sleep(1)
                exit()


        if self.config["nltk_words"] == "False" :
            print_message("Installing Dependencies (NLTK) :", color='green')
            nltk.download('words')
            self.change_config("nltk_words", "True")

        if self.config["mistral_ai"] == "False" :
            print_message("Pulling Mistral AI :", color='green')
            try : 
                os.system("ollama pull mistral")
                self.change_config("mistral_ai", "True")
            except Exception as e:
                print_message(f"Error : {e} \nMistral AI cannot be pulled!", color='red')

        self.run = True

        while self.run:
            # self.interview_page("temp")
            self.home_page()
            clear()
    
    def reset(self) -> None:
        self.config["nltk_words"] = "False"
        self.config["mistral_ai"] = "False"
        self.config["dependencies"] = "False"

        with open(self.configfile, 'w') as f:
            json.dump(self.config, f, indent=4)
        
        with open(self.configfile, 'r') as f:
            self.config = json.load(f)
        print_message("Reset Complete!", color='green')
        print_message("Please Restart the app!", color='green')
        print_message("Exiting...", color='red')
        time.sleep(2)   


    def change_config(self, conf : str, state :str) -> None:
        self.config[conf] = state

        with open(self.configfile, 'w') as f:
            json.dump(self.config, f, indent=4)
        
        with open(self.configfile, 'r') as f:
            self.config = json.load(f)


    def print_header(self, loc : str, text : str = None) : 
        commands = {
            "home" :  lambda : print_message("🚀 Welcome to \"Companion\" - Your Interview Partner 🚀", color="blue", centered=True),
            "new_test" : lambda : print_message("⭐ New Test ⭐", color="blue", centered=True),
            "test" : lambda : print_message("⭐ Available Tests ⭐", color='blue', centered=True),
            "inst" : lambda : print_message("🔴 Instructions 🔴", color='red',centered=True),
            "interview" : lambda : print_message("⭐ Give Your Best! ⭐",color="blue", centered=True),
            "question_page" : lambda : print_message(f"Interview : {text}", color='red', centered=True),
            "report" : lambda : print_message(f"Report : {text}", color='blue', centered=True)
        }
        clear()
        print_br()
        commands[loc]()
        print_br()


    def home_page(self):
        self.print_header("home")
        
        print_message("⭐  Sky's the Limit! ⭐", color='cyan', centered=True)
        
        print_message("What should we prepare today : ", color='orange')
        
        ch = input("""1. Choose from existing tests.
2. Start New Test
3. Reset Settings
>> """)
        match ch:
            case '1' : 
                self.test_page()
            case '2' : 
                self.new_test_page()
            case '3' : 
                self.reset()
                self.run = False
            case _ :
                print_message("Invalid Choice!", color='red')
                time.sleep(1)
                return


    def test_page(self):
        self.print_header("test")

        topics = self.data.get_topics()
        
        if topics:
            print_message("Available Tests : ", color="orange")
            for i, t in enumerate(topics):
                print(f"{i+1} : {t.title()}")

            print_message("Please select the topic for Today's Interview (numbers): ", color="orange")
            print_message("Enter \"new\" to create a new test ", color="magenta")
            ch = ""
            while not ch:
                try : 
                    ch = input(">> ")
                    if ch.lower() == "new":
                        self.new_test_page()

                    elif int(ch) > len(topics):
                        print_message("Invalid Choice!", color="red")
                        ch = ""
                        time.sleep(1)
                    else:
                        print_message(f"Starting Test {topics[int(ch)-1].title()} ...", color="green")
                        time.sleep(1)
                        self.interview_page(topic=topics[int(ch)-1], presaved=True)
                except ValueError:
                    print_message("Invalid Choice!", color="red")
                    time.sleep(1)
                    ch = ""
        
        else:
            print_message("No Tests Available ! ", color="red")
            print_message("Do you want to create a new test ? (y : yes)", color="orange")
            ch = input(">> ")
            if ch.lower() == 'y':
                print_message("Redirecting to New Test Page >>", color="green")
                time.sleep(1)
                self.new_test_page()
            else:
                print_message("Going Back...", color="green")
                time.sleep(1)
                
                
    
    def new_test_page(self):
        self.topic = ""
        self.diff = ""
        self.use_ai = ""
        self.questions = []

        while not self.topic or not self.diff or not self.use_ai :
            self.print_header("new_test")
            if self.topic:
                print_message("Topic : ", color='orange', end = "")
                print_message(f"{self.topic}") 

            if self.diff:
                print_message("Difficuty : ", color='orange', end = "")
                print_message(f"{self.diff}")

            if self.use_ai:
                print_message("AI : ", color='orange', end = "")
                print_message(f"{self.use_ai}")

            if not self.topic : 
                
                print_message("Let's create a new test 🚀", color='orange')

                print_message("Enter Topic :", color="orange")
                self.topic = input(">> ")
                if self.topic.lower() in self.data.get_topics():
                    print_message(f"Topic {self.topic} is already in database!", color="red")
                    print_message(f"Do you want to overwrite it ?", color="orange")
                    ch = input("(y/n) >> ")
                    if ch.lower() != 'y':
                        self.topic = ""
                elif not self.topic:
                    print_message("Topic cannot be empty!", color='red')
                    time.sleep(1)
            
            elif not self.diff:
                print_message("Please Choose Difficulty Level :", color="orange")
                ch = input("""1. Easy
2. Moderate
3. Hard
>> """)
                match ch :
                    case '1' : 
                        self.diff = "Easy"
                    case '2' : 
                        self.diff = "Moderate"
                    case '3' : 
                        self.diff = "Hard"
                    case _ :
                        print_message("Invalid Choice !", color='red')
                        time.sleep(1)

            elif not self.use_ai:
                print_message("Do you wanna use AI to generate questions ?", color="orange")
                self.use_ai = input("(y/n) >> ")

                if self.use_ai.lower() == 'y':
                    self.use_ai = "Yes"
                elif self.use_ai.lower() == 'n':
                    self.use_ai = "No"
                else :
                    print_message("Invalid Choice!", color='red')
                    self.use_ai = ""
                    time.sleep(1)
                    
        if self.use_ai.lower() == 'yes':
            self.count = ""
            while not self.count:
                self.print_header("new_test")
                print_message("Topic : ", color='orange', end = "")
                print_message(f"{self.topic}")
                print_message("Difficuty : ", color='orange', end = "")
                print_message(f"{self.diff}")
                print_message("AI : ", color='orange', end = "")
                print_message(f"{self.use_ai}")

                print_message("Enter the count of questions :", color="orange")
                self.count = input(">> ")

                if not self.count.isnumeric():
                    print_message("Invalid Number!", color='red')
                    time.sleep(1)
                    self.count = ""
            
            print_message("Please Wait...AI is generating Questions.", color="green")

            while len(self.questions) != int(self.count):
                self.questions = ai.prompt(topic=self.topic, difficulty=self.diff, count=self.count)
        
            print_message("Questions Generated Successfully!", color="green")
            time.sleep(1)
        else:
            print_message("Enter Questions: ", color='orange')
            print_message("(stop) to exit", color='magenta')
            c = 1
            while True:   
                q = input(f"{c} >> ")
                if q.lower() == 'stop':
                    break
                else:
                    self.questions.append(q)
                c += 1
            
       
        while True:
            
            self.print_header("new_test")
            print_message("Do you want to preview the Questions?", color="orange")
            ch = input("(y/n) >> ")
            if ch.lower() == 'y':
                print_message("Topic : ", color='orange', end = "")
                print_message(f"{self.topic}")

                print("Questions : ",)

                for i, q in enumerate(self.questions):
                    print(f"{i+1} : {q}")
                
                print_message("NOTE: ", color="red", end="")
                print_message("Please regenerate the questions if you notice any anomaly.")
            
                print_message("Do you want to Regenerate the questions?", color="orange")
                regen = input("(y/n) >> ")
                if regen.lower() == 'y':
                    self.count = ""
                    while not self.count:
                        print_message("Enter the count of questions :", color="orange")
                        self.count = input(">> ")

                        if not self.count.isnumeric():
                            print_message("Invalid Number!", color='red')
                            time.sleep(1)
                            self.count = ""
                    
                    print_message("Please Wait...AI is generating Questions.", color="green")
                    self.questions = []
                    while len(self.questions) != int(self.count):
                        self.questions = ai.prompt(topic=self.topic, difficulty=self.diff, count=self.count)
                    print_message("Questions Generated Successfully!", color="green")
                elif regen.lower() == 'n':
                    break
                else:
                    print_message("Invalid response!", color='red')
                    time.sleep(1)

            else:
                break    
                

        ch = ""
        while not ch:
            self.print_header("new_test")
            print_message("Do you want to save the test or start the interview ?")
            print_message("save : Save the test\nstart : Start the Interview\nexit : Go back to Home Page", color='magenta')
            ch = input("(save/start) >> ")

            if ch.lower() == "save":
                template = {
                    "topic" : self.topic.lower(),
                    "questions" : self.questions
                }
                self.data.add_topic(template)
                self.data = Data()
                return    
            elif ch.lower() == "start":
                self.interview_page(topic = self.topic, questions=self.questions, difficulty=self.diff)
                return
            elif ch.lower() == "exit":
                return
            else:
                print_message("Invalid Choice!", color='red')
                ch = ""
                time.sleep(1) 

    def generate_model_answers(self, questions : list[str], indices :list[int] = [], All=False):
        
        qa_map = dict()

        if All :
            indices = [x for x in range(len(questions))]
        
        k = 1
        with open("temp.txt", "w"):
            pass

        for i in indices:
            print_message(f"Generating response : {k}/{len(indices)}", color='green')
            response = ai.prompt(questions[i], isIndep=True)
           
            with open('temp.txt', 'a') as f:
                f.write(f"Question : {questions[i]}\n")

                f.write(f"Answer : {response}")
                f.write("\n\n")
            qa_map[questions[i]] = response
            k += 1

        for k, v in qa_map.items():
            print_message(f"Que : {k}", color='orange')
            print_message(f"Ans : {v}", color='white')
            print("\n\n")
        
        print_message("Do you want to save the content to a text file?", color='magenta')
        ch = input("(y/n)>> ")
        if ch.lower() == 'y' :
            name = input("Enter the name for the file : ")

            with open("temp.txt", "r") as input_file:
                content = input_file.read()

            with open(f"{name}.txt", "w") as output_file:
                output_file.write(content)

            with open("temp.txt", "w"):
                pass

            print_message(f"Content Saved to : {name}.txt", color='green')
            time.sleep(1.5)

    def print_instructions(self) -> None:
        self.print_header("inst")  
        print_message("Please read all the instructions carefully before proceeding!", color='red')
        print("1. This is a Mock Interview simulated using AI. It will help you increase your fluency and confidence while speaking.")
        print("2. All the questions are either generated using AI or taken from the saved test.")
        print("3. Please use the Right Arrow key to move on to the next question.")
        print("4. If there is any question that is irrelevant, press the Down Arrow key to discard it.")
        print("5. If there is any question that you could not answer, press the Up Arrow key to mark it.")

        print_message("NOTE: ", color='red', end="")
        print("This is an Interview Simulation aimed to help you prepare for the real one.\nIn order to take full advantage, please make sure you are honest while answering the questions and prepare your environment accordingly.")

        print_message("Press Right Arrow Key to continue -->", color='magenta')
        keyboard.wait("right")

    def interview_page(self, topic :str, questions :list[str] = [], difficulty :str = "Moderate", presaved=False) -> None:
        
        markedQs = []
        discardedQs = []
        unsolvedQs = []

        def markUnsolved(event):
            if c not in markedQs: 
                markedQs.append(c)
                unsolvedQs.append(q)
                print_message("Questions marked as Unsolved", color='green')
                time.sleep(1)
                

        def markDiscarded(event):
            if c not in discardedQs: 
                discardedQs.append(c)
                print_message("Question Discarded!", color='green')

        def print_report(unsolved=None) -> None:
            def print_info():
                print_message("Topic : ", color='orange', end = "")
                print_message(f"{topic.title()}")

                print_message("Difficulty : ", color='orange', end = "")
                print_message(f"{difficulty}")

                print_message("Total Questions : ", color='orange', end = "")
                print_message(f"{len(questions)}")

                print_message("Questions Answered: ", color='orange', end = "")
                print_message(f"{len(questions) - len(set(markedQs + discardedQs))}")

                print_message("Questions Unanswered: ", color='orange', end = "")
                print_message(f"{len(markedQs)}")
                
                if unsolved:
                    for i,u in enumerate(unsolved):
                        print_message(f"Q{i+1}: ", color='red', end = "")
                        print(u)

                print_message("Questions Discarded: ", color='orange', end = "")
                print_message(f"{len(discardedQs)}")

                


            ch = ""
            while not ch:
                self.print_header("report", text = f"{topic} - ({datetime.date.today()})")
                print_info()
                print_message("Do you want to generate Model Answers for the questions?", color='magenta')
                ch = input("(y/n)>> ")
                if ch.lower() == 'y' :
                    c = ""
                    while not c : 
                        self.print_header("report", text = f"{topic} - ({datetime.date.today()})")
                        print_info()
                        print_message("Generate model answers for :", color='blue')
                        c = input("""1. All Questions (including discarded Qs)
2. All Questions (excluding discarded Qs)
3. Only Marked (unanswered) Qs                                                       
>> """)
                        match c :
                            case '1':
                                self.generate_model_answers(questions=questions, All=True)
                            case '2':
                                indices = [x for x in range(len(questions)) if x not in discardedQs]
                                self.generate_model_answers(questions=questions, indices=indices)
                            case '3' :
                                self.generate_model_answers(questions=questions, indices=markedQs)
                            case _ :
                                print_message("Invalid Choice!", color='red')
                                time.sleep(1)
                                c = ""

                elif ch.lower() == 'n':
                    print_message("Going back to Home Page...", color='green')
                    time.sleep(1)
                else:
                    print_message("Invalid Choice!", color='red')
                    time.sleep(1)
                    ch = ""
            
  
        self.print_instructions()
        self.print_header("interview")
        time.sleep(1)

        if presaved :
            self.data = Data()
            questions = self.data.get_questions(topic=topic)

        c = 0   

        random.shuffle(questions)

        for q in questions:
            self.print_header("question_page", text=topic.title())
            print_message(f"{c+1} : {q}", color='orange', centered=True)
            for _ in range(10):
                print()
            print_message("Right Arrow : Next Question   ", color='magenta', centered=True)
            print_message("Up Arrow    : Mark as Unsolved",color='magenta', centered=True)
            print_message("Down Arrow  : Discard Question",color='magenta', centered=True)

            talk(q)

            keyboard.on_press_key('up', markUnsolved)
            keyboard.on_press_key('down',markDiscarded)
            keyboard.wait('right')
            
            c += 1

            keyboard.unhook_all()


        choice = ""

        while not choice:
            self.print_header("question_page", text=topic)

            print_message("Interview Ended :)", color = 'green', centered=True)
            
            print_message("Do you want to save the test?", color = 'orange')
            choice = input("(y/n)>> ")

            if choice.lower() == 'y':
                template = {
                    "topic" : topic.lower(),
                    "questions" : questions
                }
                self.data.add_topic(template)
                self.data = Data()
                print_message(f"Test Saves as {topic}.", color='green')

            elif choice.lower() == 'n':
                pass
            else:
                print_message("Invalud Choice!", color='red')    
                time.sleep(1)
                choice = ""

        print_message("Generating Report...", color='green')
        time.sleep(1)
        print_report(unsolved=unsolvedQs)
        return

  


if __name__ == "__main__" :
    app = App()

