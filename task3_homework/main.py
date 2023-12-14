import asyncio

from metagpt.actions import Action
from metagpt.roles import Role


class PrintAction(Action):
    text: str

    def __init__(self, text: str):
        super().__init__("PrintAction", None, None)
        self.text = text

    async def run(self, *args, **kwargs):
        print(self.text)
        return self.text

    def __str__(self):
        return super().__str__() + f' {self.text}'


class Agent(Role):

    def __init__(self, name="", profile="", goal="", constraints="", desc="", is_human=False):
        super().__init__(name, profile, goal, constraints, desc, is_human)

    def init_actions(self, action_list):
        self._init_actions(action_list)
        self._rc.max_react_loop = len(action_list)

    @staticmethod
    def get_action_list(start: int, end: int):
        action_list = [PrintAction(f'Action {i}') for i in range(start, end)]
        return action_list

    async def _think(self) -> None:
        # 使得 Agent 顺序执行上面三个动作
        state = self._rc.state
        if state < len(self._states) - 1:
            self._set_state(state + 1)

    async def run(self, message=None):
        # 给三个动作：打印1 打印2 打印3
        self.init_actions(Agent.get_action_list(1, 4))
        message_ = await super().run(message)
        print(self._rc.memory.storage)
        # 上述三个动作执行完毕后，为 Agent 生成新的动作 打印4 打印5 打印6 并顺序执行
        self.init_actions(Agent.get_action_list(4, 7))
        message_ = await super().run(message)
        print(self._rc.memory.storage)
        return message_


async def main():
    agent = Agent()
    await agent.run("请按顺序执行")


if __name__ == '__main__':
    asyncio.run(main())
