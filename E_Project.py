from mysql import connector as ct
from random import randint
from prettytable import PrettyTable  # , from_db_cursor
# from prettytable.colortable import ColorTable, Themes


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


def read_meaning(cursor, table, limit=None, sort=False):
    table = table.lower()
    cursor.execute(f'SHOW COLUMNS FROM PJ_Vocab.{table};')
    col_names = cursor.fetchall()
    col_names = [cols[0] for cols in col_names][1:]

    if sort:
        if limit is None:
            cursor.execute(f'SELECT Word, W_Meaning FROM PJ_Vocab.{table} ORDER BY Word ASC;')
        else:
            cursor.execute(f'SELECT Word, W_Meaning FROM PJ_Vocab.{table} ORDER BY Word ASC LIMIT {limit};')

    else:
        if limit is None:
            cursor.execute(f'SELECT Word, W_Meaning FROM {table};')

        else:
            cursor.execute(f'SELECT Word, W_Meaning FROM {table} LIMIT {limit};')

    data = cursor.fetchall()

    # table = from_db_cursor(cursor)
    # table.align = 'l'
    # print(table)

    display(col_names, data)


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

        print(f"'{word}' is removed from the {table} table!")

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

                    print(f"[+] 1 row is removed from {from_tb} table!")

                cursor.execute(f"SELECT COUNT(*) FROM {to_tb};")

                row_count = cursor.fetchone()[0] + 1

                sql = f'INSERT INTO PJ_Vocab.{to_tb} ({primary_columns[to_tb]}, M_Code) VALUE (%s, %s)'
                val = (f'{primary_index[to_tb]}{row_count}', m_code)

                cursor.execute(sql, val)

                connection.commit()

                print(f"[+] 1 row is inserted into {to_tb} table!")

            else:
                print(f"[-] The data already exists in the {to_tb} table!")

        else:
            print(f'[-] Data is not found in {from_tb} table')

    except Exception as e:
        connection.rollback()
        print(e)


def check_existence(cursor, m_code, table):
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE M_Code='{m_code}';")
    result = cursor.fetchone()

    return result[0]


def insert_meaning(connection, cursor, no_of_rows=1):
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


def welcome(cursor, connection, limit_choice):
    print('            +---------------------------------------------------------------------------------------------+')
    print('            |                                                                                             |')
    print('            |                                    Welcome to Vocabulary Land                               |')
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


def main():
    try:
        connection = ct.connect(user='hla', password='miitCSE013!23', host='localhost', port=3306, database='PJ_Vocab')

        if connection.is_connected():
            cursor = connection.cursor()
            welcome(cursor, connection, limit_choice=5)
            # insert_meaning(connection, cursor, 1)
            # read_meaning(cursor, 'Meaning', sort=True)
            # mark_word(connection, cursor, 'legit', 'bookmark')
            # read_marked_data(cursor, 'bookmark', sort=True, _display_=True)

            # need to work on commands and optimization

        connection.close()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
