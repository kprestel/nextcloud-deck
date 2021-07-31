import pytest
from requests.auth import HTTPBasicAuth

from deck.api import NextCloudDeckAPI
from deck.models import Board, Card, Stack


@pytest.fixture(scope="session")
def nc() -> NextCloudDeckAPI:
    return NextCloudDeckAPI(
        "https://localhost:443", HTTPBasicAuth("Admin", "admin"), ssl_verify=False
    )


@pytest.fixture(scope="session")
def board(nc) -> Board:
    board_ = nc.create_board("test board")
    yield board_
    nc.delete_board(board_.id)


@pytest.fixture()
def stack(nc, board: Board):
    s = nc.create_stack(board.id, "test stack")
    yield s
    nc.delete_stack(board_id=board.id, stack_id=s.id)


@pytest.fixture()
def stack2(nc, board: Board):
    s = nc.create_stack(board.id, "test stack 2")
    yield s
    nc.delete_stack(board_id=board.id, stack_id=s.id)


@pytest.fixture()
def card(nc, board, stack):
    c = nc.create_card(board_id=board.id, stack_id=stack.id, title="test card fixture")
    yield c
    nc.delete_card(board_id=board.id, stack_id=stack.id, card_id=c.id)


def test_sanity(nc: NextCloudDeckAPI):
    boards = nc.get_boards()
    assert boards is not None
    assert len(boards) > 0


def test_create_stack(nc: NextCloudDeckAPI, board):
    stack = nc.create_stack(board.id, "Test")
    assert stack.deleted_at <= 0
    board_after = nc.get_board(board_id=board.id)
    assert board != board_after
    stack = nc.delete_stack(board_id=board.id, stack_id=stack.id)
    assert stack.deleted_at > 0


def test_create_card(nc: NextCloudDeckAPI, board, stack):
    card = nc.create_card(board_id=board.id, stack_id=stack.id, title="test card")
    cards = nc.get_cards_from_stack(board_id=board.id, stack_id=stack.id)
    for c in cards:
        if card.id == c.id:
            break
    else:
        assert False

    updated_card = nc.update_card(
        board_id=board.id,
        stack_id=stack.id,
        card_id=card.id,
        title="New Title",
        description="desc",
        owner=card.owner,
    )

    assert updated_card.title != card.title
    assert updated_card.description != card.description
    assert updated_card.last_modified > card.last_modified
    assert updated_card.id == card.id

    updated_card_fetched = nc.get_card(
        board_id=board.id, stack_id=stack.id, card_id=updated_card.id
    )
    assert updated_card_fetched == updated_card

    nc.delete_card(board_id=board.id, stack_id=stack.id, card_id=card.id)


def test_create_label(board: Board, nc: NextCloudDeckAPI, stack: Stack, card: Card):
    label = nc.create_label(board_id=board.id, title="Test label")
    labels = nc.get_board_labels(board_id=board.id)
    for l in labels:
        if l.id == label.id:
            assert l == label
            break
    else:
        assert False

    nc.assign_label_to_card(
        label_id=label.id, card_id=card.id, board_id=board.id, stack_id=stack.id
    )

    card_with_label = nc.get_card(board_id=board.id, stack_id=stack.id, card_id=card.id)

    assert card_with_label.labels[0].id == label.id

    nc.remove_label_from_card(
        board_id=board.id, stack_id=stack.id, card_id=card.id, label_id=label.id
    )

    card_without_label = nc.get_card(
        board_id=board.id, stack_id=stack.id, card_id=card.id
    )

    assert len(card_without_label.labels) == 0

    nc.delete_label(board_id=board.id, label_id=label.id)


def test_get_cards_from_stack(board, stack, card, nc: NextCloudDeckAPI):
    cards = nc.get_cards_from_stack(board_id=board.id, stack_id=stack.id)
    assert len(cards) == 1
    assert cards[0] == card


def test_reorder_card(board, stack, stack2, card, nc: NextCloudDeckAPI):
    assert card.stack_id == stack.id
    nc.reorder_card(board.id, stack.id, card.id, card.order-1, stack2.id)
    cards1 = nc.get_cards_from_stack(board.id, stack.id)
    cards2 = nc.get_cards_from_stack(board.id, stack2.id)
    assert len(cards1) == 0
    assert len(cards2) == 1
    card_moved = nc.get_card(board.id, stack2.id, card.id)
    assert card.title == card_moved.title
    assert card.stack_id != card_moved.stack_id
    assert card_moved.stack_id == stack2.id
