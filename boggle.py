import random
import json
import time
import os


def save_score(scr, usr, tms):
    """
    save score of user into file for future references
    :param scr: score
    :param usr: username
    :param tms: timestamp from starting the game
    :return:
    """
    with open('scores/boggle_score.json', 'r', encoding='utf8') as rf:
        jsn = json.load(rf)
    if usr not in jsn:
        jsn[usr] = {'all_games': {}, 'best': 0}
    jsn[usr]['all_games'][tms] = scr
    if scr > jsn[usr]['best']:
        jsn[usr]['best'] = scr
    with open('scores/boggle_score.json', 'w', encoding='utf8') as wf:
        wf.write(json.dumps(jsn))


def test_alternative_roads(brd, pos, word):
    """
    test alternative paths by removing last letter and check if it can try another letter before
    :param brd: nested list of letters
    :param pos: dead-end position
    :return: position of found word
    """
    # POS [C A D]

    tried_positions = [pos[:]]
    orig_pos = pos
    for i in range(1, 1000):
        test_pos = orig_pos[:-i]
        if not test_pos:
            return []
        # print('test_pos', test_pos)
        for ltr in word[len(orig_pos[:-i]):]:
            ltr_found = 0
            for next_pos in next_position(orig_pos[:-i][-1], len(brd)):
                next_ltr = brd[next_pos[0]][next_pos[1]]
                if next_ltr == ltr:
                    if not ltr_found:
                        test_pos.append(next_pos)
                        if test_pos in tried_positions:
                            test_pos.pop()
                            continue
                        ltr_found = 1
                    # break
            if not ltr_found:  # did not find necessary letter
                break
        if len(test_pos) == len(word):
            # print('FOUND ALTERNATIVE', test_pos)
            return test_pos


def score_word(word):
    scoring_d = {'A': 2, 'E': 2, 'I': 2, 'O': 2, 'U': 2}
    scr = 1
    for ltr in word:
        if ltr.upper() not in scoring_d:
            scr *= 3
        else:
            scr *= scoring_d[ltr.upper()]
    return scr + 20


def next_position(start_p, n):
    """
    check where the player could have moved on board
    :param start_p: position on board now
    :param n: length of board
    :return: possible positions (row, index)
    """
    columns = [start_p[1]]
    rows = [start_p[0]]
    if start_p[0] < 1:
        rows.append(start_p[0] + 1)
    elif start_p[0] >= n-1:
        rows.append(start_p[0] - 1)
    else:
        rows.append(start_p[0] + 1)
        rows.append(start_p[0] - 1)

    if start_p[1] < 1:
        columns.append(start_p[1] + 1)
    elif start_p[1] >= n-1:
        columns.append(start_p[1] - 1)
    else:
        columns.append(start_p[1] + 1)
        columns.append(start_p[1] - 1)

    positions = []
    for rw in rows:
        for clm in columns:
            if (rw, clm) != start_p:
                positions.append((rw, clm))
    # print('next positions', positions)
    return positions


def find_word(brd, word):
    global used_words
    """
    check the board for the inputted word (for simplicity considering only 1 match)
    use of index() function is not advised as it would not consider multiple letters in one row
    :param brd: nested list of letters
    :param word: input from player
    :return:
    """
    n = len(brd)
    positions = []  # all start positions of first letter
    for rw_indx in range(len(brd)):
        for clm_indx in range(len(brd[rw_indx])):
            if brd[rw_indx][clm_indx] == word[0]:
                positions.append([(rw_indx, clm_indx)])

    word_found = 0
    already_used = 0
    for ps in positions:
        for ltr in word[1:]:
            start_p = ps[-1]
            ltr_found = 0
            for next_pos in next_position(start_p, n):
                next_ltr = brd[next_pos[0]][next_pos[1]]
                if next_ltr == ltr:
                    if not ltr_found:
                        ps.append(next_pos)
                        ltr_found = 1
            if not ltr_found:  # did not find necessary letter
                break
        if len(ps) != len(word):
            ps = test_alternative_roads(brd, ps, word)

        if ps in used_words:
            already_used = 1
        if len(ps) == len(word) and ps not in used_words:
            # print("WORD FOUND!!!", ps)
            used_words.append(ps)
            word_found = 1
            break

    return word_found, already_used


def import_dictionary(from_file=True):
    print('\nGenerating dictionary...')
    if not from_file:
        import nltk

        try:
            all_words = set(i.lower() for i in nltk.corpus.brown.words())
        except:  # if dictionary was not yet downloaded
            nltk.download('brown')
            all_words = set(i.lower() for i in nltk.corpus.brown.words())
    else:  # dictionary from file for speed
        try:
            with open('Collins Scrabble Words (2019).txt', 'r', encoding='utf8') as rf:
                all_words = set(i for i in rf.read().split('\n'))
        except FileNotFoundError:
            print('PLEASE DOWNLOAD A DICTIONARY FROM MY GITHUB REPOSITORY')
            exit()
    print(f'\nDictionary containing {len(all_words)} words generated !\n')
    return all_words


