from mysql import connector as ct
from Helper_Functions import *


def welcome(cursor, connection, limit_choice):

    """
    When program start,

    In the background,a random word is chosen from bookmark_word,

    Ask the definition of that word as a quiz_word,

    it will ask you whether you know the meaning of that word or not.

    If you know that word, it will be mark as a known word otherwise as a new word.

    The program chooseses 4 more random words from bookmark words and display all 5 words along with their definition.

    """
      
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
                        'show_favourite': 'Show the favourite words',
                        'bookmark': 'Bookmark a word.',
                        'favourite': 'Mark a word as favourite',
                        'quiz_history': 'Show the history of all performed quizzes.'}

            i = 1
            for key, val in commands.items():
                print(f'{i}. {key}{" " * (15 - len(key))} - {val}')
                i += 1

            while True:
                choice = int(input("What is your choice (number), (0 to exit): "))

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
                    print('\nDisplaying favourite words.\n')
                    read_marked_data(cursor, 'favourite', sort=True, _display_=True)

                elif choice == 8:
                    word = input("Enter the word : ")
                    mark_word(connection, cursor, word, 'bookmark')

                elif choice == 9:
                    word = input("Enter the word : ")
                    mark_word(connection, cursor, word, 'favourite')

                elif choice == 10:
                    print('\nDisplaying quiz history.\n')
                    show_quiz_history(cursor)

                elif choice == 0:
                    print('Bye')
                    break

                input('Press Enter to continue...')
                i = 1
                for key, val in commands.items():
                    print(f'{i}. {key}{" " * (15 - len(key))} - {val}')
                    i += 1

        connection.close()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
