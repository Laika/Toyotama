from collections.abc import Iterator
from logging import getLogger

from sage.all import Matrix, Vector

logger = getLogger(__name__)


def shortest_vector(A: Matrix) -> Iterator[Vector]:
    A = A.LLL()
    for row in A.rows():
        if row.is_zero():
            continue
        yield row


# https://cims.nyu.edu/~regev/teaching/lattices_fall_2004/ln/cvp.pdf
def babai_closest_plane(B: Matrix, t: Vector) -> Iterator[Vector]:
    n = B.nrows()
    B = B.LLL()

    for b_ in B.gram_schmidt():
        b = t
        for j in range(n - 1, -1, -1):
            c_j = (b * b_[j]) / (b_[j] * b_[j])
            b -= c_j * B[j]
        yield t - b


def closest_vectors_embedding(B: Matrix, t: Vector) -> Iterator[Vector]:
    raise NotImplementedError("closest_vectors_embedding is not implemented yet")


def closest_vectors(B: Matrix, t: Vector, algorithm: Literal["babai", "embedding"] = "babai") -> Iterator[Vector]:
    if algorithm == "babai":
        yield from babai_closest_plane(B, t)
    elif algorithm == "embedding":
        yield from closest_vectors_embedding(B, t)
