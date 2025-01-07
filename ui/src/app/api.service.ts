// Interface to UI API service
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { Injectable } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { Observable, Subject, Subscription } from 'rxjs';
import { encode, decode } from '@msgpack/msgpack';

class Call extends Subject<any> {
    call_id: number;
    api_name: string;

    constructor(call_id: number, api_name: string) {
        super();
        this.call_id = call_id;
        this.api_name = api_name;
    }
}

type ReplyMsg = {
    api_error: string;
    call_id: number;
    api_result: any;
};


@Injectable({
    providedIn: 'root'
})
export class APIService {
    private _socket$: WebSocketSubject<any>;
    private _pendingCalls: Map<number, any> = new Map<number,any>();
    private _destroyed: boolean = false;
    private _receiver: Subscription;
    private _call_id: number = 0;

    constructor() {
        console.log("constructor");
        this._socket$ = webSocket({
            url: '/api-v1',
            binaryType: 'arraybuffer',
            serializer: (v) => v,
            deserializer: (v) => v,
        });
        this._receiver = this._socket$.asObservable().subscribe({
            error: (err) => this._error(err),
            next: (msg) => this._reply(msg),
            complete: () => this._complete(),
        })
    }

    // Send a message to the server
    call(api_name: string, api_args: any) : Observable<any> {
        const c = new Call(++this._call_id, api_name);
        this._socket$.next(encode({
            call_id: c.call_id,
            api_name: api_name,
            api_args: api_args,
        }));
        this._pendingCalls.set(c.call_id, c);
        console.log("call", c.call_id, api_name, api_args);
        return c;
    }

    ngOnDestroy() {
        console.log("ngOnDestroy");
        this._receiver.unsubscribe();
        this._socket$.complete();
    }

    private _complete() {
        console.log('APIService unexpected websocket disconnect');
        for (let c of this._pendingCalls.values()) {
            c.complete();
        }
    }

    private _error(err: any) {
        console.log("error", err);
        console.log('APIService websocket error', err);
        console.log(this);
        console.log(this._pendingCalls);
        for (const c of this._pendingCalls.values()) {
            c.error(err);
            c.complete();
        }
    }

    private _reply(msg: MessageEvent) {
        const m = decode(msg.data) as ReplyMsg;
        if (! this._pendingCalls.has(m.call_id)) {
            console.log('call not found', m.call_id)
            return;
        }
        const c = this._pendingCalls.get(m.call_id);
        this._pendingCalls.delete(m.call_id);
        if (m.api_error) {
            console.log(m.api_error);
            c.error(m.api_error);
        }
        else {
            console.log(m.api_result);
            console.log("reply", c.call_id, m.api_result);
            c.next(m.api_result);
        }
        c.complete();
    }
}
