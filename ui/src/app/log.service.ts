// Logging
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class LogService {
    dbg(msg: any) {
        this.#console(new Error(), msg);
    }

    error(msg: any) {
        this.#console(new Error(), msg);
    }

    info(msg: any) {
        this.#console(new Error(), msg);
    }

    #caller(stack: string) : string {
        if (! stack) {
            return "";
        }
        const l = stack.split(/\r?\n/);
        if (l[0] == 'Error') {
            return l[2];
        }
        return l[1];
    }

    #console(error: Error, msg: any) {
        console.log(
            (new Date().toISOString()).substring(11, 19),
            msg,
            this.#caller(error.stack || ""),
        );
    }
}
