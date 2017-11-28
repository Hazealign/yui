import pytest

from yui.type import PublicChannel

from ..util import FakeBot


@pytest.mark.asyncio
async def test_slack_api_channels_info():
    channel_id = 'C1234'
    channel = PublicChannel(id='C4567')

    bot = FakeBot()

    await bot.api.channels.info(channel_id)
    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {
        'channel': channel_id,
        'include_locale': 'false',
    }

    await bot.api.channels.info(channel)
    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {
        'channel': channel.id,
        'include_locale': 'false',
    }


@pytest.mark.asyncio
async def test_slack_api_channels_list():
    cursor = '1234asdf'
    exclude_archived = False
    exclude_members = False
    limit = 12

    bot = FakeBot()

    await bot.api.channels.list(
        cursor,
        exclude_archived,
        exclude_members,
        limit
    )
    call = bot.call_queue.pop()
    assert call.method == 'channels.list'
    assert call.data == {
        'cursor': cursor,
        'exclude_archived': 'false',
        'exclude_members': 'false',
        'limit': '12',
    }
