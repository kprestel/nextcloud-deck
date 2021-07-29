import logging
import typing

import requests

from deck.models import Board, Card, Label, Stack, deserialize

logger = logging.getLogger(__name__)


IdType = typing.Union[int, str]


class NextCloudDeckAPI:
    """docstring for NextCloudDeck."""

    def __init__(
        self,
        url,
        auth,
        ssl_verify=True,
        deck_api_path="/index.php/apps/deck/api/v1.0/boards",
        raise_for_status=True,
    ):
        self.url = f"{url}{deck_api_path}"
        self.session: requests.Session = requests.Session()
        self.session.auth = auth
        self.session.headers.update(
            {"OCS-APIRequest": "true", "Content-Type": "application/json"}
        )
        self.session.verify = ssl_verify
        if raise_for_status:
            self.session.hooks = {
                "response": lambda r, *args, **kwargs: r.raise_for_status()
            }

    @deserialize(typing.List[Board])
    def get_boards(self):
        response = self.session.get(
            f"{self.url}",
        )
        return response.json()

    @deserialize(Board)
    def get_board(self, board_id) -> Board:
        response = self.session.get(
            f"{self.url}/{board_id}",
        )
        return response.json()

    @deserialize(typing.List[Stack])
    def get_stacks(self, board_id):
        response = self.session.get(
            f"{self.url}/{board_id}/stacks",
        )
        return response.json()

    @deserialize(typing.List[Card])
    def get_cards_from_stack(self, board_id, stack_id):
        response = self.session.get(
            f"{self.url}/{board_id}/stacks/{stack_id}",
        )
        if "cards" in response.json():
            return response.json()["cards"]
        return []

    @deserialize(Card)
    def get_card(self, board_id, stack_id, card_id):
        response = self.session.get(
            f"{self.url}/{board_id}/stacks/{stack_id}/cards/{card_id}",
        )
        return response.json()

    @deserialize(Label)
    def create_label(self, board_id, title, color="ff0000"):
        response = self.session.post(
            f"{self.url}/{board_id}/labels",
            json={"title": title, "color": color},
        )
        return response.json()

    @deserialize(Stack)
    def create_stack(self, board_id, title, order=999):
        response = self.session.post(
            f"{self.url}/{board_id}/stacks",
            json={"title": title, "order": order},
        )
        return response.json()

    @deserialize(Stack)
    def delete_stack(self, board_id, stack_id):
        response = self.session.delete(f"{self.url}/{board_id}/stacks/{stack_id}")
        return response.json()

    @deserialize(Card)
    def create_card(
        self,
        board_id,
        stack_id,
        title,
        ctype="plain",
        order=999,
        description=None,
        duedate=None,
    ):
        response = self.session.post(
            f"{self.url}/{board_id}/stacks/{stack_id}/cards",
            json={
                "title": title,
                "type": ctype,
                "order": order,
                "description": description,
                "duedate": duedate,
            },
        )
        return response.json()

    @deserialize(Card)
    def update_card(
        self,
        board_id,
        stack_id,
        card_id,
        title,
        owner,
        description="",
        order=999,
        duedate=None,
    ) -> Card:
        response = self.session.put(
            f"{self.url}/{board_id}/stacks/{stack_id}/cards/{card_id}",
            json={
                "owner": owner,
                "title": title,
                "type": "plain",
                "order": order,
                "description": description,
                "duedate": duedate,
            },
        )
        return response.json()

    def delete_card(self, board_id, stack_id, card_id) -> typing.Dict[str, typing.Any]:
        response = self.session.delete(
            f"{self.url}/{board_id}/stacks/{stack_id}/cards/{card_id}"
        )

        return response.json()

    def get_labels(self, board_id):
        boards = self.get_board(board_id)
        return boards.labels

    def remove_label_from_card(self, board_id, stack_id, card_id, label_id):
        logger.info(
            f"removing label: board_id: {board_id}, stack_id: {stack_id}, card_id: {card_id}, label_id: {label_id}"
        )
        response = self.session.put(
            f"{self.url}/{board_id}/stacks/{stack_id}/cards/{card_id}/removeLabel",
            json={"labelId": label_id},
        )
        return response.json()

    def delete_label(self, board_id, label_id):
        response = self.session.delete(f"{self.url}/{board_id}/labels/{label_id}")
        return response.json()

    def assign_label_to_card(
        self, board_id, stack_id, card_id, label_id
    ) -> typing.Dict[str, typing.Any]:
        response = self.session.put(
            f"{self.url}/{board_id}/stacks/{stack_id}/cards/{card_id}/assignLabel",
            json={"labelId": label_id},
        )
        return response.json()

    @deserialize(Board)
    def create_board(self, title, color="ff0000") -> Board:
        logger.info(f"Creating board with title: {title} and color: {color}")
        response = self.session.post(
            f"{self.url}", json={"title": title, "color": color}
        )
        return response.json()

    def delete_board(self, board_id):
        logger.info(f"Deleting board with ID: {board_id}")
        response = self.session.delete(f"{self.url}/{board_id}")
        logger.debug(response)
        return response.json()
