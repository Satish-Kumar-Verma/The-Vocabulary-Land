from mysql import connector as ct
from random import randint
from prettytable import PrettyTable, from_db_cursor
# from prettytable.colortable import ColorTable, Themes
import datetime


def display(column_names, data):
    table = PrettyTable(align='l')
    table.field_names = column_names
    table.add_rows(data)
    print(table)


def mark_word(connection, cursor, word, mark_as):
    try:
        primary_columns = {'bookmark': 'B_Code', 'favourite': 'FN_Code', 'new': 'N_Code', 'known': 'KN_Code'}
        primary_index = {'bookmark': 'B_', 'favourite': 'FN_', 'new': 'N_', 'known': 'KN_'}
        out_param = 0
        result = cursor.callproc(f'check_{mark_as}', [word, out_param])[-1]

        if result == 1:
            cursor.execute(f'SELECT COUNT(*) FROM PJ_Vocab.{mark_as}_word;')
            count = cursor.fetchone()[0] + 1

            cursor.execute(f'SELECT M_Code FROM PJ_Vocab.meaning WHERE Word = "{word}";')
            m_code = cursor.fetchone()[0]

            sql = f'INSERT INTO PJ_Vocab.{mark_as}_word ({primary_columns[mark_as]}, M_Code) VALUE (%s, %s)'
            val = (f'{primary_index[mark_as]}{count}', m_code)
            cursor.execute(sql, val)

            connection.commit()
            print(f'{word} is inserted into {mark_as} words!')
        else:
            print(f"The word '{word}' already exists in the {mark_as} words!")

    except Exception as e:
        print(e)
        connection.rollback()


def show_quiz_history(cursor):
    cursor.execute('SELECT Q_ID, Score, Quiz_Date AS "Quiz Time" FROM PJ_Vocab.Quiz_History ORDER BY Quiz_Date DESC')

    table = from_db_cursor(cursor)
    table.align = 'l'
    print(table)


def read_meaning(cursor, limit=None, sort=False, _display_=False):
    cursor.execute('SHOW COLUMNS FROM PJ_Vocab.meaning;')
    col_names = cursor.fetchall()
    col_names = [cols[0] for cols in col_names][1:]

    if sort:
        if limit is None:
            cursor.execute('SELECT Word, W_Meaning FROM PJ_Vocab.meaning ORDER BY Word ASC;')
        else:
            cursor.execute('SELECT Word, W_Meaning FROM PJ_Vocab.meaning ORDER BY Word ASC LIMIT {limit};')

    else:
        if limit is None:
            cursor.execute(f'SELECT Word, W_Meaning FROM PJ_Vocab.meaning;')

        else:
            cursor.execute(f'SELECT Word, W_Meaning FROM PJ_Vocab.meaning LIMIT {limit};')

    data = cursor.fetchall()

    # table = from_db_cursor(cursor)
    # table.align = 'l'
    # print(table)

    if _display_:
        display(col_names, data)

    return data


def read_marked_data(cursor, mark_as, limit=None, sort=False, _display_=False):
    if limit is None:
        if sort:
            cursor.execute(f'''SELECT Word, W_Meaning FROM PJ_Vocab.meaning WHERE M_Code IN 
                            (SELECT M_Code FROM {mark_as}_word WHERE M_Code != 'N/A') ORDER BY Word ASC;''')

        else:
            cursor.execute(f'''SELECT Word, W_Meaning FROM PJ_Vocab.meaning WHERE M_Code IN 
                                        (SELECT M_Code FROM {mark_as}_word WHERE M_Code != 'N/A');''')

    else:
        if sort:
            cursor.execute(f'''SELECT Word, W_Meaning FROM PJ_Vocab.meaning WHERE M_Code IN 
                                        (SELECT M_Code FROM {mark_as}_word WHERE M_Code != 'N/A') 
                                        ORDER BY Word ASC LIMIT {limit};''')

        else:
            cursor.execute(f'''SELECT Word, W_Meaning FROM PJ_Vocab.meaning WHERE M_Code IN 
                                        (SELECT M_Code FROM {mark_as}_word WHERE M_Code != 'N/A') LIMIT {limit};''')

    data = cursor.fetchall()
    if _display_:
        display(['Word', 'W_Meaning'], data)
    return data


def remove_word(cursor, connection, table, word):
    try:
        table = table + "_word"
        cursor.execute(f"SELECT M_Code FROM PJ_Vocab.meaning WHERE Word='{word}';")
        m_code = cursor.fetchone()[0]

        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute(f"UPDATE PJ_Vocab.{table} SET M_Code='N/A' WHERE M_Code='{m_code}';")

        # print(f"'{word}' is removed from the {table} table!")

        connection.commit()

    except Exception as e:
        print(e)
        connection.rollback()


