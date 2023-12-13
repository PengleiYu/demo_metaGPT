from typing import Dict

from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message

from write_doc.WriteContent import WriteContent
from write_doc.WriteDirectory import WriteDirectory


class TutorialAssistant(Role):
    """Tutorial assistant, input one sentence to generate a tutorial document in markup format.

    Args:
        name: The name of the role.
        profile: The role profile description.
        goal: The goal of the role.
        constraints: Constraints or requirements for the role.
        language: The language in which the tutorial documents will be generated.
    """

    def __init__(
            self,
            name: str = "Stitch",
            profile: str = "Tutorial Assistant",
            goal: str = "Generate tutorial documents",
            constraints: str = "Strictly follow Markdown's syntax, with neat and standardized layout",
            language: str = "Chinese",
    ):
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteDirectory(language=language)])
        self.topic = ""
        self.main_title = ""
        self.total_content = ""
        self.language = language

    async def _think(self) -> None:
        """Determine the next action to be taken by the role."""
        if self._rc.todo is None:
            self._set_state(0)
            return

        if self._rc.state + 1 < len(self._states):
            self._set_state(self._rc.state + 1)
        else:
            self._rc.todo = None

    async def _act(self) -> Message:
        """Perform an action as determined by the role.

        Returns:
                A message containing the result of the action.
        """
        todo = self._rc.todo
        if type(todo) is WriteDirectory:
            msg = self._rc.memory.get(k=1)[0]
            self.topic = msg.content
            resp = await todo.run(topic=self.topic)
            logger.info(resp)
            return await self._handle_directory(resp)
        resp = await todo.run(topic=self.topic)
        logger.info(resp)
        if self.total_content != "":
            self.total_content += "\n\n\n"
        self.total_content += resp
        return Message(content=resp, role=self.profile)

    async def _handle_directory(self, titles: Dict) -> Message:
        """Handle the directories for the tutorial document.

        Args:
            titles: A dictionary containing the titles and directory structure,
                    such as {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}

        Returns:
            A message containing information about the directory.
        """
        # 当生成目录后记录目录标题（因为最后要输出完整文档）
        self.main_title = titles.get("title")
        directory = f"{self.main_title}\n"
        # self.total_content用来存储最好要输出的所有内容
        self.total_content += f"# {self.main_title}"
        actions = list()
        for first_dir in titles.get("directory"):
            # 根据目录结构来生成新的需要行动的action（目前只设计了两级目录）
            actions.append(WriteContent(language=self.language, directory=first_dir))
            key = list(first_dir.keys())[0]
            directory += f"- {key}\n"
            for second_dir in first_dir[key]:
                directory += f"  - {second_dir}\n"
        self._init_actions(actions)
        self._rc.todo = None
        return Message(content=directory)
