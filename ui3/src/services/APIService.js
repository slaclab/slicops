// Interface to UI API service
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { encode, decode } from '@msgpack/msgpack';
import LogService from './LogService';

// Constants
const AUTH_API_NAME = 'authenticate_connection';
const AUTH_API_VERSION = 658584001;

const MSG_KIND_BASE = 777500;
const MSG_KIND_CALL = 1 + MSG_KIND_BASE;
const MSG_KIND_REPLY = 2 + MSG_KIND_BASE;
const MSG_KIND_SUBSCRIBE = 3 + MSG_KIND_BASE;
const MSG_KIND_UNSUBSCRIBE = 4 + MSG_KIND_BASE;

class Call {
  constructor(apiService, isSubscription, call_id, api_name, api_args, resultHandler, apiErrorHandler) {
    this.apiErrorHandler = apiErrorHandler;
    this.apiService = apiService;
    this.api_args = api_args;
    this.api_name = api_name;
    this.call_id = call_id;
    this.isSubscription = isSubscription;
    this.resultHandler = resultHandler;
    this.destroyed = false;
  }

  // Stop a subscription
  unsubscribe() {
    if (this.destroyed) {
      // so unsubscribe() can be idempotent
      return;
    }
    if (!this.isSubscription) {
      throw new Error(`call to api_name=${this.api_name} is not a subscription`);
    }
    this.apiService.sendUnsubscribe(
      encode({
        call_id: this.call_id,
        msg_kind: MSG_KIND_UNSUBSCRIBE,
      }),
    );
    this.destroy();
  }

  destroy() {
    if (this.destroyed) {
      return;
    }
    this.destroyed = true;
    this.apiService.callDestroy(this.call_id);
  }

  handleError(api_error) {
    if (this.apiErrorHandler) {
      this.apiErrorHandler(api_error);
    }
    else {
      LogService.error(['call error', api_error, this]);
    }
    // implicit unsubscribe
    this.destroy();
  }

  handleResult(api_result) {
    this.resultHandler(api_result);
    if (api_result == null || !this.isSubscription) {
      this.destroy();
    }
  }

  msg() {
    const a = this.api_args;
    this.api_args = null;
    return encode({
      api_args: a,
      api_name: this.api_name,
      call_id: this.call_id,
      msg_kind: this.isSubscription ? MSG_KIND_SUBSCRIBE : MSG_KIND_CALL,
    });
  }
}

class APIService {
  constructor() {
    this._authOK = false;
    this._call_id = 0;
    this._client_id = null;
    this._pendingCalls = new Map();
    this._socket = null;
    this._socketRetryBackoff = 0;
    this._unsentMsgs = [];

    LogService.info('create websocket');
    this._socketOpen();
  }

  // Single send and a reply
  call(api_name, api_args, resultHandler, apiErrorHandler) {
    return this._sendCall(new Call(this, false, ++this._call_id, api_name, api_args, resultHandler, apiErrorHandler));
  }

  // not a public interface
  callDestroy(call_id) {
    this._pendingCalls.delete(call_id);
    // unsentMsgs could be deleted, but unlikely
  }

  destroy() {
    LogService.info('destroy websocket');
    if (this._socket) {
      this._socket.close();
      this._socket = null;
    }
    this._clearCalls('destroy');
  }

  // not a public interface
  sendUnsubscribe(msg) {
    this._unsentMsgs.push(msg);
    this._send();
  }

  // Single send and a reply
  subscribe(api_name, api_args, resultHandler, apiErrorHandler) {
    return this._sendCall(new Call(this, true, ++this._call_id, api_name, api_args, resultHandler, apiErrorHandler));
  }

  _authError(error) {
    // If there is a protocol error, this will retry forever. That would be a major problem
    // which is not fixable or really detectable. Likely case is the socket closed before auth
    // completed.
    if (this._socket) {
      this._socket.close();
    }
    this._socketOnError(error);
  }

  _authResult(api_result) {
    this._authOK = true;
    this._socketRetryBackoff = 0;
    this._send();
  }

  _clearCalls(error) {
    const a = [...this._pendingCalls.values()];
    this._pendingCalls = new Map();
    this._unsentMsgs = [];
    for (const c of a) {
      c.destroy();
    }
  }

  _findCall(call_id) {
    const rv = this._pendingCalls.get(call_id);
    if (!rv) {
      return null;
    }
    if (rv.destroyed) {
      // TODO(robnagler) raise error? This should not happen.
      this._pendingCalls.delete(call_id);
      return null;
    }
    return rv;
  }

  _send() {
    if (!this._socket || this._unsentMsgs.length <= 0 || !this._authOK) {
      return;
    }
    let m = null;
    while (m = this._unsentMsgs.shift()) {
      this._sendOne(m);
    }
  }

  _sendCall(call) {
    this._pendingCalls.set(call.call_id, call);
    this._unsentMsgs.push(call.msg());
    this._send();
    return call;
  }

  _sendOne(msg) {
    // the latter test is to pacify typescript
    if (!this._socket) {
      return;
    }
    this._socket.send(msg);
  }

  _socketOnError(event) {
    // close: event.code : short, event.reason : str, wasClean : boolean
    // error: app specific
    this._socket = null;
    if (this._socketRetryBackoff <= 0) {
      this._socketRetryBackoff = 1;
      LogService.error(['WebSocket failed', event]);
      this._clearCalls(event.wasClean ? 'socket closed' : 'socket error');
    }
    if (this._socketRetryBackoff < 60) {
      this._socketRetryBackoff *= 2;
    }
    setTimeout(this._socketOpen.bind(this), this._socketRetryBackoff * 1000);
  }

  _socketOnMessage(msg) {
    const m = decode(msg);
    const c = this._findCall(m.call_id);
    if (!c) {
      // happens on unsubscribe
      return;
    }
    if (MSG_KIND_REPLY == m.msg_kind) {
      if (m.api_error) {
        c.handleError(m.api_error);
      }
      else {
        c.handleResult(m.api_result);
      }
    }
    else if (MSG_KIND_UNSUBSCRIBE == m.msg_kind) {
      if (c.isSubscription) {
        c.handleResult(null);
      }
      else {
        c.handleError('unsubscribe of non-subscription');
      }
    }
    else {
      c.handleError(`protocol error: invalid msg_kind=${m.msg_kind}`)
    }
  }

  _socketOnOpen(event) {
    this.call(
      AUTH_API_NAME,
      {
        // No token, because any value would have to come from the server,
        // and therefore would be discoverable.
        token: null,
        version: AUTH_API_VERSION,
      },
      this._authResult.bind(this),
      this._authError.bind(this),
    )
    const m = this._unsentMsgs.pop();
    if (m) this._sendOne(m);
  }

  _socketOpen() {
    try {
      // Construct WebSocket URL relative to current page
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api-v1`;

      console.log('Connecting to WebSocket at:', wsUrl);
      const s = new WebSocket(wsUrl);

      s.onclose = this._socketOnError.bind(this);
      s.onerror = this._socketOnError.bind(this);
      s.onmessage = (event) => {
        event.data.arrayBuffer().then(
          this._socketOnMessage.bind(this),
          (error) => {
            LogService.error(['arrayBuffer decode error', error, event.data]);
            this._socketOnError(event);
          },
        );
      };
      s.onopen = this._socketOnOpen.bind(this);
      this._authOK = false;
      this._socket = s;
    } catch (err) {
      this._socketOnError(err);
    }
  }
}

export default new APIService();
