"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
import pickle
from typing import (
    Dict
)
import sys

from communication import Communication
from expression import (
    Expression,
    Secret, AbstractOperator, Addition, Subtraction, Scalar, Multiplication
)
from protocol import ProtocolSpec
from secret_sharing import Share, share_secret, reconstruct_secret

# You might want to import more classes if needed.


# Feel free to add as many imports as you want.
sys.setrecursionlimit(100000)


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    # 参与方发送自己share请求路径前缀
    SHARE_PUBLISH_PREFIX = "send_share_from_"
    # 参与方发送自己解析expr结果的请求路径前缀
    SHARE_COMPLETED_PREFIX = "complete_share_from_"
    # 参与方发送直接Beaver triplet protocol结果请求路径前缀
    SHARE_TRIPLET_A_PREFIX = "send_triplet_a_from_"
    SHARE_TRIPLET_B_PREFIX = "send_triplet_b_from_"

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
    ):
        self.comm = Communication(server_host, server_port, client_id)
        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict
        # k: secret v: share  expr中每个secret对应的共享对象share
        self.share_dict = dict()

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        # 1. 创建自己的Secret，并且将自己的Secret发送给其他参与方
        self.create_and_send_share()

        # 2. 阻塞等待所有参与方完成第一步操作
        for id in self.protocol_spec.participant_ids:
            if id != self.client_id:
                print("{} retrieve public msg from {}".format(self.client_id, id))
                self.comm.retrieve_public_message(id, self.SHARE_PUBLISH_PREFIX + id)

        # 3. 所有参与方完成share共享后，开始解析expr，完成自己的计算任务
        curr_share = self.process_expression(self.protocol_spec.expr)

        # 4. 计算任务完成后向其他参与方发布自己的计算结果
        for id in self.protocol_spec.participant_ids:
            if id != self.client_id:
                self.comm.publish_message(self.SHARE_COMPLETED_PREFIX + self.client_id, pickle.dumps(curr_share))
        completed_share = [curr_share]

        # 5. 获取其他参与方的计算结果
        for id in self.protocol_spec.participant_ids:
            if id != self.client_id:
                completed_share.append(
                    pickle.loads(self.comm.retrieve_public_message(id, self.SHARE_COMPLETED_PREFIX + id)))

        return reconstruct_secret(completed_share)

    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(self, expr: Expression) -> Share:

        # expr有secret未加密成share
        # 自己的直接获取share，不是自己的发请求获取
        if isinstance(expr, Secret):
            return self.get_or_retrieve_share(expr)

        # 遇到标量Scalar直接返回share
        if isinstance(expr, Scalar):
            return Share(expr.value)

        # 分离操作符
        if isinstance(expr, AbstractOperator):
            pre_expr, next_expr = expr.separate()
            pre_expr_share = self.process_expression(pre_expr)
            next_expr_share = self.process_expression(next_expr)
            scalar_format = expr.scalar_format()
            # 检查前后表达式标量情况
            # 1. 对与加减法操作，存在标量时，只需第一个参与方执行加减法标量即可 see: pdf-1.5
            # 2. 乘法操作存在标量时(secret * scalar or scalar * scalar)，直接返回相乘结果。无标量情况下(secret * secret)，使用Beaver协议计算 see: pdf-1.6
            if isinstance(expr, Addition) or isinstance(expr, Subtraction):
                # 两边都不是标量 或 当前参与方是队长，处理加减法的标量操作
                if scalar_format == 0 or self.is_captain():
                    # 处理加法操作
                    if isinstance(expr, Addition):
                        return pre_expr_share + next_expr_share
                    # 处理减法操作
                    if isinstance(expr, Subtraction):
                        return pre_expr_share - next_expr_share
                # 如果expr操作符前是标量, 只需处理并返回操作符后的表达式
                if scalar_format == 1:
                    return next_expr_share
                # 如果expr操作符后是标量, 只需处理并返回操作符前的表达式
                if scalar_format == 2:
                    return pre_expr_share
                # 如果操作符前后都是标量，无需处理计算结果，因为参与方队长已经处理掉了
                if scalar_format == 3:
                    return Share(0)
            # 处理乘法操作
            if isinstance(expr, Multiplication):
                # 乘法存在标量直接处理
                if scalar_format > 0:
                    return pre_expr_share * next_expr_share

                # Multiplication using the Beaver triplet protocol -- pdf-1.6
                # secret * secret
                a_share, b_share, c_share = self.comm.retrieve_beaver_triplet_shares(str(expr.id))
                # pre_expr_share = x
                pre_expr_share_a = pre_expr_share - a_share
                # next_expr_share = y
                next_expr_share_b = next_expr_share - b_share
                # 向其他参与方共享
                self.comm.publish_message(self.SHARE_TRIPLET_A_PREFIX + str(expr.id), pickle.dumps(pre_expr_share_a))
                self.comm.publish_message(self.SHARE_TRIPLET_B_PREFIX + str(expr.id), pickle.dumps(next_expr_share_b))

                # 检索其他参与者共享的三元组
                pre_expr_msg_list = [pre_expr_share_a]
                next_expr_msg_list = [next_expr_share_b]
                for id in self.protocol_spec.participant_ids:
                    if id != self.client_id:
                        pre_expr_msg_list.append(
                            pickle.loads(
                                self.comm.retrieve_public_message(id, self.SHARE_TRIPLET_A_PREFIX + str(expr.id))
                            )
                        )

                        next_expr_msg_list.append(
                            pickle.loads(
                                self.comm.retrieve_public_message(id, self.SHARE_TRIPLET_B_PREFIX + str(expr.id))
                            )
                        )
                # x - a
                x_a = sum(pre_expr_msg_list, start=Share(0))
                # y - b
                y_b = sum(next_expr_msg_list, start=Share(0))
                z = c_share + pre_expr_share * y_b + next_expr_share * x_a
                if self.is_captain():
                    z = z - x_a * y_b
                return z

        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
        pass

    # Feel free to add as many methods as you want.
    def get_or_retrieve_share(self, secret: Secret):
        """
        将原本由Secret表示的expr转换为Share表示的expr
            * 如果Secret属于参与方自己，直接从share_dict中获取
            * 如果Secret属于其他参与方，发请求获取
        """
        # 本地直接获取
        if secret in self.share_dict:
            return self.share_dict[secret]

        # 本地没有向服务器获取
        # 处理expr之前，每个参与者都共享了自己的share，所以这里肯定能拿到
        serialized_share = self.comm.retrieve_private_message(str(secret.id))
        share = pickle.loads(serialized_share)
        # 本地存一份
        self.share_dict[secret] = share
        return share

    def create_and_send_share(self):

        # # 获取当前参与者的secret和值  不适配test_8
        # secret = next(iter(self.value_dict.keys()))
        # val = next(iter(self.value_dict.values()))
        for secret in self.value_dict.keys():
            val = self.value_dict[secret]
            # 加密
            share_list = share_secret(val, len(self.protocol_spec.participant_ids))
            # 向其他参与者共享share
            for idx, id in enumerate(self.protocol_spec.participant_ids):
                if id == self.client_id:
                    self.share_dict[secret] = share_list[idx]
                else:
                    serialized_share = pickle.dumps(share_list[idx])
                    self.comm.send_private_message(id, str(secret.id), serialized_share)

        # 通知所有参与方自己完成加密并发送了share
        self.comm.publish_message(self.SHARE_PUBLISH_PREFIX + self.client_id, "~")

    def is_captain(self):
        # 指定参与方中第一个参与方为队长，负责加减运算中的标量处理
        return self.protocol_spec.participant_ids[0] == self.client_id