def create_board(num):
    """
    creates a board of num*num size containing letters
    :param num: number of rows/columns
    :return: nested list of letters
    """
    return [[chr(random.randint(65,90)) for a in range(num)] for b in range(num)]


def print_out_board(brd):
    """
    pretty prints a board
    :param brd: nested list of letters
    :return:
    """
    # str_b = '\n'*100
    str_b = '\n'
    for lst in brd:
        str_b += f"{'  |  '.join(lst)}\n\n"
    str_b = str_b[:-1]
    print(str_b)


def main():
    global used_words
    """
    Function creating the boggle game
    :return:1
    """
    used_words = []
    tms = round(time.time())
    try:
        with open('scores/boggle_score.json', 'r', encoding='utf8') as rf:
            scores = json.load(rf)
    except FileNotFoundError:
        os.makedirs('scores')
        with open('scores/boggle_score.json', 'w') as wf:
            wf.write(json.dumps('{}'))

    usr = input('PLEASE SELECT YOUR USERNAME: ')
    if usr not in scores:
        print(f'\nWELCOME {usr.upper()} ! I HOPE YOU ENJOY THE GAME !')
        time.sleep(1)
    else:
        print(f'\nWELCOME BACK {usr.upper()} !')

    all_words = import_dictionary()
    done, num = 0, 0
    while not done:
        try:
            num = input('INPUT A NUMBER [4-8] ')
            if num.lower().strip() == 'exit':
                done = 'exit'
                break
            num = int(num)
            if num not in range(4, 9):
                print('NUMBER MUST BE FROM 4 TO 8')
                continue
            done = 1
        except:
            print('PLEASE INPUT A NUMBER FROM FROM 4 TO 8 (type "exit" to exit the game)')
    if done == 'exit':
        exit()

    brd = create_board(num)

    # test board - came (bug hunting)
    # brd = [["N",  "P",  "A",  "M",  "O",  "G",  "S",  "Z"],  ["N",  "Y",  "C",  "E",  "Y",  "Y",  "B",  "Q"],  ["U",  "U",  "L",  "A",  "D",  "G",  "V",  "U"],  ["K",  "B",  "N",  "S",  "V",  "X",  "O",  "J"],  ["L",  "U",  "N",  "L",  "N",  "G",  "N",  "O"],  ["E",  "I",  "B",  "N",  "Y",  "N",  "W",  "N"],  ["G",  "L",  "O",  "G",  "T",  "S",  "M",  "W"],  ["Q",  "Z",  "X",  "U",  "T",  "D",  "K",  "L"]]

    finished = 0
    err_counter = 0
    ttl_scr = 0
    while not finished:
        try:
            print_out_board(brd)
            word = input('INPUT A WORD ').upper().strip()
            print('\n'*100)
            if word.lower() == 'help me':
                print('\nType "score" to display your best score\nType "exit game" to exit the game\n')
                continue
            elif word.lower() == 'exit game':
                exit()

            if len(word) < 3:
                print('YOUR WORD IS TOO SHORT ! USE AT LEAST 3 LETTERS')
                continue
            elif word not in all_words:
                err_counter += 1
                print(f'{" "*round(num*2-4)}YOUR SCORE IS {ttl_scr}')
                print(f'INVALID WORD - {word}', err_counter)
                if err_counter >= 3: print('\nHint (type "help me")')
                continue

            word_found, already_used = find_word(brd, word)
            if word_found:
                err_counter = 0
                scr = score_word(word)
                ttl_scr += scr
                print(f'{" "*round(num*2-4)}YOUR SCORE IS {ttl_scr}')
                print(f'{word}, A GOOD WORD +{scr} Pts ! CAN YOU FIND ONE MORE ?')
                save_score(ttl_scr, usr, tms)
            else:
                err_counter += 1
                print(f'{" "*round(num*2-4)}YOUR SCORE IS {ttl_scr}')
                if already_used:
                    print(f'YOU ALREADY USED {word} ! TRY AGAIN')
                else:
                    print(f'{word}, IS NOT ON THE BOARD ! TRY AGAIN')
                if err_counter >= 3:
                    # print('\nHint (type "exit" to exit the game)'.lower())
                    print('\nHint (type "help me")')
        except:
            print('THANK YOU FOR PLAYING THE GAME')
            exit()


if __name__ == '__main__':
    main()
