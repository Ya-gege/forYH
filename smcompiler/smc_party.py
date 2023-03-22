"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
import pickle
from typing import (
    Dict
)

from communication import Communication
from expression import (
    Expression,
    Secret, AbstractOperator, Addition, Subtraction, Scalar, Multiplication
)
from protocol import ProtocolSpec
from secret_sharing import Share, share_secret, reconstruct_secret


# You might want to import more classes if needed.


# Feel free to add as many imports as you want.


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
                completed_share.append(pickle.loads(self.comm.retrieve_public_message(id, self.SHARE_COMPLETED_PREFIX + id)))

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
            # 处理加法操作
            if isinstance(expr, Addition):
                return pre_expr_share + next_expr_share

            # 处理减法操作
            if isinstance(expr, Subtraction):
                return pre_expr_share - next_expr_share

            # 处理乘法操作
            if isinstance(expr, Multiplication):
                return pre_expr_share * next_expr_share
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

        # 获取当前参与者的secret和值
        secret = next(iter(self.value_dict.keys()))
        val = next(iter(self.value_dict.values()))
        # 加密算法问题暂定
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
