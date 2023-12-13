from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message

from SimpleRunCode import SimpleRunCode
from SimpleWriteCode import SimpleWriteCode


class RunnableCoder(Role):
    def __init__(
            self,
            name: str = "Alice",
            profile: str = "RunnableCoder",
            **kwargs,
    ):
        super().__init__(name, profile, **kwargs)
        self._init_actions([SimpleWriteCode, SimpleRunCode])
        self._set_react_mode(react_mode="by_order")

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备 {self._rc.todo}")
        # 通过在底层按顺序选择动作
        # todo 首先是 SimpleWriteCode() 然后是 SimpleRunCode()
        todo = self._rc.todo

        msg = self.get_memories(k=1)[0]  # 得到最相似的 k 条消息
        result = await todo.run(msg.content)

        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self._rc.memory.add(msg)
        return msg
