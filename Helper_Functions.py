from prettytable import PrettyTable, from_db_cursor
from random import randint
import datetime
# from prettytable.colortable import ColorTable, Themes


def display(column_names, data):

    """
    This function just displays the data in a pretty table.

    """

    table = PrettyTable(align='l')
    table.field_names = column_names
    table.add_rows(data)
    print(table)


def mark_word(connection, cursor, word, mark_as):

    """
    Mark the particular word as (bookmark / favorite / new / known ) word.

    """

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
        print(f'The word "{word}" might not exist in the database!')
        print(e)
        connection.rollback()


def show_quiz_history(cursor):

    """
    Display the information of all quizzes that you have been taken.

    """

    cursor.execute('SELECT Q_ID, Score, Quiz_Date AS "Quiz Time" FROM PJ_Vocab.Quiz_History ORDER BY Quiz_Date DESC')

    table = from_db_cursor(cursor)
    table.align = 'l'
    print(table)


def read_meaning(cursor, limit=None, sort=False, _display_=False):

    """
    Read all the meaning from the Database.

    -------------------
     Options available
    -------------------

    --> Limit can be applied to the number of rows while displaying the vocabularies.
    --> Can sort the vocabs Alphabetically by setting sort to "True".
    --> You can set _display_=True if you want to display the data. Otherwise, the data will only be returned in a list.

    """

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

    """
    Display vocabularies which are mark as (favorite / bookmark / known / new) words.

    -------------------
     Options available
    -------------------

    --> Limit can be applied to the number of rows while displaying the vocabularies.
    --> Can sort the vocabularies Alphabetically by setting sort to "True".
    --> You can set _display_=True if you want to display the data. Otherwise, the data will only be returned in a list.

    """

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

    """
    Clear the M_Code and replace with N/A from respective (favorite / bookmark / known / new) tables.
    
    """

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


def check_existence(cursor, m_code, table):

    """
    Check if the vocabulary exists or not in the destination database.
    
    """

    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE M_Code='{m_code}';")
    result = cursor.fetchone()

    return result[0]


def transfer_word(cursor, connection, from_tb, to_tb, word, action=None):

    """
    Transfer Vocabularies from one of (favorite / bookmark / known / new) to another table between branch table.
    
    """

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


def insert_word(connection, cursor, no_of_rows=1):

    """
    Insert a new word with its definition to the main database.
    
    """

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

    """
    Store the quiz information (Score, Time) to the database.
    
    """

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


def rotate(ans_list):

    """
    Rotate the position of the definition of quiz word : avoiding the correct answer in the same position.

    """

    r_number = randint(0, 10)

    # ans_list = [1, 2, 3, 4, 5, 6, 7]

    ans_list = (ans_list[len(ans_list) - r_number:len(ans_list)] + ans_list[0:len(ans_list) - r_number])

    return ans_list


def create_questions(data, quiz_words, noq):

    """
    The purpose of this function is to create multiple question with 4 choices.

    The number of questions can be controlled.

    """

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

    return questions, answers


def create_quiz(connection, cursor, quiz_length=3):

    """
    The purpose of this function is to create the quiz of length x(int).

    """
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

    """
    Find the desired word from the main database and display its definition.

    """

    try:
        cursor.execute(f'SELECT W_Meaning FROM PJ_Vocab.meaning WHERE Word = "{word}"')
        result = cursor.fetchone()[0]
        print(f"{word} : {result}")

    except Exception as e:
        print(f"\nThe word '{word}' might not exist in the database!")
        print(e, "\n")


def total_known(cursor):

    """
    Display the total number of known words.

    """

    cursor.execute('SELECT COUNT(*) FROM PJ_Vocab.known_word WHERE M_Code != "N/A";')
    count = cursor.fetchall()[0][0]
    print(f'You have {count} known words')
    read_marked_data(cursor, 'known', sort=True, _display_=True)


def total_new(cursor):

    """
    Display the total number of new words.

    """
    cursor.execute('SELECT COUNT(*) FROM PJ_Vocab.new_word WHERE M_Code != "N/A";')
    count = cursor.fetchall()[0][0]
    print(f'You have {count} new words')
    read_marked_data(cursor, 'new', sort=True, _display_=True)
