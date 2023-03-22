"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional, Tuple

ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)





class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
    ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        return Addition(self, other)

    def __sub__(self, other):
        return Subtraction(self, other)

    def __mul__(self, other):
        return Multiplication(self, other)

    def __hash__(self):
        return hash(self.id)

    # Feel free to add as many methods as you like.


class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __hash__(self):
        return

    # Feel free to add as many methods as you like.


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
            self,
            id: Optional[bytes] = None,
            value: Optional[int] = None
    ):
        super().__init__(id)
        self.value = value

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )

    # Feel free to add as many methods as you like.


# Feel free to add as many classes as you like.

class AbstractOperator(Expression):
    """
    抽象操作类
    """

    def __init__(self,
                 pre_expr: Expression,
                 next_expr: Expression,
                 id: Optional[bytes] = None):
        super().__init__(id)
        self.pre_expr = pre_expr
        self.next_expr = next_expr

    def separate(self) -> Tuple[Expression, Expression]:
        """
        分离操作符左右表达式
        2 * 3 + 8  ->  2 * 3, 8
        """
        return self.pre_expr, self.next_expr

    def scalar_format(self):
        """
        将表达式expr操作符前后标量情况转换为具体数字
        a + b -> a == Scalar: 1  a != Scalar: 0
        (0, 0) = (!Scalar, !Scalar)
        (0, 1) = (!Scalar, Scalar)
        (1, 0) = (Scalar, !Scalar)
        (1, 1) = (Scalar. Scalar)

        boolean(a) + boolean(b) >> 1
        (0, 0) = 0
        (0, 1) = 2
        (1, 0) = 1
        (1, 1) = 3
        """
        return int(isinstance(self.pre_expr, Scalar)) + int(isinstance(self.next_expr, Scalar) << 1)


class Addition(AbstractOperator):
    """
    加法操作
    """
    # def __repr__(self) -> str:
    #     return f"({repr(self.pre_expr)} + {self.next_expr})"


class Subtraction(AbstractOperator):
    """
    减法操作
    """


class Multiplication(AbstractOperator):
    """
    乘法操作
    """
