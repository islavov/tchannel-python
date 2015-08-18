# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import

import pytest
from tornado import gen

from tchannel import TChannel
from tchannel import Response
from tchannel.context import get_current_context


@pytest.mark.gen_test
def test_context():
    context = [None, None]
    server = TChannel(name='server')

    @server.raw.register
    @gen.coroutine
    def endpoint1(request):
        yield server.raw(
            service='server',
            endpoint='endpoint2',
            headers='req headers',
            body='req body',
            hostport=server.hostport,
        )
        context[0] = get_current_context()
        raise gen.Return(Response('resp body', 'resp headers'))

    @server.raw.register
    def endpoint2(request):
        context[1] = get_current_context()
        return Response('resp body', 'resp headers')

    server.listen()

    # Make a call:

    tchannel = TChannel(name='client')

    yield tchannel.raw(
        service='server',
        endpoint='endpoint1',
        headers='req headers',
        body='req body',
        hostport=server.hostport,
    )

    assert context[0].parent_tracing.name == 'endpoint1'
    assert context[1].parent_tracing.name == 'endpoint2'