def transfer_word(cursor, connection, from_tb, to_tb, word, action=None):
    try:

        from_tb = from_tb + "_word"
        to_tb = to_tb + "_word"

        cursor.execute(f"SELECT M_Code FROM PJ_Vocab.meaning WHERE Word='{word}';")

        m_code = cursor.fetchone()[0]

        primary_columns = {'bookmark_word': 'B_Code', 'favourite_word': 'FN_Code',
                           'new_word': 'N_Code', 'known_word': 'KN_Code'}
        primary_index = {'bookmark_word': 'B_', 'favourite_word': 'FN_',
                         'new_word': 'N_', 'known_word': 'KN_'}

        if check_existence(cursor, m_code, from_tb) == 1:

            if check_existence(cursor, m_code, to_tb) == 0:

                if action.lower() == 'move':
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                    cursor.execute(f"UPDATE PJ_Vocab.{from_tb} SET M_Code='N/A' WHERE M_Code='{m_code}';")

                    # print(f"[+] 1 row is removed from {from_tb} table!")

                cursor.execute(f"SELECT COUNT(*) FROM {to_tb};")

                row_count = cursor.fetchone()[0] + 1

                sql = f'INSERT INTO PJ_Vocab.{to_tb} ({primary_columns[to_tb]}, M_Code) VALUE (%s, %s)'
                val = (f'{primary_index[to_tb]}{row_count}', m_code)

                cursor.execute(sql, val)

                connection.commit()

                # print(f"[+] 1 row is inserted into {to_tb} table!")

            # else:
            #     print(f"[-] The data already exists in the {to_tb} table!")

        # else:
        #     print(f'[-] Data is not found in {from_tb} table')

    except Exception as e:
        connection.rollback()
        print(e)


def check_existence(cursor, m_code, table):
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE M_Code='{m_code}';")
    result = cursor.fetchone()

    return result[0]


def insert_word(connection, cursor, no_of_rows=1):
    try:
        for i in range(no_of_rows):
            word = input("Word : ")
            meaning = input("Meaning : ")

            cursor.execute('SELECT COUNT(M_Code) FROM PJ_Vocab.meaning;')
            count = cursor.fetchone()[0] + 1

            sql = 'INSERT INTO PJ_Vocab.meaning (M_Code, Word, W_Meaning) VALUES (%s, %s, %s)'
            val = (f'M_{count}', word, meaning)

            cursor.execute(sql, val)

        connection.commit()
        print(f"{no_of_rows} row(s) inserted!")

    except Exception as e:
        print(e)
        connection.rollback()


def log_quiz_info(connection, cursor, score, q_time):
    try:

        cursor.execute('SELECT COUNT(Q_ID) FROM PJ_Vocab.Quiz_History;')
        count = cursor.fetchone()[0] + 1

        sql = 'INSERT INTO PJ_Vocab.Quiz_History (Q_ID, Score, Quiz_Date) VALUES (%s, %s, %s)'
        val = (f'Q_{count}', score, q_time)

        cursor.execute(sql, val)
        connection.commit()
        print(f'\nQuiz has been performed at {q_time}.\n')

    except Exception as e:
        print(e)
        connection.rollback()


def welcome(cursor, connection, limit_choice):
    print('            +---------------------------------------------------------------------------------------------+')
    print('            |                                                                                             |')
    print('            |                                  Welcome to Vocabulary Land                                 |')
    print('            |                                                                                             |')
    print('            +---------------------------------------------------------------------------------------------+')

    print("\n\n")

    data = read_marked_data(cursor, 'bookmark')

    quiz_word = data[randint(0, len(data) - 1)]

    print(f"Do you know the meaning of this word : {quiz_word[0]}")

    choice = input("[Y] for Yes [N] for No : ")

    if choice.lower() == 'n':
        transfer_word(cursor, connection, 'bookmark', 'new', quiz_word[0], 'copy')
        remove_word(cursor, connection, 'known', quiz_word[0])

    elif choice.lower() == 'y':
        transfer_word(cursor, connection, 'bookmark', 'known', quiz_word[0], 'copy')
        remove_word(cursor, connection, 'new', quiz_word[0])

    print("\nHere are some random words which are new to you along with the word you are quizzed!\n")

    tmp_data = [quiz_word]

    if len(data) <= limit_choice:
        limit_choice = len(data)

    i = 1
    while i < limit_choice:
        tp = data[randint(0, len(data) - 1)]
        if tp not in tmp_data:
            tmp_data.append(tp)
            i += 1

    display(['Word', 'Meaning'], tmp_data)


def rotate(ans_list):
    r_number = randint(0, 10)

    # ans_list = [1, 2, 3, 4, 5, 6, 7]

    ans_list = (ans_list[len(ans_list) - r_number:len(ans_list)] + ans_list[0:len(ans_list) - r_number])

    return ans_list


