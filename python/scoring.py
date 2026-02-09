import fil_rouge_py

n = 10
scorer = fil_rouge_py.Scorer(10)


def score_solution(solution: list[int]) -> float:

    return scorer.score(solution)


if __name__ == "__main__":
    print(score_solution([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    print(score_solution([0, 1, 2, 3, 7, 5, 6, 4, 8, 9]))
