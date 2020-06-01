from sqlalchemy import create_engine
import logging
import pandas as pd
import random
import os

# SQL ENGINE SETTINGS
USER = os.environ.get('DB_USER')
PASS = os.environ.get('DB_PASS')
engine = create_engine(
    f'postgresql://{USER}:{PASS}@localhost:5432/turk_eng_dict')

# LOGGING SETTINGS
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(message)s')
file_handler = logging.FileHandler('lesson_results.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# MAIN PROGRAM
class flash_turk():
    def __init__(self):
        # READ IN DATA
        self.df = pd.read_sql('vocab', engine, index_col='id')

        # GROUP DATA BY TYPE
        self.data_groups = self.df.groupby('type')
        self.group_type = ['noun', 'verb', 'adjective', 'adverb', 'phrase', 'test']

        self.welcome_prompt()

    # ENTRY PROMPT
    def welcome_prompt(self):
        self.name = input("What is your name? ")
        print(f'\nWelcome {self.name}!')
        print(f'''
Types of words:
    0. Nouns ({len(self.data_groups.groups[self.group_type[0]])} words)
    1. Verbs ({len(self.data_groups.groups[self.group_type[1]])} words)
    2. Adjectives ({len(self.data_groups.groups[self.group_type[2]])} words)
    3. Adverbs ({len(self.data_groups.groups[self.group_type[3]])} words)
    4. Phrases ({len(self.data_groups.groups[self.group_type[4]])} phrases)

    q. Quit
''')

        self.choice = input('Pick a type (0, 1, 2, 3, 4): ')

        # ======= VERIFY CHOICE ======= #

        # QUIT
        if self.choice.lower() == 'q':
            self.quitter()

        # CHECK SELECTION
        else:
            try:
                if int(self.choice) not in [0, 1, 2, 3, 4, 5]:
                    print('Not a valid number!')
                    self.welcome_prompt()
                else:
                    self.choice = int(self.choice)
                    self.packet_picker()
            except ValueError:
                print('Not a valid answer!')
                self.welcome_prompt()

        # ============================== #

    # SELECT A PACKET (For list greater than 100)
    def packet_picker(self):
        if int(self.choice) > 2:
            self.p_choice = None
            self.packet = \
                self.data_groups.groups[self.group_type[self.choice]]
            self.list_maker()
        else:
            print(f'\nAvailable packets for the \
{self.group_type[self.choice]} group')
            print('''
Packets:
    1. Packet 1
    2. Packet 2
    3. Packet 3
    4. Packet 4

    m. Main Menu
    q. Quit
''')

            self.p_choice = input('Pick a Packet (1, 2, 3, 4): ')

            # ======= VERIFY CHOICE ======= #

            # MENU
            if self.p_choice.lower() == 'm':
                self.welcome_prompt()

            # QUIT
            elif self.p_choice.lower() == 'q':
                self.quitter()

            # CHECK SELECTION
            else:
                try:
                    if int(self.p_choice) not in [1, 2, 3, 4]:
                        print('Not a valid number!')
                        self.packet_picker()
                    else:
                        self.p_choice = int(self.p_choice)
                        self.packet_slicer()
                except ValueError:
                    print('Not a valid answer!')
                    self.packet_picker()

            # ============================== #

    # SLICE LIST ACCORDING TO PACKET SELECTION
    def packet_slicer(self):
        self.big_group = \
            self.data_groups.groups[self.group_type[self.choice]]
        self.slices = int(len(self.big_group) / 4)
        self.packet = \
            self.big_group[((self.p_choice - 1) * self.slices):
                           (self.p_choice * self.slices)]
        self.list_maker()

    # BUILD TURKISH:ENGLISH DICTIONARY
    def list_maker(self):

        self.remains = {}  # FOR TURKISH:ENGLISH DICTIONARY
        self.correct = []   # FOR CORRECT TOTALS
        self.incorrect = []  # FOR INCORRECT TOTALS

        for i in self.packet:
            self.remains[self.df.loc[i]["turkish"]] = self.df.loc[i]["english"]
        self.next()

    # QUIZ
    def quiz(self):

        # EXIT OPTIONS
        print('''
Exit options:
m. Main Menu
q. Quit
''')

        # STATUS BAR
        print(f"\n{len(self.correct)} correct. {len(self.incorrect)} incorrect. \
            {len(self.remains)} remaining...")

        # QUESTION GENERATOR
        self.words = random.choice(list(self.remains.items()))
        self.ans = input(
            f"\nWhat is the english translation for '{self.words[0]}'?\n")

        self.check()

    # CHECK ANSWER
    def check(self):
        # MENU
        if self.ans.lower() == 'm':
            os.system('clear')
            self.welcome_prompt()

        # QUIT
        elif self.ans.lower() == 'q':
            os.system('clear')
            self.quitter()

        # CORRECT ANSWER
        elif self.ans.lower() == self.words[1]:
            print('\nCorrect!')
            self.correct.append(self.words)

            # REMOVE WORDS FROM DICT
            self.remains.pop(self.words[0])

            input("\n\nPress enter to continue...")
            self.next()

        # INCORRECT ANSWER
        else:
            print(f'\nIncorrect!\nCorrect Answer: {self.words[1]}')

            # ADD WORD TO INCORRECT IF NON-EXIST
            self.counter = self.incorrect.count(self.words)
            if self.counter == 0:
                self.incorrect.append(self.words)

            input("\n\nPress enter to continue...")
            self.next()

    # GENERATE NEXT WINDOW
    def next(self):
        os.system('clear')
        if len(self.remains) != 0:
            self.quiz()
        else:
            self.end_round()

    # RESULTS WINDOW
    def end_round(self):

        # RESULTS INFO
        print(f'''
Results:
{len(self.incorrect)} incorrect.''')

        # INCORRECT WORDS
        print(''.join(
            "\n{0}".format(i[0] + " = " + i[1]) for i in self.incorrect))

        # LOG RESULTS
        logger.info(
            f' Name: {self.name}, Group: {self.group_type[self.choice]}, \
Packet: {self.p_choice}, \
Incorrect: {len(self.incorrect)}')

        # EXIT OPTIONS
        print('''
Where to next?
m. Main Menu
q. Quit
''')

        self.ans = input()
        self.check()

    def quitter(self):
        pass


# GROUND ZERO
if __name__ == '__main__':
    flash_turk()