def create_questions(data, quiz_words, noq):
    questions = {}
    answers = []
    temp_data = dict(data)
    for i in range(noq):
        temp_li = []
        correct_included = False
        correct_choice = temp_data[quiz_words[i]]
        answers.append(correct_choice)
        j = 0
        while j < 4:
            choice = data[randint(0, len(data) - 1)][1]
            if not correct_included:
                temp_li.append(correct_choice)
                correct_included = True
                j += 1

            elif choice not in temp_li and choice != correct_choice:
                temp_li.append(choice)
                j += 1

        temp_li = rotate(temp_li)

        questions[quiz_words[i]] = temp_li

    # for key, val in questions.items():
    #     print(f'{key} : {val}')
    # print(questions)

    return questions, answers


def create_quiz(connection, cursor, quiz_length=3):
    data = read_meaning(cursor)
    answered = {}
    total_marks = 0
    quiz_words = []
    if len(data) <= quiz_length:
        quiz_length = len(data)

    i = 1
    while i <= quiz_length:
        tp = data[randint(0, len(data) - 1)][0]
        if tp not in quiz_words:
            quiz_words.append(tp)
            i += 1

    questions, answers = create_questions(data, quiz_words, quiz_length)

    q_number = 0

    quiz_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key in questions.keys():
        print(f"\nChoose the correct meaning of the word : {key}")

        ans_choice = questions[key]
        for i in range(len(ans_choice)):
            print(f"[{i + 1}] --> {ans_choice[i]}")

        choice = int(input("Choose the correct number : ")) - 1

        if ans_choice[choice] == answers[q_number]:
            total_marks += 1
            answered[key] = [True, answers[q_number]]

        else:
            answered[key] = [False, answers[q_number]]

        q_number += 1

    log_quiz_info(connection, cursor, total_marks, quiz_time)

    temp = 0
    for key, val in answered.items():
        if val[0]:
            print(f"No.{temp + 1} [Correct!] {key} : {val[1]}")

        else:
            print(f"No.{temp + 1} [Incorrect!] {key} : {val[1]}")

        temp += 1

    print(f"\nTotal marks : {total_marks}")


def find_word(cursor, word):
    try:
        cursor.execute(f'SELECT W_Meaning FROM PJ_Vocab.meaning WHERE Word = "{word}"')
        result = cursor.fetchone()[0]
        print(type(result))

    except Exception as e:
        print(f"\nThe word '{word}' might not exist in the database!")
        print(e, "\n")


def total_known(cursor):
    cursor.execute('SELECT COUNT(*) FROM PJ_Vocab.known_word WHERE M_Code != "N/A";')
    count = cursor.fetchall()[0][0]
    print(f'You have {count} known words')
    read_marked_data(cursor, 'known', sort=True, _display_=True)


def total_new(cursor):
    cursor.execute('SELECT COUNT(*) FROM PJ_Vocab.new_word WHERE M_Code != "N/A";')
    count = cursor.fetchall()[0][0]
    print(f'You have {count} new words')
    read_marked_data(cursor, 'new', sort=True, _display_=True)


def main():
    try:
        connection = ct.connect(user='hla', password='miitCSE013!23', host='localhost', port=3306, database='PJ_Vocab')

        if connection.is_connected():
            cursor = connection.cursor()
            # create_quiz(connection, cursor, 3)
            welcome(cursor, connection, limit_choice=5)
            # insert_meaning(connection, cursor, 1)
            # read_meaning(cursor, 'Meaning', sort=True)
            # mark_word(connection, cursor, 'legit', 'bookmark')
            # read_marked_data(cursor, 'bookmark', sort=True, _display_=True)

            # need to work on commands and optimization

            commands = {'quiz': 'Want to take a quiz.', 'find_meaning': 'Find the meaning of a word.',
                        'total_known': 'Find out how many vocabs you know.',
                        'total_new': 'Find out how many new vocabs for you.',
                        'insert_new_word': 'Insert new meaning into the database.',
                        'show_bookmark': 'Show the bookmarked words',
                        'quiz_history': 'Show the history of all performed quizzes.',
                        'quit': 'Exit from the application.'}
            i = 1
            for key, val in commands.items():
                print(f'{i}. {key}{" " * (15 - len(key))} - {val}')
                i += 1

            while True:
                choice = int(input("What is your choice (number) : "))

                if choice == 1:
                    create_quiz(connection, cursor, 3)

                elif choice == 2:
                    word = input("Enter the word : ")
                    find_word(cursor, word=word)

                elif choice == 3:
                    total_known(cursor)

                elif choice == 4:
                    total_new(cursor)

                elif choice == 5:
                    print('Insert a new word.')
                    insert_word(connection, cursor, 1)

                elif choice == 6:
                    print('\nDisplaying bookmarked words.\n')
                    read_marked_data(cursor, 'bookmark', sort=True, _display_=True)

                elif choice == 7:
                    print('\nDisplaying quiz history.\n')
                    show_quiz_history(cursor)

                elif choice == 8:
                    print('Bye')
                    break

        connection.close()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
