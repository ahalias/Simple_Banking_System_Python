import random
import sqlite3

con = sqlite3.connect('card.s3db')


def create_db():
    con.cursor().execute("""CREATE TABLE IF NOT EXISTS card(id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);""").close()
    con.commit()


class Card:
    def __init__(self):
        iin = '400000'
        generate_num = iin + ''.join([str(random.randint(0, 9)) for _ in range(10)])
        self.card_number = str(''.join(generate_num[:-1]) + Card.gen_checksum(generate_num))
        self.pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        cursor = con.cursor()
        self.id = cursor.execute('SELECT MAX(id) + 1 FROM card').fetchone()
        cursor.close()
        self.status = 'not_logged'

    @staticmethod
    def gen_checksum(num):
        mult = [int(x) * 2 if (index + 1) % 2 != 0 else int(x) for index, x in enumerate([*num[:-1]])]
        sum_ = sum([(x - 9) if x > 9 else x for x in mult]) % 10
        checksum = 10 - sum_ if sum_ != 0 else 0
        return str(checksum)

    def get_card_number(self):
        return self.card_number

    def get_pin(self):
        return self.pin

    def get_id(self):
        return self.id[0]

    def run(self):
        while True:
            Card.menu(self)
            Card.process_menu(self)

    def menu(self):
        login_menu = '1. Create an account', '2. Log into account', '0. Exit'
        logged_menu = '1. Balance', '2. Add income', '3. Do transfer', '4. Close account', '5. Log out', '0. Exit'
        if self.status == 'not_logged':
            print(*login_menu, sep='\n')
        else:
            print(*logged_menu, sep='\n')

    def process_menu(self):
        choice = input()
        if self.status == 'not_logged':
            if choice == "1":
                Card.create_card()
            elif choice == '2':
                Card.log_in(self)
            elif choice == '0':
                exit()
        if self.status != 'not_logged':
            if choice == '1':
                print(con.cursor().execute('SELECT balance FROM card WHERE number = ?', self.status).close())
                con.commit()

            if choice == '2':
                income = int(input('Enter income:'))
                con.cursor().execute('UPDATE card SET balance = balance + ? WHERE number = ?', (income, self.status)).close()
                con.commit()
                print('Income was added!')

            if choice == '3':
                transfer_to_card = input('Transfer\nEnter card number:')
                cursor = con.cursor()
                num_fetch = cursor.execute('SELECT number FROM card WHERE number = ?', (transfer_to_card,)).fetchone()
                cursor.close()
                if Card.gen_checksum(transfer_to_card) != transfer_to_card[-1]:
                    print('Probably you made a mistake in the card number. Please try again!')
                elif not num_fetch:
                    print('Such a card does not exist.')
                else:
                    sum_of_transfer = int(input('Enter how much money you want to transfer:'))
                    check_balance = con.cursor().execute('SELECT balance FROM card WHERE number = ? and balance > ?', (self.status, sum_of_transfer)).fetchone()
                    cursor.close()
                    if not check_balance:
                        print('Not enough money!')
                    else:
                        con.cursor().execute("UPDATE card SET balance = balance - ? WHERE number = ?", (sum_of_transfer, self.status))
                        con.cursor().execute("UPDATE card SET balance = balance + ? WHERE number = ?", (sum_of_transfer, transfer_to_card)).close()
                        con.commit()
                        print('Success!')

            if choice == '4':
                con.cursor().execute('DELETE FROM card WHERE number = ?', (self.status,)).close()
                con.commit()
                print('The account has been closed!')
            if choice == '5':
                Card.log_out(self)
            if choice == '0':
                exit()

    @staticmethod
    def create_card():
        card = Card()
        con.cursor().execute('INSERT INTO card(id, number, pin) VALUES (?, ?, ?)', (card.get_id(), card.get_card_number(), card.get_pin())).close()
        con.commit()
        print(f'Your card has been created\nYour card number: \n{card.card_number}\nYour card PIN: \n{card.pin}')

    def log_in(self):
        if self.status == "not_logged":
            check_num = input('Enter your card number:')
            check_pin = input('Enter your PIN:')
            cursor = con.cursor()
            num_fetch = cursor.execute('SELECT number, pin FROM card WHERE number = ? AND pin = ?', (check_num, check_pin)).fetchall()
            cursor.close()
            try:
                if num_fetch:
                    self.status = str(check_num)
                    print('You have successfully logged in!')
                    Card.run(self)
                else:
                    print('Wrong PIN!')
            except KeyError:
                print("Wrong card number!")

    def log_out(self):
        self.status = 'not_logged'


create_db()
Card().run()
con.close()
