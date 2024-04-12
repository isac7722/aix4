import random
import time
import pyglet

# 필요한 경우 pyglet을 설치합니다.
# pip install pyglet


def wordLoad():
    """word.txt 파일로부터 단어를 로딩하여 리스트로 반환하는 함수"""
    with open("data/word.txt", "r") as file:
        words = [line.strip() for line in file.readlines()]
    return words


def gameRun(words):

    while True:

        """워드 게임 실행 함수"""
        correct_count = 0
        start_time = time.time()

        # Load the sound
        good_sound = pyglet.media.load("assets/good.wav", streaming=False)
        bad_sound = pyglet.media.load("assets/bad.wav", streaming=False)

        # 몇번의 기회를 원하는지
        try:
            chances = int(input("단어수를 입려하시오? "))
        except ValueError:
            print("정수를 입력하시오")

        for _ in range(chances):
            target_word = random.choice(words)
            display_word = ''.join(random.choice(
                [c.upper(), c]) for c in target_word)
            print(f"Your word: {display_word}")
            user_input = input("Type the word: ")

            if user_input.strip() == display_word:
                print("Correct!")
                good_sound.play()
                correct_count += 1
            else:
                print("Wrong!")
                bad_sound.play()

        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Correct answers: {correct_count}")

        pass_score = round(chances * 0.8)

        if correct_count >= pass_score:
            print("Passed!")
        else:
            print("Failed!")

        # 재도전 여부 확인
        retry = input("재도전 하시겠습니까? (y/n): ").strip().lower()

        if retry != 'y':
            break


def main():
    words = wordLoad()
    gameRun(words)


if __name__ == "__main__":
    main()
